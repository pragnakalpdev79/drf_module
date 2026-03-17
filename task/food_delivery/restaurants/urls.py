from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r"details",RestaurantViewSet,basename='restaurant')

urlpatterns = [
    path("",include(router.urls)),
    #path('listall',RestoListView.as_view(),name='listofallresto'),
    #path('test',RestoCreateView.as_view(),name='test1')
    
]