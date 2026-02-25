from django.urls import path,include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'books',views.BookViewSet,basename='book')
router.register(r'tasks',views.TaskViewSet,basename='task')
router.register(r'authors',views.AuthorViewSet,basename='author')
router.register(r'products',views.ProductViewSet,basename='product')

urlpatterns = [
    path('',include(router.urls)),
    #path('test/',BookView.as_view())
]

