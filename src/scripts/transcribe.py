# import gradio as gr
# from google.cloud import storage, speech
# from google.oauth2 import service_account
# import os
# import subprocess
# import tempfile

# # Path to the service account JSON file
# SERVICE_ACCOUNT_FILE = ""  # Update the path as needed

# # Initialize Google Cloud clients
# credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
# storage_client = storage.Client(credentials=credentials)
# speech_client = speech.SpeechClient(credentials=credentials)
# bucket_name = "meeting-ai-storage"  # Replace with your bucket name
# bucket = storage_client.bucket(bucket_name)

# def list_files_in_bucket():
#     """
#     List all files in the bucket with a hierarchical view of folders and subfolders.
#     """
#     files = {}
#     blobs = storage_client.list_blobs(bucket_name)
#     for blob in blobs:
#         folder = "/".join(blob.name.split("/")[:-1]) or "root"
#         files.setdefault(folder, []).append(blob.name)
#     return files

# def retrieve_file_link(selected_file):
#     """
#     Retrieve the GCS link of the selected file.
#     """
#     return f"gs://{bucket_name}/{selected_file}"

# def get_audio_duration(gcs_audio_uri):
#     """
#     Retrieves the duration of the audio file in seconds.
#     This requires ffmpeg to be installed on your system.
#     Downloads the file temporarily from GCS to compute duration.
#     """
#     try:
#         # Initialize the Google Cloud storage client
#         storage_client = storage.Client(credentials=credentials)
#         bucket_name = gcs_audio_uri.split("/")[2]
#         blob_name = "/".join(gcs_audio_uri.split("/")[3:])
#         bucket = storage_client.bucket(bucket_name)
#         blob = bucket.blob(blob_name)

#         # Create a temporary file to download the audio
#         with tempfile.NamedTemporaryFile(delete=False) as temp_file:
#             blob.download_to_filename(temp_file.name)
#             temp_file.close()
            
#             # Use ffmpeg to get the duration of the audio file
#             cmd = f"ffmpeg -i {temp_file.name} 2>&1 | grep 'Duration' | awk '{{print $2}}' | tr -d ,"
#             result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
#             duration_str = result.stdout.strip()
            
#             # Clean up the temporary file after getting the duration
#             os.remove(temp_file.name)
            
#             # Convert the duration from HH:MM:SS.MS format to seconds
#             if duration_str:
#                 parts = duration_str.split(":")
#                 seconds = float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
#                 return seconds
#             else:
#                 return 0  # Return 0 if duration couldn't be fetched
#     except Exception as e:
#         print(f"Error while calculating duration: {e}")
#         return 0  # Return 0 in case of error

# def transcribe_audio(gcs_audio_uri):
#     """
#     Transcribes audio from a GCS file using Google Cloud Speech-to-Text API.
#     Supports both MP3 and WAV formats.
#     """
#     try:
#         # Prepare audio URI
#         audio = speech.RecognitionAudio(uri=gcs_audio_uri)

#         # Configure the recognition settings based on the file type
#         if gcs_audio_uri.endswith(".wav"):
#             encoding = speech.RecognitionConfig.AudioEncoding.LINEAR16
#         elif gcs_audio_uri.endswith(".mp3"):
#             encoding = speech.RecognitionConfig.AudioEncoding.MP3
#         else:
#             raise ValueError("Unsupported file type. Only MP3 and WAV are supported.")

#         config = speech.RecognitionConfig(
#             encoding=encoding,
#             sample_rate_hertz=44100,  # Ensure this matches your file's sample rate
#             language_code="en-US",
#             audio_channel_count=2,  # Adjust based on the file's actual channel count
#         )

#         # Get audio duration
#         audio_duration_seconds = get_audio_duration(gcs_audio_uri)
#         print("Audio duration: ", audio_duration_seconds)

#         # Decide API method based on audio duration
#         if audio_duration_seconds > 60:
#             print("Using Long Running Recognize for transcription...")
#             operation = speech_client.long_running_recognize(config=config, audio=audio)
#             print("Operation started. Waiting for completion...")

