import openai
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# --- 1. Configuration ---
# --- IMPORTANT: ADD THE EXACT NAMES OF CONTACTS OR GROUPS TO IGNORE ---
EXCLUDED_CONTACTS = [
    "My Boss",
    "Family Group",
    "Dr. Smith"
]

# --- 2. AI Brain (Connects to LM Studio) ---
client = openai.OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")

def ask_agent(messages_context):
    """Sends the full context of unread messages to the local AI model."""
    print(f"🤖 Agent is thinking about the context:\n{messages_context}")
    
    prompt = f"""
    Read the following series of messages from a single person and provide one, single, comprehensive reply that addresses all of their points.

    --- START OF MESSAGES ---
    {messages_context}
    --- END OF MESSAGES ---

    Your reply:
    """
    
    try:
        completion = client.chat.completions.create(
            model="local-model",
            messages=[
                {"role": "system", "content": "You are a helpful assistant responding to WhatsApp messages. Synthesize multiple messages into a single, coherent reply."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error communicating with local AI: {e}")
        return "Sorry, I'm having trouble thinking right now."

# --- 3. WhatsApp Automation ---
def main():
    print("🚀 Initializing WhatsApp Agent with Exclusion List...")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.get("https://web.whatsapp.com/")
    
    print("Please scan the QR code on the browser to log in to WhatsApp Web.")
    input("Press ENTER after you have successfully logged in.")

    print("✅ Login successful. Agent is now scanning for unread messages...")
    
    try:
        while True:
            unread_chat_xpath = "//span[contains(@class, 'l7jjieqr')]/../../../../.."
            
            try:
                unread_chats = driver.find_elements(By.XPATH, unread_chat_xpath)
                
                if unread_chats:
                    first_unread_chat = unread_chats[0]
                    
                    contact_name_element = first_unread_chat.find_element(By.XPATH, ".//span[@dir='auto' and @aria-label]")
                    contact_name = contact_name_element.get_attribute("title")
                    
                    # --- The New Exclusion Check ---
                    if contact_name in EXCLUDED_CONTACTS:
                        print(f"🤫 Ignoring unread message from excluded contact: '{contact_name}'")
                        # We use 'continue' to skip the rest of the loop and start over
                        time.sleep(5)
                        continue
                    
                    print(f"💬 Unread conversation detected from '{contact_name}'!")
                    first_unread_chat.click()
                    time.sleep(2)

                    all_chat_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'message-in')] | //div[contains(@class, '_1-F5z')]")
                    
                    start_reading = False
                    temp_unread_messages = []
                    for element in all_chat_elements:
                        if "UNREAD" in element.text.upper():
                            start_reading = True
                            temp_unread_messages = []
                            continue
                        if start_reading and 'message-in' in element.get_attribute("class"):
                            temp_unread_messages.append(element.text.strip())
                    
                    if not temp_unread_messages and driver.find_elements(By.CSS_SELECTOR, ".message-in"):
                        temp_unread_messages.append(driver.find_elements(By.CSS_SELECTOR, ".message-in")[-1].text.strip())

                    if temp_unread_messages:
                        unread_messages_text = "\n".join(temp_unread_messages)
                        
                        ai_reply = ask_agent(unread_messages_text)
                        
                        input_box = driver.find_element(By.XPATH, '//div[@title="Type a message"]')
                        input_box.send_keys(ai_reply)
                        input_box.send_keys(Keys.ENTER)
                        print(f"↪️ Agent replied to '{contact_name}': '{ai_reply}'")
                        time.sleep(2)
            except Exception:
                pass
                
            time.sleep(5)

    except KeyboardInterrupt:
        print("\n🛑 Shutting down agent.")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()