# import gradio as gr
# import datetime
# import os
# from google.cloud import storage
# from google.oauth2 import service_account

# # Path to the service account JSON file
# SERVICE_ACCOUNT_FILE = "sa_minutes_ai.json"  # Update the path as needed

# # Initialize Google Cloud Storage client using the service account file
# credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
# client = storage.Client(credentials=credentials)
# bucket_name = "meeting-ai-storage"  # Replace with your bucket name
# bucket = client.bucket(bucket_name)

# def save_audio_to_gcs(audio):
#     """
#     Saves an audio file to Google Cloud Storage in a structured folder hierarchy.
#     The hierarchy is: <current_date>/<folder_number>/audio.wav

#     Args:
#         audio (str): Path to the audio file.

#     Returns:
#         str: Success message with the path in GCS or an error message.
#     """
#     try:
#         # Get the current date
#         current_date = datetime.datetime.now().strftime("%Y-%m-%d")

#         # Path for the date folder
#         date_folder = f"{current_date}/"

#         # Get all blobs in the date folder
#         blobs = list(client.list_blobs(bucket_name, prefix=date_folder))

#         # Extract folder numbers
#         folder_numbers = [
#             int(blob.name.split("/")[1])
#             for blob in blobs
#             if len(blob.name.split("/")) > 1 and blob.name.split("/")[1].isdigit()
#         ]

#         # Determine the new folder number
#         new_folder_number = max(folder_numbers, default=0) + 1

#         # Path for the new folder and audio file
#         audio_folder = f"{date_folder}{new_folder_number}/"
#         audio_path = f"{audio_folder}audio.wav"

#         # Create the blob and upload the file
#         blob = bucket.blob(audio_path)
#         blob.upload_from_filename(audio)

#         return f"Audio saved to: {audio_path}"

#     except Exception as e:
#         return f"An error occurred: {str(e)}"

# # Gradio interface function
# def record_and_upload(audio):
#     """
#     Handles audio recording and uploads it to Google Cloud Storage.

#     Args:
#         audio (str): Path to the audio file.

#     Returns:
#         str: Response from the save_audio_to_gcs function.
#     """
#     if not audio:
#         return "No audio file provided."
#     return save_audio_to_gcs(audio)

# # Gradio interface
# interface = gr.Interface(
#     fn=record_and_upload,
#     inputs=gr.Audio(sources="microphone", type="filepath"),
#     outputs="text",
#     title="Audio Recorder and Uploader",
#     description="Record an audio file and upload it to Google Cloud Storage with a structured folder hierarchy."
# )

# # Launch the interface
# if __name__ == "__main__":
#     interface.launch()



# import gradio as gr
# import datetime
# import os
# from google.cloud import storage
# from google.oauth2 import service_account
# import sys

# # Path to the service account JSON file
# SERVICE_ACCOUNT_FILE = "sa_minutes_ai.json"  # Update the path as needed

# # Initialize Google Cloud Storage client using the service account file
# credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
# client = storage.Client(credentials=credentials)
# bucket_name = "meeting-ai-storage"  # Replace with your bucket name
# bucket = client.bucket(bucket_name)

# def save_audio_to_gcs(audio):
#     """
#     Saves an audio file to Google Cloud Storage in a structured folder hierarchy.
#     The hierarchy is: <current_date>/<folder_number>/audio.wav

#     Args:
#         audio (str): Path to the audio file.

#     Returns:
#         str: Success message with the path in GCS or an error message.
#     """
#     try:
#         # Get the current date
#         current_date = datetime.datetime.now().strftime("%Y-%m-%d")

#         # Path for the date folder
#         date_folder = f"{current_date}/"

#         # Get all blobs in the date folder
#         blobs = list(client.list_blobs(bucket_name, prefix=date_folder))

#         # Extract folder numbers
#         folder_numbers = [
#             int(blob.name.split("/")[1])
#             for blob in blobs
#             if len(blob.name.split("/")) > 1 and blob.name.split("/")[1].isdigit()
#         ]

#         # Determine the new folder number
#         new_folder_number = max(folder_numbers, default=0) + 1

#         # Path for the new folder and audio file
#         audio_folder = f"{date_folder}{new_folder_number}/"
#         audio_path = f"{audio_folder}audio.wav"

#         # Create the blob and upload the file
#         blob = bucket.blob(audio_path)
#         blob.upload_from_filename(audio)

#         return f"Audio saved to: {audio_path}"

#     except Exception as e:
#         return f"An error occurred: {str(e)}"

# # Gradio interface function
# def record_and_upload(audio):
#     """
#     Handles audio recording and uploads it to Google Cloud Storage.

#     Args:
#         audio (str): Path to the audio file.

#     Returns:
#         str: Response from the save_audio_to_gcs function.
#     """
#     if not audio:
#         return "No audio file provided."
#     response = save_audio_to_gcs(audio)

#     # Close the Gradio interface and exit
#     gr.close_all()  # Ensure all Gradio interfaces are closed
#     sys.exit()  # Stop the Python script

#     return response  # This line won't execute but ensures proper syntax

# # Gradio interface
# interface = gr.Interface(
#     fn=record_and_upload,
#     inputs=gr.Audio(sources="microphone", type="filepath"),
#     outputs="text",
#     title="Audio Recorder and Uploader",
#     description="Record an audio file and upload it to Google Cloud Storage with a structured folder hierarchy."
# )

# # Launch the interface
# if __name__ == "__main__":
#     interface.launch()


# import gradio as gr
# import datetime
# import os
# from google.cloud import storage
# from google.oauth2 import service_account
# import threading
# import time

# # Path to the service account JSON file
# SERVICE_ACCOUNT_FILE = "sa_minutes_ai.json"  # Update the path as needed