#             # Allow more time for long operations
#             response = operation.result(timeout=600)  # Adjust timeout if necessary
#             print("Operation completed successfully.")
#         else:
#             print("Using standard Recognize API for transcription...")
#             response = speech_client.recognize(config=config, audio=audio)

#         # Collect and return the transcription result
#         transcript = " ".join([result.alternatives[0].transcript for result in response.results])
        
#         if transcript:
#             return transcript
#         else:
#             return "No speech detected."

#     except Exception as e:
#         print(f"Error during transcription: {e}")
#         return "Transcription failed due to an error."


# def process_file_and_transcribe(selected_file):
#     """
#     Process the selected file: Retrieve its GCS URI, transcribe audio, and save transcript.
#     """
#     try:
#         # Use the selected file path to retrieve the GCS URI
#         file_url = retrieve_file_link(selected_file)
#         transcript = transcribe_audio(file_url)
        
#         # Save transcript to a text file
#         transcript_file = f"transcript_{os.path.basename(selected_file)}.txt"
#         with open(transcript_file, "w") as f:
#             f.write(transcript)
        
#         return f"Transcript saved to: {transcript_file}"

#     except Exception as e:
#         return f"An error occurred: {str(e)}"

# def gradio_interface():
#     """
#     Gradio interface for selecting files and transcribing audio using Blocks.
#     """
#     files = list_files_in_bucket()
#     folder_options = list(files.keys())
    
#     with gr.Blocks() as interface:
#         selected_folder = gr.Dropdown(choices=folder_options, label="Select Folder")
#         selected_file = gr.Dropdown(choices=[], label="Select File")
#         transcript_output = gr.Textbox(label="Transcript", placeholder="Transcript will appear here...")

#         # Update files based on selected folder
#         def update_files(folder):
#             return gr.update(choices=files.get(folder, []))
        
#         # Process the selected file
#         def process_selected_file(folder, file):
#             # Here we are using the complete path directly
#             full_path = file if folder == "root" else f"{file}"
#             return process_file_and_transcribe(full_path)
        
#         selected_folder.change(update_files, inputs=selected_folder, outputs=selected_file)
        
#         gr.Button("Transcribe").click(process_selected_file, inputs=[selected_folder, selected_file], outputs=transcript_output)
        
#     interface.launch()

# if __name__ == "__main__":
#     gradio_interface()



import gradio as gr
from google.cloud import storage, speech
from google.oauth2 import service_account
import os
import subprocess
import tempfile
import threading
import time
import sys

# Path to the service account JSON file
SERVICE_ACCOUNT_FILE = ""  # Update the path as needed

# Initialize Google Cloud clients
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
storage_client = storage.Client(credentials=credentials)
speech_client = speech.SpeechClient(credentials=credentials)
bucket_name = "meeting-ai-storage"  # Replace with your bucket name
bucket = storage_client.bucket(bucket_name)

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

def retrieve_file_link(selected_file):
    """
    Retrieve the GCS link of the selected file.
    """
    return f"gs://{bucket_name}/{selected_file}"

def get_audio_duration(gcs_audio_uri):
    """
    Retrieves the duration of the audio file in seconds.
    This requires ffmpeg to be installed on your system.
    Downloads the file temporarily from GCS to compute duration.
    """
    try:
        # Initialize the Google Cloud storage client
        storage_client = storage.Client(credentials=credentials)
        bucket_name = gcs_audio_uri.split("/")[2]
        blob_name = "/".join(gcs_audio_uri.split("/")[3:])
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        # Create a temporary file to download the audio
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            blob.download_to_filename(temp_file.name)
            temp_file.close()
            
            # Use ffmpeg to get the duration of the audio file
            cmd = f"ffmpeg -i {temp_file.name} 2>&1 | grep 'Duration' | awk '{{print $2}}' | tr -d ,"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            duration_str = result.stdout.strip()
            
            # Clean up the temporary file after getting the duration
            os.remove(temp_file.name)
            
            # Convert the duration from HH:MM:SS.MS format to seconds
            if duration_str:
                parts = duration_str.split(":")
                seconds = float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
                return seconds
            else:
                return 0  # Return 0 if duration couldn't be fetched
    except Exception as e:
        print(f"Error while calculating duration: {e}")
        return 0  # Return 0 in case of error

