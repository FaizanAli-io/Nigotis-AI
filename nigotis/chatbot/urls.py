from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ClientViewSet,
    SessionViewSet,
    MessageViewSet,
    TalkToChatBotView,
    CheckAuthTokenView,
)

router = DefaultRouter()

router.register("client", ClientViewSet, basename="client")
router.register("session", SessionViewSet, basename="session")
router.register("message", MessageViewSet, basename="message")

urlpatterns = [
    path("", include(router.urls)),
    path("talk-to-bot/<int:id>", TalkToChatBotView.as_view()),
    path("refresh-auth/<int:id>", CheckAuthTokenView.as_view()),
]
