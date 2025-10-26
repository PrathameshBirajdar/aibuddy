from django.apps import AppConfig

class ChatConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "aibuddy.chat"  # ✅ must match import path exactly
    verbose_name = "AI Buddy Chat"