# # Initialize Google Cloud Storage client using the service account file
# credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
# client = storage.Client(credentials=credentials)
# bucket_name = "meeting-ai-storage"  # Replace with your bucket name
# bucket = client.bucket(bucket_name)

# def save_audio_to_gcs(audio):
#     """
#     Saves an audio file to Google Cloud Storage in a structured folder hierarchy.
#     The hierarchy is: <current_date>/<folder_number>/audio.wav

#     Args:
#         audio (str): Path to the audio file.

#     Returns:
#         str: Success message with the path in GCS or an error message.
#     """
#     try:
#         # Get the current date
#         current_date = datetime.datetime.now().strftime("%Y-%m-%d")

#         # Path for the date folder
#         date_folder = f"{current_date}/"

#         # Get all blobs in the date folder
#         blobs = list(client.list_blobs(bucket_name, prefix=date_folder))

#         # Extract folder numbers
#         folder_numbers = [
#             int(blob.name.split("/")[1])
#             for blob in blobs
#             if len(blob.name.split("/")) > 1 and blob.name.split("/")[1].isdigit()
#         ]

#         # Determine the new folder number
#         new_folder_number = max(folder_numbers, default=0) + 1

#         # Path for the new folder and audio file
#         audio_folder = f"{date_folder}{new_folder_number}/"
#         audio_path = f"{audio_folder}audio.wav"

#         # Create the blob and upload the file
#         blob = bucket.blob(audio_path)
#         blob.upload_from_filename(audio)

#         return f"Audio saved to: {audio_path}"

#     except Exception as e:
#         return f"An error occurred: {str(e)}"

# def record_and_upload(audio):
#     """
#     Handles audio recording and uploads it to Google Cloud Storage.

#     Args:
#         audio (str): Path to the audio file.

#     Returns:
#         str: Response from the save_audio_to_gcs function.
#     """
#     if not audio:
#         return "No audio file provided."
#     response = save_audio_to_gcs(audio)

#     # Delay server shutdown to let the response be sent to the client
#     threading.Thread(target=delayed_shutdown).start()

#     return response

# def delayed_shutdown():
#     """
#     Waits for 2 seconds and then shuts down the Gradio server cleanly.
#     """
#     time.sleep(2)  # Allow time for the response to be displayed
#     print("Shutting down the Gradio server...")
#     interface.close()  # Close the Gradio interface

# # Gradio interface
# interface = gr.Interface(
#     fn=record_and_upload,
#     inputs=gr.Audio(sources="microphone", type="filepath"),
#     outputs="text",
#     title="Audio Recorder and Uploader",
#     description="Record an audio file and upload it to Google Cloud Storage with a structured folder hierarchy."
# )

# # Launch the interface
# if __name__ == "__main__":
#     interface.launch()



import gradio as gr
import datetime
import os
from google.cloud import storage
from google.oauth2 import service_account

# Path to the service account JSON file
SERVICE_ACCOUNT_FILE = "sa_minutes_ai.json"  # Update the path as needed

# Initialize Google Cloud Storage client using the service account file
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
client = storage.Client(credentials=credentials)
bucket_name = "meeting-ai-storage"  # Replace with your bucket name
bucket = client.bucket(bucket_name)

def save_audio_to_gcs(audio):
    """
    Saves an audio file to Google Cloud Storage in a structured folder hierarchy.
    The hierarchy is: <current_date>/<folder_number>/audio.wav

    Args:
        audio (str): Path to the audio file.

    Returns:
        str: Success message with the path in GCS or an error message.
    """
    try:
        # Get the current date
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")

        # Path for the date folder
        date_folder = f"{current_date}/"

        # Get all blobs in the date folder
        blobs = list(client.list_blobs(bucket_name, prefix=date_folder))

        # Extract folder numbers
        folder_numbers = [
            int(blob.name.split("/")[1])
            for blob in blobs
            if len(blob.name.split("/")) > 1 and blob.name.split("/")[1].isdigit()
        ]

        # Determine the new folder number
        new_folder_number = max(folder_numbers, default=0) + 1

        # Path for the new folder and audio file
        audio_folder = f"{date_folder}{new_folder_number}/"
        audio_path = f"{audio_folder}audio.wav"

        # Create the blob and upload the file
        blob = bucket.blob(audio_path)
        blob.upload_from_filename(audio)

        return f"Audio saved to: {audio_path}"

    except Exception as e:
        return f"An error occurred while saving audio: {str(e)}"

def record_and_upload(audio):
    """
    Handles audio recording and uploads it to Google Cloud Storage.

    Args:
        audio (str): Path to the audio file.

    Returns:
        str: Response from the save_audio_to_gcs function.
    """
    if not audio:
        return "No audio file provided."
    return save_audio_to_gcs(audio)

def close_gradio():
    """
    Closes the Gradio interface and terminates the script.
    """
    print("Shutting down the Gradio server...")
    os._exit(0)  # Forcefully terminate the script

# Gradio interface
with gr.Blocks() as interface:
    gr.Markdown("# Audio Recorder and Uploader")
    gr.Markdown("Record an audio file and upload it to Google Cloud Storage with a structured folder hierarchy.")
    
    audio_input = gr.Audio(sources="microphone", type="filepath", label="Record Audio")
    upload_button = gr.Button("Upload and Save")
    output_text = gr.Textbox(label="Output", placeholder="Status will appear here...")
    
    # Button to close the application
    close_button = gr.Button("Close Application")

    upload_button.click(fn=record_and_upload, inputs=audio_input, outputs=output_text)
    close_button.click(fn=close_gradio)

# Launch the interface
if __name__ == "__main__":
    interface.launch()
