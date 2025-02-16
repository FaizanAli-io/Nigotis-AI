from django.contrib import admin
from .models import Client, Message


@admin.register(Client)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "role", "login_email")


@admin.register(Message)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "sender", "content", "session")
