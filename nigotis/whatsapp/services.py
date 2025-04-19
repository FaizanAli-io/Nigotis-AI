import re
import os
import json
import time
import random
import requests
import schedule
import requests
import threading
from dotenv import load_dotenv
from django.utils.timezone import now
from chatbot.models import Message, Client, Session

from llama_index.llms.openai import OpenAI as OpenAiLlm
from llama_index.core.memory import ChatSummaryMemoryBuffer
from llama_index.core.llms import ChatMessage as MessageModel, MessageRole
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
        print("Authenticating User")
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
        # session = Client.objects.filter(phone_number=sender_id).first()
        client_name = f"{data['personalInfo']['firstName']} {data['personalInfo'].get('lastName', '')}"
        client = Client.objects.create(  # Store the created Client instance
            name=client_name,
            role=data["role"].upper(),
            login_email=email,
            login_password=password,  # Consider hashing the password if stored
            auth_token=data["token"],
            authenticated_at=now(),
        )
        print(f"Client ID : {client.id}")
        Session.objects.create(phone_number=sender_id, website=False, client=client)

        return welcome_login_message(client_name)

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
    
    Email: example@example.com
    Password: ********
    
    
    Ensure that your credentials are correct to proceed.
    """
    return template


def welcome_login_message(name):

    response_message = f"""
✅ Login Successful! Welcome to Nigotis-AI, {name}. 🚀

You can now:
- Use #options to view and run available analysis options.
- Use #logout to securely log out of your session.
- Use #createinvoice to create invoices.

Let me know how I can assist you!
"""
    return response_message


def get_logout_message():
    response_message = """👋 Goodbye, 

You have successfully logged out of your session. 🛡

If you need further assistance, feel free to log in again anytime.

Use #login to log back into your account.

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
        "🔥 Believe in yourself and make today count! You've got this. And if you need help, I'm just a message away.",
        "💪 Every new day is a chance to grow, learn, and shine. Keep going! If there's anything I can do for you, just let me know.",
        "🌈 Stay inspired, stay focused, and make the most of today! If you ever need support, I'm here to help.",
        "🌍 Wherever you are, whatever you're doing—wishing you success and happiness. And remember, I'm always here if you need assistance.",
        "🎯 Take on the day with confidence and energy. Great things await you! If you need anything, don't hesitate to ask.",
    ]
    message = random.choice(messages)

    # Get all authenticated clients
    authenticated_clients = Client.objects.filter(auth_token__isnull=False).values_list(
        "phone_number", flat=True
    )

    if not authenticated_clients:
        print("⚠ No authenticated clients found.")
        return

    print(
        f"📢 Sending messages to {len(authenticated_clients)} authenticated clients..."
    )

    for client in authenticated_clients:
        data = get_text_message_input(client, message)
        send_message(data)
        time.sleep(1)


def scheduled_task():
    """Runs the scheduler to send messages daily at 9 AM."""
    schedule.every().day.at("15:10").do(send_greeting_message)
    print("✅ Scheduler started: Waiting for 9 AM to send messages...")

    while True:
        schedule.run_pending()
        time.sleep(60)


def run_scheduler():
    """Runs the scheduler in a separate background thread."""
    scheduler_thread = threading.Thread(target=scheduled_task, daemon=True)
    scheduler_thread.start()
    print("🟢 Background scheduler thread started.")


