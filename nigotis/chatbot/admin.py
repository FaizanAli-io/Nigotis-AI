from django.contrib import admin
from .models import Client, Session, Message


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "role", "login_email")


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ("id", "phone_number", "website", "client")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "sender", "content", "session")
