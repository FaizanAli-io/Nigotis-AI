import json
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from chatbot.bot.pipeline import Pipeline
from .services import get_text_message_input, send_message ,authenticate_user
from chatbot.models import ChatMessage, ChatSession
from .test2 import get_interactive_list_message ,get_login_detail_message , get_logout_message
import re


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

            if "statuses" in data.get("entry", [])[0]["changes"][0]["value"]:
                # Log and ignore status updates
                print("Ignoring status update:", data)
                return JsonResponse({"status": "ignored status update"}, status=200)
            
            entry = data.get("entry", [])[0]
            changes = entry.get("changes", [])[0]
            messages = changes.get("value", {}).get("messages", [])
            contacts = changes.get("value", {}).get("contacts", [])
            


            if messages:

                sender_id = messages[0]["from"]
                unique_message_id = messages[0]["id"]

                incoming_text = messages[0].get("text", {}).get("body", "").strip()
                email_pattern = r"Email:\s*(\S+@\S+)"
                password_pattern = r"Password:\s*(\S+)"
                email_match = re.search(email_pattern, incoming_text, re.IGNORECASE)
                password_match = re.search(password_pattern, incoming_text, re.IGNORECASE)

                print(email_match,password_match)
                if email_match and password_match:
                        email = email_match.group(1).strip()
                        password = password_match.group(1).strip()
                        if email and password:
                            response = authenticate_user(email, password, sender_id)
                            message_data = get_text_message_input(sender_id, response)
                            send_message(message_data)
                            return JsonResponse({"status": "success", "message": "Analysis executed"}, status=200)
                        else :
                             send_message(get_text_message_input(sender_id, "⚠️ Please enter both email and password in the correct format."))
                             return JsonResponse({"status": "success", "message": "Analysis executed"}, status=200)




                incoming_text = messages[0].get("text", {}).get("body", "").strip().lower()  # Convert to lowercase for case insensitivity
                if contacts:
                    user_name = contacts[0]["profile"].get("name", "Unknown")
                    print(f"Whatsapp User Name: {user_name}")
                


                


                if ChatSession.objects.filter(phone_number=sender_id,auth_token__isnull=False).exists():
                    
                    session_data = ChatSession.objects.filter(phone_number=sender_id, auth_token__isnull=False).values("id", "auth_token").get()
                    session_id=session_data["id"]
                    auth_token=session_data["auth_token"]
                    session = ChatSession.objects.get(id=session_id)
                    AUTH_TOKEN = auth_token

                    if ChatMessage.objects.filter(unique_message_id=unique_message_id).exists():
                        print(f"Duplicate message detected: {unique_message_id}")
                        return JsonResponse({"status": "duplicate message ignored"}, status=200)
                    
                    # Handle "help" message
                    if incoming_text == "#options":
                        interactive_message = get_interactive_list_message(sender_id)
                        ChatMessage.objects.create(sender="USER", content=incoming_text,unique_message_id=unique_message_id ,session=session)
                        send_message(interactive_message)
                        ChatMessage.objects.create(sender="BOT", content="Options Sent.",unique_message_id="" ,session=session)
                        return JsonResponse({"status": "success", "message": "Help interactive message sent"}, status=200)
                    
                    if incoming_text == "#logout":
                     try:
                        session = ChatSession.objects.get(phone_number=sender_id)
                        session.login_email = None
                        session.login_password = None
                        session.auth_token = None
                        session.authenticated_at = None

       
                        session.save()

                        message_data = get_text_message_input(sender_id, get_logout_message())

                        send_message(message_data)
                        return JsonResponse({"status": "success", "message": "Help interactive message sent"}, status=200)
                     except :
                        error_message = "⚠️ Unable to logout. No active session found for your phone number."
                        send_message(get_text_message_input(sender_id, error_message))
                        return JsonResponse({"status": "error", "message": "No session found"}, status=404)
                         
                    # Handle interactive message responses
                    if messages[0]["type"] == "interactive":
                        interactive_data = messages[0]["interactive"]
                        if "list_reply" in interactive_data:
                            selected_id = interactive_data["list_reply"]["id"]
                            ChatMessage.objects.create(sender="USER", content=selected_id,unique_message_id=unique_message_id ,session=session)
                            print(f"User selected option ID: {selected_id}")
                            pipeline_instance = Pipeline(AUTH_TOKEN)
                            function_result = pipeline_instance.run_analysis_func(choice=selected_id)
                            print(function_result)

                            function_result = function_result[:4096]
                            message_data = get_text_message_input(sender_id, function_result)
                            send_message(message_data)
                            ChatMessage.objects.create(sender="BOT", content=function_result,unique_message_id="" ,session=session)
                            return JsonResponse({"status": "success", "message": "Analysis executed"}, status=200)

                    # Handle generic text questions
                    if incoming_text:
                        ChatMessage.objects.create(sender="USER", content=incoming_text,unique_message_id=unique_message_id ,session=session)
                     
                        pipeline_instance = Pipeline(AUTH_TOKEN)
                        function_result = pipeline_instance.run_generic_question(incoming_text)

                        print(function_result)

                    
                        function_result = function_result[:4096]
                        message_data = get_text_message_input(sender_id, function_result)
                        send_message(message_data)
                        ChatMessage.objects.create(sender="BOT", content=function_result,unique_message_id="" ,session=session)

                        return JsonResponse({"status": "success", "message": "Analysis executed"}, status=200)
                    
                elif not ChatSession.objects.filter(phone_number=sender_id).exists():
                    ChatSession.objects.create(phone_number=sender_id)
                    
                    message_data = get_text_message_input(sender_id, get_login_detail_message())
                    send_message(message_data)
                    return JsonResponse({"status": "success", "message": "Analysis executed"}, status=200)

                if ChatSession.objects.filter(phone_number=sender_id, auth_token__isnull=True).exists():

                    message_data = get_text_message_input(sender_id, get_login_detail_message())
                    send_message(message_data)
                    return JsonResponse({"status": "success", "message": "Analysis executed"}, status=200)
                
                    
                             


                    
            return JsonResponse({"status": "success", "message": "Webhook processed"}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON format"}, status=400)

    return HttpResponse("Method not allowed", status=405)
