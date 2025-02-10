import os
import json
import time
import random
import schedule
import requests
import threading
from dotenv import load_dotenv
from rest_framework import status
from django.utils.timezone import now
from chatbot.models import ChatMessage, ChatSession

from llama_index.core.llms import ChatMessage as ChatMessageModel, MessageRole
from llama_index.core.memory import ChatSummaryMemoryBuffer
from llama_index.llms.openai import OpenAI as OpenAiLlm
import tiktoken

# Load environment variables
load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERSION = os.getenv("VERSION")


# Function to create a text message input for WhatsApp
def get_text_message_input(recipient, text):
    return json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {"preview_url": False, "body": text},
        }
    )


# Function to send a message via WhatsApp API
def send_message(data):
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}",
    }
    url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"
    response = requests.post(url, data=data, headers=headers)
    if response.status_code == 200:
        print("Message sent successfully.")
        return response
    else:
        print("Failed to send message:", response.status_code, response.text)
        return response


def authenticate_user(email, password, sender_id):
    try:
        response = requests.post(
            "https://nigotis-be.vercel.app/api/v1/user/login",
            json={"email": email, "password": password},
        )

        response_data = response.json()

        if response.status_code != 200 or not response_data.get("success"):
            return "Authentication failed"

        # Extract user data from response
        data = response_data.get("data", {})

        # Store user session in the database
        session = ChatSession.objects.filter(phone_number=sender_id).first()
        if session:
            # Update the existing session
            session.name = f"{data['personalInfo']['firstName']} {data['personalInfo'].get('lastName', '')}"
            session.role = data["role"].upper()
            session.login_email = email
            session.login_password = password  # Consider hashing the password if stored
            session.auth_token = data["token"]
            session.authenticated_at = now()
            session.save()
            return welcome_login_message(session.name)
    except:
        return "Request not Processed"


def get_interactive_list_message(recipient):
    return json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "header": {"type": "text", "text": "Select an Analysis"},
                "body": {"text": "Choose an analysis to run:"},
                "action": {
                    "button": "Select Analysis",
                    "sections": [
                        {
                            "title": "Analysis Options",
                            "rows": [
                                {
                                    "id": "SEG",
                                    "title": "Customer Segmentation",
                                    "description": "Segment customers based on behavior",
                                },
                                {
                                    "id": "PRF",
                                    "title": "Product Preference",
                                    "description": "Analyze product popularity",
                                },
                                {
                                    "id": "REV",
                                    "title": "Revenue Insights",
                                    "description": "Get revenue breakdown",
                                },
                                {
                                    "id": "PUR",
                                    "title": "Purchase Value",
                                    "description": "Analyze purchase patterns",
                                },
                                {
                                    "id": "TRE",
                                    "title": "Seasonal Trends",
                                    "description": "Identify seasonal buying trends",
                                },
                                {
                                    "id": "CLV",
                                    "title": "Customer Lifetime Value",
                                    "description": "Estimate CLV of customers",
                                },
                                {
                                    "id": "CHP",
                                    "title": "Churn Prediction",
                                    "description": "Predict customer churn",
                                },
                                {
                                    "id": "MPP",
                                    "title": "Most Purchased Products",
                                    "description": "Find most bought items",
                                },
                                {
                                    "id": "TPR",
                                    "title": "Tailored Promotions",
                                    "description": "Optimize promotions for users",
                                },
                            ],
                        }
                    ],
                },
            },
        }
    )
def get_login_detail_message():
    template = """
    🔒 Login Required 🔒
    
    Please provide your login details:
    - Email: [Your Email Address]
    - Password: [Your Password]

    Example:
    ```
    Email: example@example.com
    Password: ********
    ```
    
    Ensure that your credentials are correct to proceed.
    """
    return template


def welcome_login_message(name):

    response_message = f"""
✅ Login Successful! Welcome to Nigotis-AI, {name}. 🚀

You can now:
- Use *#options* to view and run available analysis options.
- Use *#logout* to securely log out of your session.

Let me know how I can assist you!
"""
    return response_message


