# def save_audio_to_gcs(audio):
#     """
#     Saves an audio file to Google Cloud Storage in a structured folder hierarchy.
#     The hierarchy is: <current_date>/<folder_number>/audio.wav
#     """
#     try:
#         current_date = datetime.datetime.now().strftime("%Y-%m-%d")
#         date_folder = f"{current_date}/"
#         blobs = list(storage_client.list_blobs(bucket_name, prefix=date_folder))
#         folder_numbers = [
#             int(blob.name.split("/")[1])
#             for blob in blobs
#             if len(blob.name.split("/")) > 1 and blob.name.split("/")[1].isdigit()
#         ]
#         new_folder_number = max(folder_numbers, default=0) + 1
#         audio_folder = f"{date_folder}{new_folder_number}/"
#         audio_path = f"{audio_folder}audio.wav"

#         blob = bucket.blob(audio_path)
#         blob.upload_from_filename(audio)

#         # Return the GCS URI (gs://<bucket_name>/<path_to_audio>)
#         gcs_uri = f"gs://{bucket_name}/{audio_path}"
#         return f"Audio saved to: {gcs_uri}", audio_folder
#     except Exception as e:
#         return f"An error occurred while saving audio: {str(e)}", None



# def gradio_interface():
#     with gr.Blocks() as demo:
#         gr.Markdown("# Meeting Minutes Assistant")

#         with gr.Tab("Upload Audio"):
#             audio_input = gr.Audio(type="filepath", label="Upload Audio File")
#             upload_button = gr.Button("Upload Audio")
#             audio_output = gr.Textbox(label="Audio Upload Status")

#             def upload_and_refresh(audio):
#                 # Upload the audio and refresh the folder list
#                 upload_status, _ = save_audio_to_gcs(audio)
#                 updated_folders = list(list_files_in_bucket().keys())
#                 return upload_status, gr.update(choices=updated_folders)

#             upload_button.click(
#                 upload_and_refresh,
#                 inputs=audio_input,
#                 outputs=[audio_output],  # Only output audio upload status
#             )

#         with gr.Tab("Transcribe Audio"):
#             folder_selection = gr.Dropdown(label="Select Folder", choices=[])  # Only appears in this tab
#             audio_selection = gr.Dropdown(label="Select Audio File")
#             transcribe_button = gr.Button("Transcribe Audio")
#             transcript_output = gr.Textbox(label="Transcript")

#             def refresh_folder_list():
#                 """Fetch and update the list of folders from the GCS bucket."""
#                 folders = list(list_files_in_bucket().keys())
#                 return gr.update(choices=folders)

#             def update_audio_list(folder):
#                 """Fetch and update the list of audio files based on the selected folder."""
#                 audio_files = list_files_in_bucket().get(folder, [])
#                 return gr.update(choices=audio_files)

#             # Refresh folders button
#             refresh_folders = gr.Button("Refresh Folders")
#             refresh_folders.click(refresh_folder_list, inputs=None, outputs=folder_selection)

#             folder_selection.change(update_audio_list, inputs=folder_selection, outputs=audio_selection)

#             transcribe_button.click(
#                 lambda audio_file: transcribe_audio(f"gs://{bucket_name}/{audio_file}"),
#                 inputs=audio_selection,
#                 outputs=transcript_output,
#             )

#         with gr.Tab("Classify Transcript"):
#             transcript_input = gr.Textbox(label="Enter Transcript")
#             classify_button = gr.Button("Classify Transcript")
#             classification_output = gr.Textbox(label="Classification Result")

#             classify_button.click(classify_transcript, inputs=transcript_input, outputs=classification_output)

#         with gr.Tab("Chat with Assistant"):
#             chat_history = gr.Chatbot(type="messages")
#             user_input = gr.Textbox(placeholder="Ask a question about the meeting...")
#             submit_button = gr.Button("Submit")
#             submit_button.click(get_response, inputs=[user_input, chat_history], outputs=chat_history)

#     demo.launch()

