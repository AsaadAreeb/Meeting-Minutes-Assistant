import gradio as gr
import datetime
import os
from google.cloud import storage, speech
from google.oauth2 import service_account
import subprocess
import tempfile
import google.generativeai as genai

# Path to the service account JSON file
SERVICE_ACCOUNT_FILE = "sa_minutes_ai.json"  # Update the name as needed

# Initialize Google Cloud clients
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
storage_client = storage.Client(credentials=credentials)
speech_client = speech.SpeechClient(credentials=credentials)
bucket_name = "meeting-ai-storage"  # Replace with your bucket name
bucket = storage_client.bucket(bucket_name)

# Replace with your actual Gemini API key
os.environ["GEMINI_API_KEY"] = "AIzaSyAjmcfNMGCSI19icee7X_1-2gMrZMmEq8M"

# Global context for transcript
global_transcript = ""

def save_audio_to_gcs(audio):
    """
    Saves an audio file to Google Cloud Storage in a structured folder hierarchy.
    The hierarchy is: <current_date>/<folder_number>/audio.wav
    """
    try:
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        date_folder = f"{current_date}/"
        blobs = list(storage_client.list_blobs(bucket_name, prefix=date_folder))
        folder_numbers = [
            int(blob.name.split("/")[1])
            for blob in blobs
            if len(blob.name.split("/")) > 1 and blob.name.split("/")[1].isdigit()
        ]
        new_folder_number = max(folder_numbers, default=0) + 1
        audio_folder = f"{date_folder}{new_folder_number}/"
        audio_path = f"{audio_folder}audio.wav"

        blob = bucket.blob(audio_path)
        blob.upload_from_filename(audio)

        # Return the GCS URI (gs://<bucket_name>/<path_to_audio>)
        gcs_uri = f"gs://{bucket_name}/{audio_path}"
        return f"Audio saved to: {gcs_uri}", audio_folder
    except Exception as e:
        return f"An error occurred while saving audio: {str(e)}", None

def get_audio_duration(gcs_audio_uri):
    """
    Retrieves the duration of the audio file in seconds.
    """
    try:
        bucket_name = gcs_audio_uri.split("/")[2]
        blob_name = "/".join(gcs_audio_uri.split("/")[3:])
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            blob.download_to_filename(temp_file.name)
            temp_file.close()

            cmd = f"ffmpeg -i {temp_file.name} 2>&1 | grep 'Duration' | awk '{{print $2}}' | tr -d ,"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            duration_str = result.stdout.strip()
            os.remove(temp_file.name)

            if duration_str:
                parts = duration_str.split(":")
                seconds = float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
                return seconds
            else:
                return 0
    except Exception as e:
        return 0

def transcribe_audio(gcs_audio_uri):
    """
    Transcribes audio from a GCS file using Google Cloud Speech-to-Text API.
    """
    try:
        audio = speech.RecognitionAudio(uri=gcs_audio_uri)
        if gcs_audio_uri.endswith(".wav"):
            encoding = speech.RecognitionConfig.AudioEncoding.LINEAR16
        elif gcs_audio_uri.endswith(".mp3"):
            encoding = speech.RecognitionConfig.AudioEncoding.MP3
        else:
            raise ValueError("Unsupported file type. Only MP3 and WAV are supported.")

        config = speech.RecognitionConfig(
            encoding=encoding,
            sample_rate_hertz=44100,
            language_code="en-US",
            audio_channel_count=2,
        )

        audio_duration_seconds = get_audio_duration(gcs_audio_uri)
        if audio_duration_seconds > 60:
            operation = speech_client.long_running_recognize(config=config, audio=audio)
            response = operation.result(timeout=600)
        else:
            response = speech_client.recognize(config=config, audio=audio)

        transcript = " ".join([result.alternatives[0].transcript for result in response.results])

        # Update the global transcript variable
        global global_transcript
        global_transcript = transcript

        return transcript if transcript else "No speech detected."
    except Exception as e:
        return f"Transcription failed due to an error: {str(e)}"

def list_files_in_bucket():
    """
    List all files in the bucket with a hierarchical view of folders and subfolders.
    """
    files = {}
    blobs = storage_client.list_blobs(bucket_name)
    for blob in blobs:
        folder = "/".join(blob.name.split("/")[:-1]) or "root"
        files.setdefault(folder, []).append(blob.name)
    return files

def classify_transcript(transcript):
    """
    Classifies the transcript using the Gemini API.
    """
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")

    # First prompt: Identify major classes in the transcript
    prompt1 = f"""
    Read the following meeting transcript:

    {transcript}

    Based on the context, identify the major areas or tasks discussed.
    Return a concise, comma-separated list of these major areas.
    """

    response1 = model.generate_content(prompt1)
    major_classes = response1.text.strip().split(",")

    # Second prompt: Classify each line in the transcript
    prompt2 = f"""
    Read the following meeting transcript:

    {transcript}

    Classify each line into one of the following areas: {', '.join(major_classes)}.
    """

    response2 = model.generate_content(prompt2)

    return response2.text.strip()

