import requests

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import NotFound, ValidationError
from drf_spectacular.utils import extend_schema
from django.utils.timezone import now


from .models import Message, Client, Session

from .serializers import (
    ClientSerializer,
    MessageSerializer,
    SessionSerializer,
    LoginRequestSerializer,
    TalkToChatBotSerializer,
)

from agent.agent import ToolAgent


@extend_schema(tags=["Client"])
class ClientViewSet(ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

    @extend_schema(
        request=LoginRequestSerializer,
        responses={
            200: ClientSerializer,
            201: ClientSerializer,
        },
    )
    def create(self, request):
        login_serializer = LoginRequestSerializer(data=request.data)
        login_serializer.is_valid(raise_exception=True)

        login_email = login_serializer.validated_data["email"]
        login_password = login_serializer.validated_data["password"]

        try:
            response = requests.post(
                "https://nigotis-be.vercel.app/api/v1/user/login",
                json={"email": login_email, "password": login_password},
            )
            response_data = response.json()

            if response.status_code != 200 or not response_data.get("success"):
                return Response(
                    {"error": "Authentication failed."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            data = response_data.get("data", {})
            auth_token = data["token"]

            existing_client = Client.objects.filter(
                login_email=login_email,
                login_password=login_password,
            ).first()

            if existing_client:
                existing_client.auth_token = auth_token
                existing_client.authenticated_at = now()
                existing_client.save()

                serializer = ClientSerializer(existing_client)
                return Response(serializer.data, status=status.HTTP_200_OK)

            client = Client.objects.create(
                name=f"{data['personalInfo']['firstName']} {data['personalInfo']['lastName']}",
                auth_token=auth_token,
                login_email=login_email,
                role=data["role"].upper(),
                login_password=login_password,
            )

            serializer = ClientSerializer(client)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except requests.RequestException:
            return Response(
                {"error": "Failed to communicate with the external API."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema(tags=["Session"])
class SessionViewSet(ModelViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer

    @extend_schema(
        summary="Get or delete all messages for a session",
        responses={200: MessageSerializer(many=True), 204: None},
    )
    @action(detail=True, methods=["get", "delete"], url_path="messages")
    def manage_messages(self, request, pk=None):
        if request.method == "GET":
            messages = Message.objects.filter(session_id=pk)
            serializer = MessageSerializer(messages, many=True)
            return Response(serializer.data)

        elif request.method == "DELETE":
            Message.objects.filter(session_id=pk).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=["Message"])
class MessageViewSet(ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def perform_create(self, serializer):
        serializer.save(sender="USER")


@extend_schema(tags=["Other"])
class CheckAuthTokenView(APIView):
    def post(self, _, id):
        try:
            client = Client.objects.get(id=id)
            response = requests.post(
                "https://nigotis-be.vercel.app/api/v1/user/login",
                json={
                    "email": client.login_email,
                    "password": client.login_password,
                },
            )
            response_data = response.json()

            if response.status_code != 200 or not response_data.get("success"):
                return Response(
                    {"error": "Failed to re-authenticate."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            client.auth_token = response_data["data"]["token"]
            client.authenticated_at = now()
            client.save()

            serializer = ClientSerializer(client)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Client.DoesNotExist:
            return Response(
                {"error": "Client not found"},
                status=status.HTTP_404_NOT_FOUND,
            )


@extend_schema(tags=["Other"], request=TalkToChatBotSerializer)
class TalkToChatBotView(APIView):
    def post(self, request, id):
        try:
            session = Session.objects.get(id=id)
        except Session.DoesNotExist:
            raise NotFound("Session not found.")

        message = request.data.get("message")
        if not message:
            raise ValidationError("Message is required.")

        try:
            agent = ToolAgent()
            bot_message = agent.get_response(session, message)
        except Exception as e:
            raise ValidationError(f"Error while sending message: {str(e)}")

        return Response(
            {"message": bot_message},
            status=status.HTTP_200_OK,
        )
