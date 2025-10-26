from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponseRedirect

urlpatterns = [
    path("admin/", admin.site.urls),
    path("chat/", include("chat.urls")),
    # redirect / to /home/ if user visits root
    path("", lambda request: HttpResponseRedirect("/home/")),
]
