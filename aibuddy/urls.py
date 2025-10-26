from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponseRedirect
from django.shortcuts import render

def home_view(request):
    return render(request, "home.html")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("chat/", include("chat.urls")),  # ✅ include chat endpoints
    path("", lambda request: HttpResponseRedirect("/home/")),  # redirect /
    path("home/", home_view, name="home"),
]
