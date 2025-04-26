import json

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from chatbot.models import Message, Session, Client

from .bot import get_bot_response

from .service import WhatsAppService


@csrf_exempt
def webhook(request):
    whatsapp_service = WhatsAppService()

    input_payload = whatsapp_service.receive_message(request)

    if isinstance(input_payload, (HttpResponse, JsonResponse)):
        return input_payload

    print("Input Payload:", input_payload)

    session, _ = Session.objects.get_or_create(phone_number=input_payload["sender_id"])

    bot_response = get_bot_response(session, input_payload["incoming_text"])

    whatsapp_service.send_message(
        input_payload["sender_id"],
        bot_response["output"],
    )

    return JsonResponse(
        {
            "status": "success",
            "message": "message sent",
        },
        status=200,
    )
