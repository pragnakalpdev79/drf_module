from django.contrib import admin
from django.urls import path,include
from .views import *

urlpatterns = [
    path('get-books/',get_books),
]