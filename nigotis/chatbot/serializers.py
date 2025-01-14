from rest_framework import serializers
from .models import ChatSession, ChatMessage


class LoginRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class ChatSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatSession
        fields = [
            "id",
            "name",
            "role",
            "login_email",
            "auth_token",
            "authenticated_at",
            "created_at",
            "updated_at",
        ]


class ChatMessageSerializer(serializers.ModelSerializer):
    sender = serializers.CharField(default="USER", read_only=True)

    class Meta:
        model = ChatMessage
        fields = "__all__"


class OpenAiTestSerializer(serializers.Serializer):
    feature = serializers.ChoiceField(
        choices=[
            ("1", "Customer Segmentation"),
            ("2", "Product Preference"),
        ]
    )
