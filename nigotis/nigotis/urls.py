from django.contrib import admin
from django.urls import path, include

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from django.http import HttpResponse


def verify(request):
    challenge = request.GET.get("hub.challenge")
    return HttpResponse(challenge, status=200)


urlpatterns = [
    path("webhook/", verify),
    path("admin/", admin.site.urls),
    path("chat/", include("chatbot.urls")),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("swagger/", SpectacularSwaggerView.as_view(url_name="schema")),
]
