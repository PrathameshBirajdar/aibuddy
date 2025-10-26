from django.urls import path
from . import views

urlpatterns = [
    path('popup/', views.chat_page, name='chat_page'),
    path('api/chat/', views.chat_api, name='chat_api'),
]
