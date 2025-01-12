import requests
from datetime import timedelta

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from drf_spectacular.utils import extend_schema
from django.utils.timezone import now

from .models import ChatSession
from .serializers import ChatSessionSerializer, LoginRequestSerializer


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

        login_email = login_serializer.validated_data["login_email"]
        login_password = login_serializer.validated_data["login_password"]

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
                name=f"{data['personalInfo']['firstName']} {data['personalInfo']['lastName']}",
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


class CheckAuthTokenView(APIView):
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
