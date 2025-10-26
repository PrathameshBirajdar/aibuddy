# aibuddy/chat/urls.py
from django.urls import path
from . import views

app_name = "chat"

urlpatterns = [
    path("popup/", views.chat_page, name="popup"),
    path("api/chat/", views.chat_api, name="chat_api"),
]
