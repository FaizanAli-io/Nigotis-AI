import requests
from datetime import timedelta

from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import GenericAPIView
from drf_spectacular.utils import extend_schema
from django.utils.timezone import now

from .models import ChatSession, ChatMessage
from .serializers import (
    LoginRequestSerializer,
    ChatSessionSerializer,
    ChatMessageSerializer,
    OpenAiTestSerializer,
)

from .bot.pipeline import Pipeline


@extend_schema(tags=["Session"])
class ChatSessionViewSet(ModelViewSet):
    queryset = ChatSession.objects.all()
    serializer_class = ChatSessionSerializer

    @extend_schema(
        request=LoginRequestSerializer,
        responses={201: ChatSessionSerializer},
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
            session = ChatSession.objects.create(
                name=f"{data['personalInfo']['firstName']} {data['personalInfo'].get('lastName', '')}",
                role=data["role"].upper(),
                login_email=login_email,
                login_password=login_password,
                auth_token=data["token"],
            )

            serializer = ChatSessionSerializer(session)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except requests.RequestException:
            return Response(
                {"error": "Failed to communicate with the external API."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema(tags=["Session"])
class CheckAuthTokenView(GenericAPIView):
    def post(self, _, id):
        try:
            session = ChatSession.objects.get(id=id)
            elapsed = now() - session.authenticated_at

            if elapsed > timedelta(hours=24):
                response = requests.post(
                    "https://nigotis-be.vercel.app/api/v1/user/login",
                    json={
                        "email": session.login_email,
                        "password": session.login_password,
                    },
                )
                response_data = response.json()

                if response.status_code != 200 or not response_data.get("success"):
                    return Response(
                        {"error": "Failed to re-authenticate."},
                        status=status.HTTP_401_UNAUTHORIZED,
                    )

                session.auth_token = response_data["data"]["token"]
                session.authenticated_at = now()
                session.save()

                serializer = ChatSessionSerializer(session)
                return Response(serializer.data, status=status.HTTP_200_OK)

            else:
                return Response(
                    {"message": f"It has only been {elapsed}"},
                    status=status.HTTP_200_OK,
                )

        except ChatSession.DoesNotExist:
            return Response(
                {"error": "Chat session not found"}, status=status.HTTP_404_NOT_FOUND
            )


@extend_schema(tags=["Message"])
class ChatMessageViewSet(ModelViewSet):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer

    def perform_create(self, serializer):
        serializer.save(sender="USER")


@extend_schema(tags=["Testing"])
class OpenAiTestView(GenericAPIView):
    serializer_class = OpenAiTestSerializer

    def post(self, request, id):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session = ChatSession.objects.get(id=id)
        pipeline = Pipeline(session.auth_token)

        feature = serializer.validated_data["feature"]

        try:
            if feature == "GEN":
                message = serializer.validated_data["message"]
                bot_message = pipeline.run_generic_question(message)
            else:
                bot_message = pipeline.run_analysis_func(feature)
        except Exception as e:
            bot_message = e

        dumpname = message if feature == "GEN" else feature
        with open(f"dump/{dumpname}.txt", "w") as f:
            f.write(bot_message)

        return Response(
            {"message": bot_message},
            status=status.HTTP_200_OK,
        )
