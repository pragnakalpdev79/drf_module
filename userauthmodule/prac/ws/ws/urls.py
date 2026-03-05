from django.contrib import admin
from django.urls import path
from app.views import chat_box

urlpatterns = [
    path("admin/",admin.site.urls),
    path("chat/<str:chat_box_name>/",chat_box,name='chat'),
]