from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ChatSessionViewSet, ChatMessageViewSet, CheckAuthTokenView

router = DefaultRouter()
router.register("session", ChatSessionViewSet, basename="session")
router.register("message", ChatMessageViewSet, basename="message")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "refresh-auth/<int:id>",
        CheckAuthTokenView.as_view(),
    ),
]
