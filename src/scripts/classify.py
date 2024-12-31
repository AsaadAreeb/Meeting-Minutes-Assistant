
# import os
# import google.generativeai as genai

# # Replace with your actual Gemini API key
# os.environ["GEMINI_API_KEY"] = "" 

# def classify_transcript(transcript):
#     """
#     Classifies the transcript using the Gemini API.

#     Args:
#         transcript: The text of the meeting transcript.

#     Returns:
#         A tuple containing:
#             - A list of major classes identified in the transcript.
#             - A dictionary where keys are major classes and values are lists of 
#               transcript lines belonging to that class.
#     """

#     # Configure the Gemini API
#     genai.configure(api_key=os.environ["GEMINI_API_KEY"])
#     model = genai.GenerativeModel("gemini-1.5-flash")

#     # Prompt for identifying major classes
#     prompt1 = f"""
#     Read the following meeting transcript:

#     {transcript}

#     Based on the context, identify the major areas or tasks discussed. 
#     For example, if it's a software development meeting, 
#     identify areas like:
#         * Frontend development
#         * Backend development
#         * Database design
#         * Testing
#         * Deployment 

#     Return a concise, comma-separated list of these major areas.
#     """

#     response1 = model.generate_content(prompt1)
#     major_classes = response1.text.strip().split(",")

#     # Prompt for classifying transcript lines (revised)
#     prompt2 = f"""
#     Read the following meeting transcript:

#     {transcript}

#     Based on the context of the entire transcript, classify each line 
#     into one of the following major areas: 
#     {", ".join(major_classes)}

#     * **[Major Class 1]:** 
#         * [List of lines related to Major Class 1] 
#     * **[Major Class 2]:** 
#         * [List of lines related to Major Class 2]
#         * ...
#     * **[Other]:** 
#         * [List of lines that do not clearly belong to any major class]

#     **Important:** 
#     - Consider the overall context of the meeting when classifying lines. 
#     - A line may be classified under multiple major classes if it 
#       relates to them.
#     - Maintain the original line breaks and formatting from the transcript.
#     """

#     response2 = model.generate_content(prompt2)

#     classified_transcript = {}
#     for line in response2.text.strip().splitlines():
#         if line.startswith("* "):
#             class_name = line[2:].split(":")[0].strip()
#             classified_transcript[class_name] = []
#         else:
#             classified_transcript[class_name].append(line.strip())

#     return major_classes, classified_transcript

# def classify_transcript_from_file(file_path):
#     """
#     Reads the transcript from a file and classifies it.

#     Args:
#         file_path: Path to the transcript file.

#     Returns:
#         A tuple containing:
#             - A list of major classes identified in the transcript.
#             - A dictionary where keys are major classes and values are lists of 
#               transcript lines belonging to that class.
#     """
#     with open(file_path, 'r') as f:
#         transcript = f.read()

#     return classify_transcript(transcript)

# def save_classified_transcript(classified_transcript, output_file="classified_transcript.txt"):
#     """
#     Saves the classified transcript to a file.

#     Args:
#         classified_transcript: A dictionary containing the classified transcript.
#         output_file: The name of the output file.
#     """
#     with open(output_file, 'w') as f:
#         for cls, lines in classified_transcript.items():
#             f.write(f"**{cls}:**\n")
#             for line in lines:
#                 f.write(f"- {line}\n")
#             f.write("\n")

# # Example usage:
# file_path = "job_interview.txt" 
# major_classes, classified_transcript = classify_transcript_from_file(file_path)

# save_classified_transcript(classified_transcript)

# print("Major Classes:", major_classes)
# print("\nClassified Transcript saved to classified_transcript.txt")



import os
import google.generativeai as genai

# Replace with your actual Gemini API key
os.environ["GEMINI_API_KEY"] = "" 

def classify_transcript(transcript):
    """
    Classifies the transcript using the Gemini API.

    Args:
        transcript: The text of the meeting transcript.

    Returns:
        A tuple containing:
            - A list of major classes identified in the transcript.
            - A dictionary where keys are major classes and values are lists of 
              transcript lines belonging to that class.
    """

    # Configure the Gemini API
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")

    # Prompt for identifying major classes
    prompt1 = f"""
    Read the following meeting transcript:

    {transcript}

    Based on the context, identify the major areas or tasks discussed. 
    For example, if it's a software development meeting, 
    identify areas like:
        * Frontend development
        * Backend development
        * Database design
        * Testing
        * Deployment 

    Return a concise, comma-separated list of these major areas.
    """

    response1 = model.generate_content(prompt1)
    major_classes = response1.text.strip().split(",")

    # Prompt for classifying transcript lines (revised)
    prompt2 = f"""
    Read the following meeting transcript:

    {transcript}

    Based on the context of the entire transcript, classify each line 
    into one of the following major areas: 
    {", ".join(major_classes)}

    * **[Major Class 1]:** 
        * [List of lines related to Major Class 1] 
    * **[Major Class 2]:** 
        * [List of lines related to Major Class 2]
        * ...
    * **[Other]:** 
        * [List of lines that do not clearly belong to any major class]

    **Important:** 
    - Consider the overall context of the meeting when classifying lines. 
    - A line may be classified under multiple major classes if it 
      relates to them.
    - Maintain the original line breaks and formatting from the transcript.
    """

    response2 = model.generate_content(prompt2)

    classified_transcript = {}
    for line in response2.text.strip().splitlines():
        if line.startswith("* "):
            class_name = line[2:].split(":")[0].strip()
            classified_transcript[class_name] = []
        else:
            classified_transcript[class_name].append(line.strip())

    return major_classes, classified_transcript

def classify_transcript_from_file(file_path):
    """
    Reads the transcript from a file and classifies it.

    Args:
        file_path: Path to the transcript file.

    Returns:
        A tuple containing:
            - A list of major classes identified in the transcript.
            - A dictionary where keys are major classes and values are lists of 
              transcript lines belonging to that class.
    """
    with open(file_path, 'r') as f:
        transcript = f.read()

    return classify_transcript(transcript)

def save_classified_transcript(classified_transcript, output_file):
    """
    Saves the classified transcript to a file.

    Args:
        classified_transcript: A dictionary containing the classified transcript.
        output_file: The path of the output file.
    """
    with open(output_file, 'w') as f:
        for cls, lines in classified_transcript.items():
            f.write(f"**{cls}:**\n")
            for line in lines:
                f.write(f"- {line}\n")
            f.write("\n")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Classify a meeting transcript using the Gemini API.")
    parser.add_argument("file_path", help="Path to the transcript file.")
    parser.add_argument("output_file", help="Path to save the classified transcript.")

    args = parser.parse_args()

    # Process the transcript and classify it
    major_classes, classified_transcript = classify_transcript_from_file(args.file_path)

    # Save the classified transcript
    save_classified_transcript(classified_transcript, args.output_file)

    print("Major Classes:", major_classes)
    print(f"\nClassified Transcript saved to {args.output_file}")
