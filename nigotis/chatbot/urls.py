from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ChatMessageViewSet,
    CheckAuthTokenView,
    OpenAiTestView,
    SessionViewSet,
    ClientViewSet,

)

router = DefaultRouter()

router.register("message", ChatMessageViewSet, basename="message")
router.register("chat-session", SessionViewSet, basename="chat-session")
router.register("client", ClientViewSet, basename="client")

urlpatterns = [
    path("", include(router.urls)),
    path("test-chatbot/<int:id>", OpenAiTestView.as_view()),
    path("refresh-auth/<int:id>", CheckAuthTokenView.as_view()),
]
