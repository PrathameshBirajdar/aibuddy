# aibuddy/aibuddy/urls.py
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static


# ✅ Home redirect view
def home_redirect(request):
    return redirect("chat:popup")  # goes to chatbot popup by default


urlpatterns = [
    path('admin/', admin.site.urls),

    # ✅ Chatbot app routes
    path('chat/', include('chat.urls')),

    # ✅ Default home route
    path('', home_redirect, name='home'),
]


# ✅ Static files for development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
