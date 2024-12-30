import google.generativeai as genai
import gradio as gr
import os

# Configure Gemini API
GOOGLE_API_KEY = 'AIzaSyAjmcfNMGCSI19icee7X_1-2gMrZMmEq8M'  # Replace with your actual API key
genai.configure(api_key=GOOGLE_API_KEY)

# Read meeting minutes
try:
    with open('transcript.txt', 'r') as file:
        context = file.read()
except FileNotFoundError:
    context = "Meeting minutes are unavailable. Please upload the transcript.txt file."

def get_response(message, history):
    """
    Generates a response to the user's question using Gemini API.

    Args:
        message: The user's question.
        history: The chat history.

    Returns:
        The generated response from the Gemini model.
    """
    try:
        # Construct prompt with context and previous chat history
        full_history = "\n".join([f"User: {h['content']}\nAssistant: {h['content']}" for h in history if 'content' in h])
        prompt = f"""
        The following are the minutes of a meeting:
        {context}

        Previous Conversation:
        {full_history}

        Current Question:
        {message}

        Please provide a concise and accurate response based on the context of the meeting minutes and the conversation so far.
        """

        print("Prompt sent to Gemini:", prompt)  # Debugging: Print the prompt

        # Generate response using Gemini's text generation model
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        
        # Check the response and extract the text content properly
        print("Response from Gemini:", response)  # Debugging: Print the response

        # Access the response using the appropriate method or attribute
        if response and hasattr(response, 'candidates') and len(response.candidates) > 0:
            generated_text = response.candidates[0].content.parts[0].text.strip()
            print("Generated Text:", generated_text)
        else:
            generated_text = "Sorry, I couldn't generate a response."

        # Prepare the response in the format expected by Gradio
        assistant_message = {
            "role": "assistant",
            "content": generated_text,
            "files": []  # Empty list for files, if no files are involved
        }

        # Return the assistant message as a dictionary (not as a list)
        return assistant_message  # Return the dictionary directly

    except Exception as e:
        print(f"Error: {e}")  # Debugging: Print the error
        return {"role": "assistant", "content": f"An error occurred: {str(e)}", "files": []}

# Create Gradio interface
iface = gr.ChatInterface(
    fn=get_response,
    type="messages",  # Specify messages format
    title="Meeting Minutes Assistant",
    description="Ask questions about the meeting minutes and get contextual responses.",
    theme="soft",
    examples=[
        [{"role": "user", "content": "What were the main topics discussed?"}],
        [{"role": "user", "content": "What action items were assigned?"}],
        [{"role": "user", "content": "When is the next meeting scheduled?"}],
        [{"role": "user", "content": "Who is responsible for [specific task]?"}]
    ]
)

# Launch the interface
if __name__ == "__main__":
    iface.launch(share=True)
