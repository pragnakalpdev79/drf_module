# mysite/urls.py
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("chatapp/", include("chatapp.urls")),
    path("admin/", admin.site.urls),
]