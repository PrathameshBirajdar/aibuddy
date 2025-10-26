from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render

def home_view(request):
    return render(request, "home.html")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("chat/", include("chat.urls")),  # chatbot API endpoint
    path("home/", home_view, name="home"),
    path("", home_view),  # ✅ root URL now shows homepage
]
