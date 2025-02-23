import requests
import base64

def call_ollama(api_url="http://localhost:11434/api/generate", model="llama3", 
                system_prompt="", history=None, user_prompt="", image_path=None):
    """
    Calls a local instance of Ollama with history, system prompt, user input, and an optional image.
    
    Args:
        api_url (str): The URL of the local Ollama instance.
        model (str): The model to use (e.g., 'llama3', 'mistral').
        system_prompt (str): The system prompt guiding the AI.
        history (list): List of past messages in format [{'role': 'user', 'content': '...'}, {'role': 'assistant', 'content': '...'}].
        user_prompt (str): The user's input.
        image_path (str, optional): Path to an image file to include.

    Returns:
        str: The AI's response.
    """
    if history is None:
        history = []

    # Format history into a conversation string
    formatted_history = "\n".join(f"{m['role'].capitalize()}: {m['content']}" for m in history)

    # Start building the full prompt
    full_prompt = f"System: {system_prompt}\n{formatted_history}\nUser: {user_prompt}\nAssistant:"

    # Prepare the payload
    payload = {
        "model": model,
        "prompt": full_prompt,
        "stream": False
    }

    # If an image is provided, encode it as Base64 and add it
    if image_path:
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")
        payload["images"] = [base64_image]  # 'images' key is used for image input

    # Send request to Ollama
    response = requests.post(api_url, json=payload)

    if response.status_code == 200:
        return response.json().get("response", "No response received")
    else:
        return f"Error: {response.status_code}, {response.text}"

# # Example usage
# history = [
#     {"role": "user", "content": "Hello, who are you?"},
#     {"role": "assistant", "content": "I am an AI assistant created to help you!"}
# ]

# response = call_ollama(
#     model="llama3.2",
#     system_prompt="You are a friendly AI assistant.",
#     history=history,
#     user_prompt="How are you today",
#     image_path="example.jpg"  # Change to a valid image file
# )

# print(response)