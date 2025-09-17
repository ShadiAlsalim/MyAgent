import os
import google.generativeai as genai
from dotenv import load_dotenv
import time # <-- ADD THIS LINE

# Load the environment variables from the .env file
load_dotenv()

# Configure the Gemini API with your key
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# Initialize the Generative Model
model = genai.GenerativeModel('gemini-1.5-pro-latest')

def ask_agent(question):
    """Sends a question to the AI agent and returns the response."""
    try:
        print("🤖 Agent is thinking...")
        response = model.generate_content(question)
        return response.text
    except Exception as e:
        return f"An error occurred: {e}"

# --- Main part of the script ---
if __name__ == "__main__":
    print("✅ Your AI Agent is ready. Type 'exit' to quit.")
    
    # This loop lets you chat with your agent
    while True:
        user_question = input("You: ")
        if user_question.lower() == 'exit':
            break
        
        agent_response = ask_agent(user_question)
        print(f"Agent: {agent_response}")
        
        time.sleep(1)