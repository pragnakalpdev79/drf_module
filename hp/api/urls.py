from django.urls import path,include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.tokens import RefreshToken 
from . import views

router = DefaultRouter()
router.register(r'hp',views.HpViewSet,basename='harrypotter')
router.register(r'task',views.TaskViewSet,basename='task')

urlpatterns = [
    path('',include(router.urls)),
    path('register/',views.UserRegistrationView.as_view(),name='register')
]