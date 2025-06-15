from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.messaging_response import MessagingResponse

from agent.agent import ToolAgent
from .service import WhatsAppService
from memory.manager import MemoryManager
from chatbot.models import Message, Session


# @csrf_exempt
# def webhook(request):
#     memory_manager = MemoryManager()
#     whatsapp_service = WhatsAppService()

#     input_payload = whatsapp_service.receive_message(request)

#     if isinstance(input_payload, (HttpResponse, JsonResponse)):
#         return input_payload

#     sender_id = input_payload["sender_id"]
#     incoming_text = input_payload["incoming_text"]
#     unique_message_id = input_payload["unique_message_id"]

#     already_exists = Message.objects.filter(
#         unique_message_id=unique_message_id
#     ).exists()

#     print(f"Message: {input_payload}")
#     print(f"Already exists: {already_exists}")

#     if already_exists:
#         return JsonResponse(
#             {
#                 "status": "success",
#                 "message": "message already exists",
#             },
#             status=200,
#         )

#     session, _ = Session.objects.get_or_create(phone_number=sender_id)

#     memory_manager.add_message(
#         sender="USER",
#         content=incoming_text,
#         session_id=session.id,
#         unique_message_id=unique_message_id,
#     )

#     agent = ToolAgent()

#     bot_response = agent.get_response(session, incoming_text)

#     whatsapp_service.send_message(to=sender_id, what=bot_response)

#     memory_manager.add_message(
#         sender="BOT",
#         content=bot_response,
#         session_id=session.id,
#     )

#     return JsonResponse(
#         {
#             "status": "success",
#             "message": "message sent",
#         },
#         status=200,
#     )


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
