# chat/urls.py
from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import *

# router = DefaultRouter()
# router.register(r'test',TaskViewSet,basename='testing')

urlpatterns = [
    path("", index, name="index"),
    #path("t/",include(router.urls)),
    path('t/test/',test,name='test'),
    path("<str:room_name>/",room,name='room'),
    
    
]