from rest_framework import serializers
from .models import ChatSession


class LoginRequestSerializer(serializers.Serializer):
    login_email = serializers.EmailField()
    login_password = serializers.CharField()


class ChatSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatSession
        fields = ["id", "name", "role", "login_email", "auth_token", "authenticated_at"]
