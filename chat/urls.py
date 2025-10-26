from django.urls import path
from .views import ChatAPIView, chat_ui, test_groq

urlpatterns = [
    path("api/chat/", ChatAPIView.as_view(), name="chat_api"),
    path("popup/", chat_ui, name="chat_popup"),
    path("test/groq/", test_groq, name="test_groq"),
]