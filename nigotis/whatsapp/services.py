import os
import json
import requests
from dotenv import load_dotenv
from rest_framework import status
from django.utils.timezone import now
from .test2 import welcome_login_message

from chatbot.models import ChatMessage, ChatSession

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
