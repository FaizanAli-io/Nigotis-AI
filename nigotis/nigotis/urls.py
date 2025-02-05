from django.contrib import admin
from django.urls import path, include

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from django.http import HttpResponse




urlpatterns = [
    path("webhook/", include("whatsapp.urls")),
    path("admin/", admin.site.urls),
    path("chat/", include("chatbot.urls")),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("swagger/", SpectacularSwaggerView.as_view(url_name="schema")),
]
