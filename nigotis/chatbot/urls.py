from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ChatSessionViewSet, CheckAuthTokenView

router = DefaultRouter()

router.register("", ChatSessionViewSet, basename="chatsession")

urlpatterns = [
    path("", include(router.urls)),
    path("refresh-auth/<int:id>", CheckAuthTokenView.as_view()),
]
