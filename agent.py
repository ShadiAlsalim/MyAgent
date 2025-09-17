import os
import requests
from dotenv import load_dotenv
import time

# Load the environment variables from the .env file
load_dotenv()

# Get your Hugging Face API token
api_token = os.getenv("HUGGINGFACE_API_TOKEN")

# This is the API URL for a powerful, multilingual model (Llama 3 8B)
# You can swap this with other models from the Hugging Face Hub
API_URL = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"

# Set up the headers for the API request
headers = {"Authorization": f"Bearer {api_token}"}

def ask_agent(question):
    """Sends a question to the Hugging Face API and returns the response."""
    try:
        print("🤖 Agent is thinking...")

        # This is the data we send to the model
        payload = {
            "inputs": question,
            "parameters": { # Optional: Adjust these for different results
                "max_new_tokens": 512,
                "temperature": 0.7,
                "return_full_text": False
            }
        }

        # Send the request to the API
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status() # This will raise an error for bad responses (4xx or 5xx)

        # The response is a list, we take the first item's generated text
        result = response.json()
        return result[0]['generated_text']

    except requests.exceptions.RequestException as e:
        # Handle potential connection errors
        return f"A network error occurred: {e}"
    except Exception as e:
        # Handle other errors, like a model loading for the first time
        # The first request to a model can take ~20 seconds to load.
        return f"An error occurred: {e}. If this is the first request, the model might be loading. Please try again in a moment."

# --- Main part of the script ---
if __name__ == "__main__":
    print("✅ Your AI Agent (powered by Hugging Face) is ready. Type 'exit' to quit.")

    while True:
        user_question = input("You: ")
        if user_question.lower() == 'exit':
            break

        agent_response = ask_agent(user_question)
        print(f"Agent: {agent_response}")

        time.sleep(1)