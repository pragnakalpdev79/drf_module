from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    #PROFILE VIEWS
    path('auth/test',CustomerProfileView.as_view(),name='test1'),
    path('auth/test',AddressViewSet.as_view(),name='test2'),
   
]