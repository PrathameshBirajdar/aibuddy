from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

# ✅ Redirect root "/" to the chat popup page
def home_redirect(request):
    return redirect('/chat/popup/')

urlpatterns = [
    path('', home_redirect, name='home'),  # ✅ Root redirect added
    path('admin/', admin.site.urls),
    path('chat/', include('chat.urls')),
]
