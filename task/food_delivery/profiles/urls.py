from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'test1',AddressViewSet,basename='address')

urlpatterns = [
    #PROFILE VIEWS
    path('auth/test',CustomerProfileView.as_view(),name='test1'),
    #path('auth/test',AddressViewSet,name='test2'),
   
]