def transcribe_audio(gcs_audio_uri):
    """
    Transcribes audio from a GCS file using Google Cloud Speech-to-Text API.
    Supports both MP3 and WAV formats.
    """
    try:
        # Prepare audio URI
        audio = speech.RecognitionAudio(uri=gcs_audio_uri)

        # Configure the recognition settings based on the file type
        if gcs_audio_uri.endswith(".wav"):
            encoding = speech.RecognitionConfig.AudioEncoding.LINEAR16
        elif gcs_audio_uri.endswith(".mp3"):
            encoding = speech.RecognitionConfig.AudioEncoding.MP3
        else:
            raise ValueError("Unsupported file type. Only MP3 and WAV are supported.")

        config = speech.RecognitionConfig(
            encoding=encoding,
            sample_rate_hertz=44100,  # Ensure this matches your file's sample rate
            language_code="en-US",
            audio_channel_count=2,  # Adjust based on the file's actual channel count
        )

        # Get audio duration
        audio_duration_seconds = get_audio_duration(gcs_audio_uri)
        print("Audio duration: ", audio_duration_seconds)

        # Decide API method based on audio duration
        if audio_duration_seconds > 60:
            print("Using Long Running Recognize for transcription...")
            operation = speech_client.long_running_recognize(config=config, audio=audio)
            print("Operation started. Waiting for completion...")

            # Allow more time for long operations
            response = operation.result(timeout=600)  # Adjust timeout if necessary
            print("Operation completed successfully.")
        else:
            print("Using standard Recognize API for transcription...")
            response = speech_client.recognize(config=config, audio=audio)

        # Collect and return the transcription result
        transcript = " ".join([result.alternatives[0].transcript for result in response.results])
        
        if transcript:
            return transcript
        else:
            return "No speech detected."

    except Exception as e:
        print(f"Error during transcription: {e}")
        return "Transcription failed due to an error."


def process_file_and_transcribe(selected_file):
    """
    Process the selected file: Retrieve its GCS URI, transcribe audio, and save transcript.
    """
    try:
        # Use the selected file path to retrieve the GCS URI
        file_url = retrieve_file_link(selected_file)
        transcript = transcribe_audio(file_url)
        
        # Save transcript to a text file
        transcript_file = f"transcript_{os.path.basename(selected_file)}.txt"
        with open(transcript_file, "w") as f:
            f.write(transcript)
        
        return f"Transcript saved to: {transcript_file}"

    except Exception as e:
        return f"An error occurred: {str(e)}"

def gradio_interface():
    """
    Gradio interface for selecting files and transcribing audio using Blocks.
    """
    files = list_files_in_bucket()
    folder_options = list(files.keys())
    
    with gr.Blocks() as interface:
        selected_folder = gr.Dropdown(choices=folder_options, label="Select Folder")
        selected_file = gr.Dropdown(choices=[], label="Select File")
        transcript_output = gr.Textbox(label="Transcript", placeholder="Transcript will appear here...")

        # Update files based on selected folder
        def update_files(folder):
            return gr.update(choices=files.get(folder, []))
        
        # Process the selected file
        def process_selected_file(folder, file):
            # Here we are using the complete path directly
            full_path = file if folder == "root" else f"{file}"
            return process_file_and_transcribe(full_path)
        
        selected_folder.change(update_files, inputs=selected_folder, outputs=selected_file)
        
        gr.Button("Transcribe").click(process_selected_file, inputs=[selected_folder, selected_file], outputs=transcript_output)
        
        # Add close button to shut down Gradio and the script
        def close_gradio_and_script():
            interface.close()
            os._exit(0)  # Forcefully close the script
            
        close_button = gr.Button("Close Application")
        close_button.click(close_gradio_and_script)

    interface.launch()

if __name__ == "__main__":
    gradio_interface()
    
