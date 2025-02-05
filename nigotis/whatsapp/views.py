from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
import requests
from dotenv import load_dotenv

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

# Webhook view handling both GET (verification) and POST (processing)
@csrf_exempt
def webhook(request):
    if request.method == "GET":
        # Handle GET request for webhook verification
        challenge = request.GET.get("hub.challenge")
        if challenge:
            return HttpResponse(challenge, status=200)
        return HttpResponse("Verification failed", status=400)

    elif request.method == "POST":
        try:
            # Parse incoming webhook data
            data = json.loads(request.body)
            print("Incoming Webhook Data:", data)  # Debug log

            # Extract the sender's phone number and message text
            entry = data.get("entry", [])[0]
            changes = entry.get("changes", [])[0]
            messages = changes.get("value", {}).get("messages", [])
            if messages:
                sender_id = messages[0]["from"]  # WhatsApp ID of the sender
                print(sender_id)
                incoming_text = messages[0].get("text", {}).get("body", "")

                print(f"Message from {sender_id}: {incoming_text}")

                # Transform the incoming message to uppercase
                reply_text = incoming_text.upper()

                # Send the reply message
                message_data = get_text_message_input(recipient=sender_id, text=reply_text)
                send_message(message_data)

            return JsonResponse({"status": "success", "message": "Webhook received and processed"}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON format"}, status=400)

    # Return a 405 response for unsupported methods
    return HttpResponse("Method not allowed", status=405)
