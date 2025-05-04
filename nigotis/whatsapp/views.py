from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from agent.agent import ToolAgent
from memory.manager import MemoryManager
from chatbot.models import Message, Session

from .service import WhatsAppService

memory_manager = MemoryManager()


@csrf_exempt
def webhook(request):
    whatsapp_service = WhatsAppService()

    input_payload = whatsapp_service.receive_message(request)

    if isinstance(input_payload, (HttpResponse, JsonResponse)):
        return input_payload

    sender_id = input_payload["sender_id"]
    incoming_text = input_payload["incoming_text"]
    unique_message_id = input_payload["unique_message_id"]

    already_exists = Message.objects.filter(
        unique_message_id=unique_message_id
    ).exists()

    print(f"Message: {input_payload} already exists: {already_exists}")

    if already_exists:
        return JsonResponse(
            {
                "status": "success",
                "message": "message already exists",
            },
            status=200,
        )

    session, _ = Session.objects.get_or_create(phone_number=sender_id)

    memory_manager.add_message(
        session_id=session.id,
        sender="USER",
        content=incoming_text,
        unique_message_id=unique_message_id,
    )

    agent = ToolAgent()

    bot_response = agent.get_response(session, incoming_text)

    whatsapp_service.send_message(to=sender_id, what=bot_response)

    memory_manager.add_message(
        session_id=session.id,
        sender="BOT",
        content=bot_response,
    )

    return JsonResponse(
        {
            "status": "success",
            "message": "message sent",
        },
        status=200,
    )
