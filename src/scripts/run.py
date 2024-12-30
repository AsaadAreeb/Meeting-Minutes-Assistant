import os
import subprocess

def run_gradio_recorder():
    """
    Runs the gradio recorder script (gradio_script.py) to record and upload audio.
    """
    try:
        print("Launching the audio recorder interface...")
        subprocess.run(["python", "gradio_script.py"])
    except Exception as e:
        print(f"Error launching recorder: {e}")


def run_transcriber():
    """
    Runs the gradio transcriber script (transcribe.py) to transcribe existing audio files.
    """
    try:
        print("Launching the transcriber interface...")
        subprocess.run(["python", "transcribe.py"])
    except Exception as e:
        print(f"Error launching transcriber: {e}")

def run_classifier(file_path, output_file):
    """
    Runs the gemini api script (classify.py) to classify the transcript text.

    Args:
        file_path: Path to the transcript file.
        output_file: Path to save the classified transcript.
    """
    try:
        print("Running Gemini API...")
        subprocess.run(["python", "classify.py", file_path, output_file])
    except Exception as e:
        print(f"Error launching classifier: {e}")


def main():
    """
    Main menu for selecting between recording audio, transcribing audio, or classifying the transcript.
    """
    while True:
        print("\nSelect an option:")
        print("1. Record audio and upload to Google Cloud Storage")
        print("2. Transcribe audio from Google Cloud Storage")
        print("3. Run Gemini to classify the transcript.")
        print("4. Exit")

        choice = input("Enter your choice (1/2/3/4): ")

        if choice == "1":
            run_gradio_recorder()
        elif choice == "2":
            run_transcriber()
        elif choice == "3":
            file_path = input("Enter the path to the transcript file: ")
            output_file = input("Enter the path to save the classified transcript: ")
            run_classifier(file_path, output_file)
        elif choice == "4":
            print("Exiting the program. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    main()