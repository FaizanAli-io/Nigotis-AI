from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.messaging_response import MessagingResponse

from agent.agent import ToolAgent
from chatbot.models import Session
from memory.manager import MemoryManager


@csrf_exempt
def webhook(request):
    memory_manager = MemoryManager()

    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    sender_id = request.POST.get("From", "").replace("whatsapp:", "")
    incoming_text = request.POST.get("Body", "")

    session, _ = Session.objects.get_or_create(phone_number=sender_id)

    memory_manager.add_message(
        sender="USER",
        content=incoming_text,
        session_id=session.id,
    )

    bot_response = ToolAgent().get_response(session, incoming_text)

    memory_manager.add_message(
        sender="BOT",
        content=bot_response,
        session_id=session.id,
    )

    twiml_response = MessagingResponse()
    twiml_response.message(bot_response)

    return HttpResponse(
        str(twiml_response),
        content_type="application/xml",
    )
