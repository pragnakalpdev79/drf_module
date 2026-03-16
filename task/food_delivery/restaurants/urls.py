from django.urls import path
from .views import *

urlpatterns = [
    path('listall',RestoListView.as_view(),name='listofallresto'),
    path('test',RestoCreateView.as_view(),name='test1')
    
]