def get_response(message, history):
    """
    Handles user interaction with the assistant and incorporates chat history.
    """
    if not global_transcript:
        return [{"role": "assistant", "content": "Please transcribe audio before asking questions."}]

    # Construct the chat history as part of the prompt
    history_text = "\n".join(
        f"User: {entry['content']}" if entry['role'] == "user" else f"Assistant: {entry['content']}"
        for entry in history
    )

    prompt = f"""
    Based on the meeting transcript:

    {global_transcript}

    Here is the conversation history:
    {history_text}

    Now, answer the following question:
    {message}
    """

    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return history + [{"role": "user", "content": message}, {"role": "assistant", "content": response.text.strip()}]


# Gradio Interface
# def gradio_interface():
#     with gr.Blocks() as demo:
#         gr.Markdown("# Meeting Minutes Assistant")

#         with gr.Tab("Upload Audio"):
#             audio_input = gr.Audio(type="filepath", label="Upload Audio File")
#             upload_button = gr.Button("Upload Audio")
#             audio_output = gr.Textbox(label="Audio Upload Status")

#             upload_button.click(save_audio_to_gcs, inputs=audio_input, outputs=[audio_output])

#         with gr.Tab("Transcribe Audio"):
#             folder_selection = gr.Dropdown(label="Select Folder", choices=list(list_files_in_bucket().keys()))
#             audio_selection = gr.Dropdown(label="Select Audio File")
#             transcribe_button = gr.Button("Transcribe Audio")
#             transcript_output = gr.Textbox(label="Transcript")

#             def update_audio_dropdown(folder):
#                 audio_files = list_files_in_bucket().get(folder, [])
#                 return gr.update(choices=audio_files)

#             folder_selection.change(update_audio_dropdown, inputs=folder_selection, outputs=audio_selection)

#             def transcribe_selected_audio(audio_file):
#                 gcs_uri = f"gs://{bucket_name}/{audio_file}"
#                 return transcribe_audio(gcs_uri)

#             transcribe_button.click(transcribe_selected_audio, inputs=audio_selection, outputs=transcript_output)

#         with gr.Tab("Classify Transcript"):
#             transcript_input = gr.Textbox(label="Enter Transcript")
#             classify_button = gr.Button("Classify Transcript")
#             classification_output = gr.Textbox(label="Classification Result")

#             classify_button.click(classify_transcript, inputs=transcript_input, outputs=classification_output)

#         with gr.Tab("Chat with Assistant"):
#             chat_history = gr.Chatbot(type="messages")  # Remove 'type="messages"' for compatibility
#             user_input = gr.Textbox(placeholder="Ask a question about the meeting...")
#             submit_button = gr.Button("Submit")
#             submit_button.click(get_response, inputs=[user_input, chat_history], outputs=chat_history)

#     demo.launch()



def gradio_interface():
    with gr.Blocks() as demo:
        gr.Markdown("# Meeting Minutes Assistant")

        with gr.Tab("Upload Audio"):
            audio_input = gr.Audio(type="filepath", label="Upload Audio File")
            upload_button = gr.Button("Upload Audio")
            audio_output = gr.Textbox(label="Audio Upload Status")

            def upload_and_refresh(audio):
                # Upload the audio and refresh the folder list
                upload_status, _ = save_audio_to_gcs(audio)
                updated_folders = list(list_files_in_bucket().keys())
                return upload_status, gr.update(choices=updated_folders)

            upload_button.click(
                upload_and_refresh,
                inputs=audio_input,
                outputs=[audio_output],  # Only output audio upload status
            )

        with gr.Tab("Transcribe Audio"):
            folder_selection = gr.Dropdown(label="Select Folder", choices=[])  # Only appears in this tab
            audio_selection = gr.Dropdown(label="Select Audio File")
            transcribe_button = gr.Button("Transcribe Audio")
            transcript_output = gr.Textbox(label="Transcript")

            def refresh_folder_list():
                """Fetch and update the list of folders from the GCS bucket."""
                folders = list(list_files_in_bucket().keys())
                return gr.update(choices=folders)

            def update_audio_list(folder):
                """Fetch and update the list of audio files based on the selected folder."""
                audio_files = list_files_in_bucket().get(folder, [])
                return gr.update(choices=audio_files)

            # Refresh folders button
            refresh_folders = gr.Button("Refresh Folders")
            refresh_folders.click(refresh_folder_list, inputs=None, outputs=folder_selection)

            folder_selection.change(update_audio_list, inputs=folder_selection, outputs=audio_selection)

            transcribe_button.click(
                lambda audio_file: transcribe_audio(f"gs://{bucket_name}/{audio_file}"),
                inputs=audio_selection,
                outputs=transcript_output,
            )

        with gr.Tab("Classify Transcript"):
            transcript_input = gr.Textbox(label="Enter Transcript")
            classify_button = gr.Button("Classify Transcript")
            classification_output = gr.Textbox(label="Classification Result")

            classify_button.click(classify_transcript, inputs=transcript_input, outputs=classification_output)

        with gr.Tab("Chat with Assistant"):
            chat_history = gr.Chatbot(type="messages")
            user_input = gr.Textbox(placeholder="Ask a question about the meeting...")
            submit_button = gr.Button("Submit")
            submit_button.click(get_response, inputs=[user_input, chat_history], outputs=chat_history)

    demo.launch()



# Run the interface
gradio_interface()
