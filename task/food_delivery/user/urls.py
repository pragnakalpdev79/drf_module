from django.contrib import admin
from django.urls import path,include
from .views import UserRegisterationView

urlpatterns = [
    path('register/',UserRegisterationView.as_view(),name='register'),
]