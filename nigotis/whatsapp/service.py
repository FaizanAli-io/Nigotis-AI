import os
import json
import requests

from django.http import HttpResponse, JsonResponse

from dotenv import load_dotenv

load_dotenv()

VERSION = os.getenv("VERSION")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")


class WhatsAppService:
    def __init__(self):
        pass

    def send_message(self, to, what):
        """Send a message to a specific chat."""
        url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"

        data = json.dumps(
            {
                "to": to,
                "type": "text",
                "recipient_type": "individual",
                "messaging_product": "whatsapp",
                "text": {"preview_url": False, "body": what},
            }
        )

        headers = {
            "Content-type": "application/json",
            "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
        }

        response = requests.post(url, data=data, headers=headers)

        if response.status_code == 200:
            print("Message sent successfully.")
        else:
            print("Failed to send message:", response.status_code, response.text)

        return response

    def receive_message(self, request):
        """Receive messages from the WhatsApp client."""
        if request.method == "GET":
            return HttpResponse(
                request.GET.get("hub.challenge", "Verification failed"),
                status=200 if "hub.challenge" in request.GET else 400,
            )

        if request.method != "POST":
            return HttpResponse("Method not allowed", status=405)

        try:
            data = json.loads(request.body)

            changes = (
                data.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {})
            )

            messages, contacts = changes.get("messages", []), changes.get(
                "contacts", []
            )

            if "statuses" in changes:
                return JsonResponse({"message": "Ignored status update"}, status=200)

            if not messages:
                return JsonResponse({"message": "Webhook processed"}, status=200)

            message = messages[0]
            message_type = message["type"]

            if message_type != "text":
                return JsonResponse({"message": f"Ignored {message_type}"}, status=200)

            sender_id, unique_message_id = message["from"], message["id"]
            incoming_text = message.get["text"]["body"].strip()
            print("Message Received:", incoming_text)

            if contacts:
                whatsapp_name = contacts[0]["profile"].get("name", "Unknown")
                print(f"Whatsapp User Name: {whatsapp_name}")

            return {
                "sender_id": sender_id,
                "incoming_text": incoming_text,
                "unique_message_id": unique_message_id,
            }

        except json.JSONDecodeError:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Invalid JSON format",
                },
                status=400,
            )
