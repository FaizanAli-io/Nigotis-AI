import json
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .services import get_text_message_input, send_message


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
                incoming_text = messages[0].get("text", {}).get("body", "")

                print(f"Message from {sender_id}: {incoming_text}")

                # Transform the incoming message to uppercase
                reply_text = incoming_text.upper()

                # Send the reply message
                message_data = get_text_message_input(
                    recipient=sender_id, text=reply_text
                )
                send_message(message_data)

            return JsonResponse(
                {"status": "success", "message": "Webhook received and processed"},
                status=200,
            )
        except json.JSONDecodeError:
            return JsonResponse(
                {"status": "error", "message": "Invalid JSON format"}, status=400
            )

    # Return a 405 response for unsupported methods
    return HttpResponse("Method not allowed", status=405)