def old_get_chat_history(phone_number):
    try:

        session = Session.objects.get(phone_number=phone_number)

        messages = Message.objects.filter(session=session).order_by("-created_at")[:10]

        messages = list(messages)[::-1]
        chat_history = [
            MessageModel(
                role=(
                    MessageRole.USER if msg.sender == "USER" else MessageRole.ASSISTANT
                ),
                content=msg.content,
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
        print("Conversational History:")
        print(formatted_history)

        return formatted_history

    except Exception as e:
        print(f"Error retrieving chat history: {e}")
        return []


def get_chat_history(phone_number):
    try:

        session = Session.objects.get(phone_number=phone_number)

        user_messages = Message.objects.filter(session=session, sender="USER").order_by(
            "-created_at"
        )[:5]

        user_messages = list(user_messages)[::-1]
        history = "\n".join([f"USER: {msg.content}" for msg in user_messages])
        print("Conversational History:")
        print(history)
        return history

    except Session.DoesNotExist:
        print(f"No session found for phone number: {phone_number}")
        return ""

    except Exception as e:
        print(f"Error retrieving chat history: {e}")
        return ""


def get_client_list(AUTH_TOKEN):
    try:

        # Fetch client list from the API
        headers = {
            "Authorization": f"Bearer {AUTH_TOKEN}",
            "Content-Type": "application/json",
        }

        # Fetch client list from API with headers
        response = requests.get(
            "https://nigotis-be.vercel.app/api/v1/client",
            headers=headers,
        )

        data = response.json()

        # Check if API returned success
        if data.get("success") and "data" in data:
            clients = data["data"]

            client_selection_map = {}  # Reset previous mappings
            client_list_message = "📜 *Available Clients:*\n"

            for index, client in enumerate(clients, start=1):
                client_id = client["_id"]
                first_name = client["personalInfo"]["firstName"]
                last_name = client["personalInfo"]["lastName"]

                # Map number to client ID
                client_selection_map[str(index)] = client_id

                # Format message
                client_list_message += f"{index}. 👤 {first_name} {last_name}\n"

            return client_list_message
        else:
            return "⚠ Unable to fetch clients. Please try again later."

    except Exception as e:
        print(f"Error fetching clients: {e}")
        return "⚠ An error occurred while fetching client data."


def get_product_list(AUTH_TOKEN):
    try:
        # Set headers with Authorization token
        headers = {
            "Authorization": f"Bearer {AUTH_TOKEN}",
            "Content-Type": "application/json",
        }

        # Fetch product list from API
        response = requests.get(
            "https://nigotis-be.vercel.app/api/v1/product", headers=headers
        )
        data = response.json()

        # Check if API returned success
        if data.get("success") and "data" in data:
            products = data["data"]

            product_selection_map = {}  # Reset previous mappings
            product_list_message = "🛒 *Available Products:*\n"

            for index, product in enumerate(products, start=1):
                product_id = product["_id"]
                name = product["name"]
                price = product["price"]

                # Map number to product ID
                product_selection_map[str(index)] = product_id

                # Format message
                product_list_message += f"{index}. 🛍 *{name}*\n💲 Price: ${price}\n\n"

            return product_list_message

        else:
            return "⚠ Unable to fetch products. Please try again later."

    except Exception as e:
        print(f"Error fetching products: {e}")
        return "⚠ An error occurred while fetching product data."


def get_invoice_creation_prompt():
    return """
📝 *Invoice Creation Instructions*
You are about to create an invoice. Please follow the format sent to you in next message.

1️⃣ *Choose a client number (from the list sent earlier).*
2️⃣ *Select products & quantities (from the product list).*
3️⃣ *Copy & edit the template in the next message.*

📩 *Once edited, send the formatted invoice back!*
"""


def get_invoice_template():
    return """
Create Invoice

Client: 2
Issue Date: 2025-03-01
Due Date: 2025-03-10
Status: pending
Discount: 15
Amount: 100
Tax: 8

Items:
Product: 5, Quantity: 3
Product: 7, Quantity: 1
Product: 9, Quantity: 4
"""


def product_selection_map(product_number, AUTH_TOKEN):
    try:
        headers = {
            "Authorization": f"Bearer {AUTH_TOKEN}",
            "Content-Type": "application/json",
        }

        # Fetch product list from API
        response = requests.get(
            "https://nigotis-be.vercel.app/api/v1/product", headers=headers
        )
        data = response.json()

        if data.get("success") and "data" in data:
            products = data["data"]

            for index, product in enumerate(products, start=1):
                if str(index) == str(
                    product_number
                ):  # Stop loop when matching product_number
                    return product["_id"]  # Return product ID immediately

            return None  # If product_number not found

        else:
            return None  # API error case

    except Exception as e:
        print(f"Error fetching products: {e}")
        return None  # Handle errors gracefully


def client_selection_map(client_number, AUTH_TOKEN):
    try:
        headers = {
            "Authorization": f"Bearer {AUTH_TOKEN}",
            "Content-Type": "application/json",
        }

        # Fetch client list from API with headers
        response = requests.get(
            "https://nigotis-be.vercel.app/api/v1/client", headers=headers
        )

        data = response.json()

        if data.get("success") and "data" in data:
            clients = data["data"]

            for index, client in enumerate(clients, start=1):
                if str(index) == str(
                    client_number
                ):  # Stop loop when matching client_number
                    return client["_id"]  # Return client ID immediately

            return None
        else:
            return None

    except Exception as e:
        print(f"Error fetching clients: {e}")
        return "⚠ An error occurred while fetching client data."


def parse_and_post_invoice(message, AUTH_TOKEN):
    try:
        message = str(message)
        if not message.startswith("create invoice"):
            return "⚠ Invalid format. Please ensure your message starts with 'create invoice'."

        client_number = re.search(r"client:\s*(\d+)", message).group(1)
        issue_date = re.search(r"issue date:\s*(\S+)", message).group(1)
        due_date = re.search(r"due date:\s*(\S+)", message).group(1)
        status = re.search(r"status:\s*(\S+)", message).group(1)
        discount = int(re.search(r"discount:\s*(\d+)", message).group(1))
        paid_amount = int(re.search(r"amount:\s*(\d+)", message).group(1))
        tax = int(re.search(r"tax:\s*(\d+)", message).group(1))

        client_id = client_selection_map(client_number, AUTH_TOKEN)
        if not client_id:
            return "⚠ Invalid Client ID. Please check your selection."

        items = []
        item_matches = re.findall(r"product:\s*(\d+),\s*quantity:\s*(\d+)", message)
        for item in item_matches:
            product_number, quantity = item
            product_id = product_selection_map(product_number, AUTH_TOKEN)
            if product_id:
                items.append({"productId": product_id, "quantity": int(quantity)})

        invoice_data = {
            "clientId": client_id,
            "issueDate": issue_date,
            "dueDate": due_date,
            "status": status,
            "tax": tax,
            "discount": discount,
            "paidAmount": paid_amount,
            "items": items,
        }

        invoice_json = json.dumps(invoice_data, indent=4)
        headers = {
            "Authorization": f"Bearer {AUTH_TOKEN}",
            "Content-Type": "application/json",
        }
        response = requests.post(
            "https://nigotis-be.vercel.app/api/v1/client/invoice",
            headers=headers,
            data=invoice_json,
        )

        return (
            "✅ Invoice Created Successfully!"
            if response.status_code == 201
            else f"⚠ Error creating invoice. Server responded with: {response.status_code} - {response.text}"
        )

    except Exception as e:
        return f"⚠ Error parsing invoice data: {e}"
