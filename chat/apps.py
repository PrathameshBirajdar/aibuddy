from django.apps import AppConfig

class ChatConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "aibuddy.chat"   # ✅ full path matches your folder structure
