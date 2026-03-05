from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'task',views.TaskViewSet,basename='task')
router.register(r'taskfile',views.TaskAttachmentViewSet,basename='tfile')


urlpatterns = [
    path('',include(router.urls)),
    path('register/',views.UserRegistrationView.as_view(),name='register'),
]
if settings.DEBUG: #USED TO SERVE MEDIA FILES IN DJANGO
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
