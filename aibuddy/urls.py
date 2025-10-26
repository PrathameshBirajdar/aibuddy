from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render

# ✅ This will now load chat_page.html
def home_view(request):
    return render(request, "chat/chat_page.html")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("chat/", include("chat.urls")),
    path("", home_view, name="home"),  # root → chat_page.html
    path("home/", home_view),
]
