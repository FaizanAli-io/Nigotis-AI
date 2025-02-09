import os
import json
import requests
from dotenv import load_dotenv

# from chatbot.bot.pipeline import Pipeline
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


# Function to create an interactive list message
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


# Function to send a message via WhatsApp API
def send_message(data):
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}",
    }
    url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"

    response = requests.post(url, data=data, headers=headers)
    response_json = response.json()  # Parse JSON response

    if response.status_code == 200:
        print("Message sent successfully.")
        print("Response:", response_json)  # Print the response data
    else:
        print("Failed to send message:", response.status_code, response.text)

    return response_json


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
