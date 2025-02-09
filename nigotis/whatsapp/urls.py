from django.urls import path
from .views import webhook  # Import the unified webhook view

urlpatterns = [
    path("", webhook, name="whatsapp-webhook"),  # Handle / for WhatsApp app
]
