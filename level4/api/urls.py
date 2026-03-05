from django.urls import path,include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'books',views.BookViewSet,basename='book')
router.register(r'tasks',views.TaskViewSet,basename='task')
router.register(r'posts',views.PostViewSet,basename='post')
router.register(r'tags',views.TagViewSet,basename='tag')



urlpatterns = [
    path('',include(router.urls)),
    path('register/',views.UserRegistrationView.as_view(),name='register'),
    path('e1/',views.async_task_list,name='HarryPotter'),
    #path('e2/',views.AsyncBookView.as_view(),name='e2'),
    #path('test/',BookView.as_view())

]

