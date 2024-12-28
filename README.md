# Meeting Minutes Assistant

This repository contains a Python-based application that allows users to upload audio recordings of meetings, transcribe them into text, classify the transcript into key areas, and interact with an AI assistant to answer questions about the meeting. The application is built using Gradio for the user interface and Google Cloud APIs for audio processing and transcription.

---

## Features
1. **Upload Audio**: Save audio files to Google Cloud Storage (GCS).
2. **Transcribe Audio**: Convert audio files into text using Google Cloud Speech-to-Text.
3. **Classify Transcript**: Identify key areas or tasks discussed in the meeting using Gemini AI.
4. **Chat with Assistant**: Interact with a chatbot to ask questions about the meeting transcript.

---

## Prerequisites
- Python 3.7+
- Google Cloud Platform (GCP) account
- Service account JSON file for GCP
- Google Cloud Storage bucket for storing audio files
- Google Cloud Speech-to-Text API enabled
- Gemini AI API key
- Gradio library installed

---

## Installation and Setup

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up GCP**:
   - Create a service account in GCP.
   - Download the service account key JSON file and save it as `sa_minutes_ai.json` (or update the code with your file's name).
   - Enable the Speech-to-Text and Cloud Storage APIs in GCP.

4. **Set Up Environment Variables**:
   - Add your Gemini API key to the environment:
     ```bash
     export GEMINI_API_KEY="your-gemini-api-key"
     ```

5. **Create a GCS Bucket**:
   - Create a bucket named `meeting-ai-storage` (or update the code with your bucket's name).

6. **Run the Application**:
   ```bash
   python app.py
   ```
   This will launch the Gradio interface in your default web browser.

---

## How to Use

### **Upload Audio**
1. Navigate to the "Upload Audio" tab.
2. Upload an audio file (WAV or MP3).
3. Click the "Upload Audio" button.
4. The audio file will be saved to GCS in a folder hierarchy organized by date and folder number.

### **Transcribe Audio**
1. Go to the "Transcribe Audio" tab.
2. Select a folder from the dropdown to list audio files.
3. Choose an audio file and click "Transcribe Audio."
4. The transcript will appear in the output box.

### **Classify Transcript**
1. Switch to the "Classify Transcript" tab.
2. Enter or paste a transcript in the text box.
3. Click "Classify Transcript" to identify major areas discussed in the meeting.

### **Chat with Assistant**
1. Open the "Chat with Assistant" tab.
2. Ask questions about the meeting based on the transcript.
3. The assistant will respond using the provided context.

---

## Function Descriptions

### [save_audio_to_gcs(audio)](./app.py#L27)
- Saves an uploaded audio file to GCS.
- Organizes files into folders based on the current date and a folder number.
- Returns the GCS URI and folder path of the uploaded file.

### [get_audio_duration(gcs_audio_uri)](./app.py#L64)
- Calculates the duration of an audio file stored in GCS.
- Downloads the file temporarily and uses FFmpeg to extract its duration.
- Returns the duration in seconds.

### [transcribe_audio(gcs_audio_uri)](./app.py#L92)
- Converts audio files into text using Google Cloud Speech-to-Text API.
- Automatically selects short or long transcription methods based on the file duration.
- Updates a global variable `global_transcript` with the transcribed text.
- Supports MP3 and WAV file formats.

### [list_files_in_bucket()](./app.py#L129)
- Lists all files in the GCS bucket.
- Organizes files in a hierarchical view based on folders.

### [classify_transcript(transcript)](./app.py#L140)
- Uses Gemini AI to identify major areas discussed in a transcript.
- Generates classifications and categorizes each line into predefined areas.
- Returns a detailed classification result.

### [get_response(message, history)](./app.py#L173)
- Facilitates chat interactions using the assistant.
- Uses the transcript and chat history to construct responses.
- Leverages Gemini AI for natural language processing.

### [gradio_interface()](./app.py#L205)
- Builds the Gradio user interface.
- Defines tabs for each feature: upload, transcribe, classify, and chat.
- Launches the application.

---

## Notes
- Ensure all dependencies are installed and APIs are properly configured.
- Audio files longer than 60 seconds will automatically use the long-running recognition API.
- Only WAV and MP3 audio files are supported for transcription.

---

## Future Enhancements
- Add support for additional audio file formats.
- Implement multilingual transcription.
- Enhance the classification logic to include more granular categories.

---

## License
This project is licensed under the MIT License. See the LICENSE file for details.