def get_logout_message():
    response_message = """👋 Goodbye, 

You have successfully logged out of your session. 🛡️

If you need further assistance, feel free to log in again anytime.

Use *#login* to log back into your account.

Stay safe and have a great day! 🚀"""
    return response_message


def send_greeting_message():
    """Send a scheduled message to all authenticated clients at 9 AM."""
    messages = [
    "🌟 Wishing you a fantastic and productive day ahead! Stay positive and keep moving forward. I'm available if you need any help.",
    "✨ Hope today brings you success, happiness, and new opportunities! Let me know if there's anything I can assist you with.",
    "💡 Stay motivated and keep pushing towards your goals—great things are coming your way! I'm here if you need any support.",
    "🚀 A fresh day, a fresh start! Make the most of every moment. If you need any help, feel free to reach out.",
    "🌼 Sending you good vibes and positivity—may your day be amazing! Let me know if you need any assistance.",
    "🔥 Believe in yourself and make today count! You’ve got this. And if you need help, I'm just a message away.",
    "💪 Every new day is a chance to grow, learn, and shine. Keep going! If there's anything I can do for you, just let me know.",
    "🌈 Stay inspired, stay focused, and make the most of today! If you ever need support, I’m here to help.",
    "🌍 Wherever you are, whatever you're doing—wishing you success and happiness. And remember, I'm always here if you need assistance.",
    "🎯 Take on the day with confidence and energy. Great things await you! If you need anything, don’t hesitate to ask."
    ]
    message = random.choice(messages)
    
    # Get all authenticated clients
    authenticated_clients = ChatSession.objects.filter(auth_token__isnull=False).values_list("phone_number", flat=True)

    if not authenticated_clients:
        print("⚠️ No authenticated clients found.")
        return

    print(f"📢 Sending messages to {len(authenticated_clients)} authenticated clients...")

    for client in authenticated_clients:
      #  number = "923312844594"
        data = get_text_message_input(client, message)
        send_message(data)
        time.sleep(1)  # Delay to prevent hitting API limits

def scheduled_task():
    """Runs the scheduler to send messages daily at 9 AM."""
    schedule.every().day.at("15:10").do(send_greeting_message)
    print("✅ Scheduler started: Waiting for 9 AM to send messages...")

    while True:
        schedule.run_pending()
        time.sleep(30)  # Check every 30 seconds

def run_scheduler():
    """Runs the scheduler in a separate background thread."""
    scheduler_thread = threading.Thread(target=scheduled_task, daemon=True)
    scheduler_thread.start()
    print("🟢 Background scheduler thread started.")


def get_chat_history(phone_number):
    try:

        session = ChatSession.objects.get(phone_number=phone_number)
        
        messages = ChatMessage.objects.filter(session=session).order_by('-created_at')[:10]
        
        messages = list(messages)[::-1]
        chat_history = [
            ChatMessageModel(
                role=MessageRole.USER if msg.sender == "USER" else MessageRole.ASSISTANT,
                content=msg.content
            )
            for msg in messages
        ]
        print(chat_history)
        os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
        model = "gpt-4o-mini"
        summarizer_llm = OpenAiLlm(model_name=model, max_tokens=256)
        tokenizer_fn = tiktoken.encoding_for_model(model).encode
        memory = ChatSummaryMemoryBuffer.from_defaults(
            chat_history=chat_history,
            llm=summarizer_llm,
            token_limit=50,
            tokenizer_fn=tokenizer_fn,
        )

        history = memory.get()
        formatted_history = "\n".join(
        [f"{msg.role.value.capitalize()}: {msg.content}" for msg in history]
    )
        print(formatted_history)

        return formatted_history
        #print("Chat history\n")
        #print(history)
       # return chat_history

    except Exception as e:
        print(f"Error retrieving chat history: {e}")
        return []