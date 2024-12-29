import gradio as gr
import datetime
import os
import tempfile
import subprocess
import platform
from google.cloud import storage, speech
from google.oauth2 import service_account
from pathlib import Path  # For cross-platform path handling
from pydub.utils import mediainfo  # For audio duration as a fallback
import google.generativeai as genai

# Path to the service account JSON file
SERVICE_ACCOUNT_FILE = ""  # Update the name as needed

# Initialize Google Cloud clients
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
storage_client = storage.Client(credentials=credentials)
speech_client = speech.SpeechClient(credentials=credentials)
bucket_name = ""  # Replace with your bucket name
bucket = storage_client.bucket(bucket_name)

# Replace with your actual Gemini API key
os.environ["GEMINI_API_KEY"] = ""

# Global context for transcript
global_transcript = ""


def save_audio_to_gcs(audio):
    """
    Saves an audio file (either uploaded or recorded) to Google Cloud Storage.
    Generates a hierarchical path for the file based on the current timestamp.
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

        # Determine file name
        audio_path = Path(audio).name if isinstance(audio, str) else f"audio_{int(time.time())}.wav"
        full_audio_path = f"{audio_folder}{audio_path}"

        # Upload to GCS
        blob = bucket.blob(full_audio_path)
        blob.upload_from_filename(audio)

        gcs_uri = f"gs://{bucket_name}/{full_audio_path}"
        return f"Audio saved to: {gcs_uri}", audio_folder
    except Exception as e:
        return f"An error occurred while saving audio: {str(e)}", None


def get_audio_duration(gcs_audio_uri):
    """
    Retrieves the duration of the audio file in seconds using FFmpeg, handling GCS URIs.
    Compatible with both Linux and Windows.
    """
    try:
        # Extract bucket name and blob name
        bucket_name = gcs_audio_uri.split("/")[2]
        blob_name = "/".join(gcs_audio_uri.split("/")[3:])
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        # Download the audio file to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(blob_name)[1]) as temp_file:
            blob.download_to_filename(temp_file.name)
            temp_file_path = temp_file.name

        # Use ffmpeg to extract duration information
        cmd = [
            "ffmpeg",
            "-i",
            temp_file_path,
            "-hide_banner",
            "-f",
            "null",
            "-"
        ]
        result = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)
        
        # Parse the FFmpeg output to find the duration
        ffmpeg_output = result.stderr
        duration_line = next((line for line in ffmpeg_output.split("\n") if "Duration" in line), None)

        # Remove the temporary file
        os.remove(temp_file_path)

        if duration_line:
            # Extract the duration from the line
            duration_str = duration_line.split(",")[0].split("Duration:")[1].strip()
            parts = duration_str.split(":")
            seconds = float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
            return seconds
        else:
            raise ValueError("Unable to extract duration from FFmpeg output.")
    except Exception as e:
        print(f"Error retrieving audio duration: {str(e)}")
        return 0




def transcribe_audio(gcs_audio_uri):
    """
    Transcribes audio from a GCS file using Google Cloud Speech-to-Text API.
    """
    try:
        audio = speech.RecognitionAudio(uri=gcs_audio_uri)
        encoding = (
            speech.RecognitionConfig.AudioEncoding.LINEAR16
            if gcs_audio_uri.endswith(".wav")
            else speech.RecognitionConfig.AudioEncoding.MP3
        )

        config = speech.RecognitionConfig(
            encoding=encoding,
            sample_rate_hertz=44100,
            language_code="en-US",
            audio_channel_count=2,
        )

        audio_duration_seconds = get_audio_duration(gcs_audio_uri)

        # Ensure duration is numeric and greater than zero
        if not isinstance(audio_duration_seconds, (int, float)) or audio_duration_seconds <= 0:
            return "Error: Unable to determine audio duration. Please check the audio file."

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

    # Identify major areas
    prompt1 = f"""
    Read the following meeting transcript:

    {transcript}

    Based on the context, identify the major areas or tasks discussed.
    Return a concise, comma-separated list of these major areas.
    """

    response1 = model.generate_content(prompt1)
    major_classes = response1.text.strip().split(",")

    # Classify each line
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
def gradio_interface():
    with gr.Blocks() as demo:
        gr.Markdown("# Meeting Minutes Assistant")

        with gr.Tab("Upload Audio"):
            audio_input = gr.Audio(type="filepath", label="Upload or Record Audio File")
            upload_button = gr.Button("Upload Audio")
            audio_output = gr.Textbox(label="Audio Upload Status")

            upload_button.click(
                lambda audio: save_audio_to_gcs(audio)[0],
                inputs=audio_input,
                outputs=audio_output,
            )

        with gr.Tab("Transcribe Audio"):
            folder_selection = gr.Dropdown(label="Select Folder", choices=[])
            audio_selection = gr.Dropdown(label="Select Audio File")
            transcribe_button = gr.Button("Transcribe Audio")
            transcript_output = gr.Textbox(label="Transcript")

            def refresh_folder_list():
                return gr.update(choices=list(list_files_in_bucket().keys()))

            def update_audio_list(folder):
                return gr.update(choices=list_files_in_bucket().get(folder, []))

            refresh_folders = gr.Button("Refresh Folders")
            refresh_folders.click(refresh_folder_list, outputs=folder_selection)

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
