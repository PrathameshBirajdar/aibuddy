from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponseRedirect
from django.shortcuts import render

# ✅ Add a simple home view inline for now
def home_view(request):
    return render(request, "home.html")  # or your actual home template

urlpatterns = [
    path("admin/", admin.site.urls),
    path("chat/", include("chat.urls")),

    # Redirect root (/) to home
    path("", lambda request: HttpResponseRedirect("/home/")),
    path("home/", home_view, name="home"),  # ✅ This adds /home/
]
