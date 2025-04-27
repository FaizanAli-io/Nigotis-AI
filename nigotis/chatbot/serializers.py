from rest_framework import serializers
from .models import Message, Client, Session


class LoginRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        exclude = ["login_password"]


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.CharField(default="USER", read_only=True)

    class Meta:
        model = Message
        fields = "__all__"


class SessionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Session
        fields = "__all__"


class TalkToChatBotSerializer(serializers.Serializer):
    message = serializers.CharField(required=True)
