import re
import json
import threading
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from chatbot.bot.pipeline import Pipeline
from chatbot.models import Message, Session, Client

from .old_services import (
    send_message,
    authenticate_user,
    welcome_login_message,
    get_text_message_input,
    get_interactive_list_message,
    get_login_detail_message,
    get_logout_message,
    get_chat_history,
    run_scheduler,
    get_client_list,
    get_product_list,
    get_invoice_creation_prompt,
    get_invoice_template,
    parse_and_post_invoice,
)


def extract_email_password(text):
    email_match = re.search(r"Email:\s*(\S+@\S+)", text, re.IGNORECASE)
    password_match = re.search(r"Password:\s*(\S+)", text, re.IGNORECASE)
    return email_match.group(1).strip() if email_match else None, (
        password_match.group(1).strip() if password_match else None
    )


def handle_login(sender_id, email, password):
    client = Client.objects.filter(login_email=email, login_password=password).first()
    if client:
        session, _ = Session.objects.get_or_create(
            phone_number=sender_id, defaults={"website": False, "client": client}
        )
        session.client = client
        session.save()
        send_message(
            get_text_message_input(sender_id, welcome_login_message(client.name))
        )
        return JsonResponse(
            {"status": "success", "message": "Login successful"}, status=200
        )
    send_message(
        get_text_message_input(sender_id, authenticate_user(email, password, sender_id))
    )
    return JsonResponse(
        {"status": "success", "message": "Login attempt processed"}, status=200
    )


def process_message(sender_id, unique_message_id, incoming_text, session, auth_token):
    if Message.objects.filter(unique_message_id=unique_message_id).exists():
        return JsonResponse({"status": "duplicate message ignored"}, status=200)
    Message.objects.create(
        sender="USER",
        content=incoming_text,
        unique_message_id=unique_message_id,
        session=session,
    )

    if incoming_text.startswith("create invoice"):
        send_message(
            get_text_message_input(
                sender_id, parse_and_post_invoice(incoming_text, auth_token)
            )
        )
        return JsonResponse(
            {"status": "success", "message": "Invoice created"}, status=200
        )

    if incoming_text == "#createinvoice":
        for message in [
            get_client_list(auth_token),
            get_product_list(auth_token),
            get_invoice_creation_prompt(),
            get_invoice_template(),
        ]:
            send_message(get_text_message_input(sender_id, message))
        return JsonResponse(
            {"status": "success", "message": "Invoice prompts sent"}, status=200
        )

    if incoming_text == "#options":
        send_message(get_interactive_list_message(sender_id))
        return JsonResponse(
            {"status": "success", "message": "Options sent"}, status=200
        )

    if incoming_text == "#logout":
        session.client = None
        session.save()
        send_message(get_text_message_input(sender_id, get_logout_message()))
        return JsonResponse({"status": "success", "message": "Logged out"}, status=200)

    chat_history = get_chat_history(sender_id)
    pipeline_instance = Pipeline(auth_token)
    response_message = pipeline_instance.run_generic_question(
        f"*Chat History:\n{chat_history}\n\nUser's Message:*\n{incoming_text}"
    )[:4096]
    send_message(get_text_message_input(sender_id, response_message))
    return JsonResponse(
        {"status": "success", "message": "Message processed"}, status=200
    )


@csrf_exempt
def webhook(request):
    if request.method == "GET":
        return HttpResponse(
            request.GET.get("hub.challenge", "Verification failed"),
            status=200 if "hub.challenge" in request.GET else 400,
        )

    if request.method != "POST":
        return HttpResponse("Method not allowed", status=405)

    try:
        data = json.loads(request.body)
        changes = data.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {})
        messages, contacts = changes.get("messages", []), changes.get("contacts", [])

        if "statuses" in changes:
            return JsonResponse({"status": "ignored status update"}, status=200)

        if not messages:
            return JsonResponse(
                {"status": "success", "message": "Webhook processed"}, status=200
            )

        sender_id, unique_message_id = messages[0]["from"], messages[0]["id"]
        incoming_text = messages[0].get("text", {}).get("body", "").strip().lower()
        print("Message Received:", incoming_text)

        if contacts:
            print(
                f"Whatsapp User Name: {contacts[0]['profile'].get('name', 'Unknown')}"
            )

        email, password = extract_email_password(incoming_text)
        if email and password:
            return handle_login(sender_id, email, password)

        session = Session.objects.filter(phone_number=sender_id).first()
        if session and session.client:
            return process_message(
                sender_id,
                unique_message_id,
                incoming_text,
                session,
                session.client.auth_token,
            )

        send_message(get_text_message_input(sender_id, get_login_detail_message()))
        return JsonResponse(
            {"status": "success", "message": "Login prompt sent"}, status=200
        )

    except json.JSONDecodeError:
        return JsonResponse(
            {"status": "error", "message": "Invalid JSON format"}, status=400
        )


if threading.active_count() > 1:
    print("🟢 Starting background scheduler thread...")
    run_scheduler()
