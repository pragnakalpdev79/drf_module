from django.urls import path,include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'books',views.BookViewSet,basename='book')
router.register(r'tasks',views.TaskViewSet,basename='task')

urlpatterns = [
    path('',include(router.urls)),
    path('register/',views.UserRegistrationView.as_view(),name='register'),
    #path('test/',BookView.as_view())

]

