from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render

def home_view(request):
    return render(request, "home.html")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('chat/', include('chat.urls')),   # ✅ connects to chat app
    path('home/', home_view, name='home'), # ✅ this fixes /home/
    path('', home_view),                   # ✅ root route redirects to home
]
