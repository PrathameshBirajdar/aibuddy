# Add to chat/urls.py
urlpatterns = [
    path("api/chat/", ChatAPIView.as_view(), name="chat_api"),
    path("popup/", chat_ui, name="chat_popup"),
    path("test/", test_groq, name="test_groq"),  # Add this
]