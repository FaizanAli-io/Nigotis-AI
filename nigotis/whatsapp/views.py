import json
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from chatbot.bot.pipeline import Pipeline
from .services import get_text_message_input, send_message
from chatbot.models import ChatMessage, ChatSession
from .test2 import get_interactive_list_message
AUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY3MjhmNTE3N2I5YjdkZjJiMDA4YTA0MyIsImlhdCI6MTczNzM5OTgzOCwiZXhwIjoxNzM5OTkxODM4fQ.tvG0cOKC6l8CrAIoiWnqHNvg-szO9GWhAn9HX5aWkmU"

@csrf_exempt
def webhook(request):
    if request.method == "GET":
        challenge = request.GET.get("hub.challenge")
        if challenge:
            return HttpResponse(challenge, status=200)
        return HttpResponse("Verification failed", status=400)

    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            print("Incoming Webhook Data:", json.dumps(data, indent=2))

            entry = data.get("entry", [])[0]
            changes = entry.get("changes", [])[0]
            messages = changes.get("value", {}).get("messages", [])

            if messages:
                sender_id = messages[0]["from"]
                incoming_text = messages[0].get("text", {}).get("body", "").strip().lower()  # Convert to lowercase for case insensitivity
                
                # Handle "help" message
                if incoming_text == "#options":
                    interactive_message = get_interactive_list_message(sender_id)
                    send_message(interactive_message)
                    return JsonResponse({"status": "success", "message": "Help interactive message sent"}, status=200)

                # Handle interactive message responses
                if messages[0]["type"] == "interactive":
                    interactive_data = messages[0]["interactive"]
                    if "list_reply" in interactive_data:
                        selected_id = interactive_data["list_reply"]["id"]
                        if selected_id == "GEN":
                            response_message = "Please type your question in the format:\nGEN: {your question}"
                            send_message(get_text_message_input(sender_id, response_message))
                            return JsonResponse({"status": "prompted for question"}, status=200)
                        
                        session = ChatSession.objects.get(id=1)
                        ChatMessage.objects.create(sender="USER", content=selected_id, session=session)
                        print(f"User selected option ID: {selected_id}")
                        pipeline_instance = Pipeline(AUTH_TOKEN)
                        function_result = pipeline_instance.run_analysis_func(choice=selected_id)
                        print(function_result)
                        ChatMessage.objects.create(sender="BOT", content=function_result, session=session)
                        function_result = function_result[:4096]
                        message_data = get_text_message_input(sender_id, function_result)
                        send_message(message_data)
                        return JsonResponse({"status": "success", "message": "Analysis executed"}, status=200)

                # Handle generic text questions
                if incoming_text:
                    session = ChatSession.objects.get(id=1)
                    ChatMessage.objects.create(sender="USER", content=incoming_text, session=session)

                    pipeline_instance = Pipeline(AUTH_TOKEN)
                    function_result = pipeline_instance.run_generic_question(incoming_text)

                    print(function_result)
                    ChatMessage.objects.create(sender="BOT", content=function_result, session=session)
                    function_result = function_result[:4096]
                    message_data = get_text_message_input(sender_id, function_result)
                    send_message(message_data)
                    return JsonResponse({"status": "success", "message": "Analysis executed"}, status=200)

            return JsonResponse({"status": "success", "message": "Webhook processed"}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON format"}, status=400)

    return HttpResponse("Method not allowed", status=405)
