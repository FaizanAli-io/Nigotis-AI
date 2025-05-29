from rest_framework import serializers
from .models import Message, Client, Session


class LoginRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    account_type = serializers.ChoiceField(choices=["admin", "sub-account"])


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        exclude = ["login_password"]


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.CharField(default="USER", read_only=True)

    class Meta:
        model = Message
        exclude = ["embedding"]


class SessionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Session
        fields = "__all__"


class TalkToChatBotSerializer(serializers.Serializer):
    message = serializers.CharField(required=True)
