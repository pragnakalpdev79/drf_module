from django.contrib import admin
from django.urls import path,include
from rest_framework_simplejwt.views import (
    TokenObtainPairView, #--> get tokens
    TokenRefreshView, #--> get new access token
    TokenVerifyView,#--> check if token is valid or not
)
from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView,SpectacularSwaggerView,SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    #api app endpoint
    path('api/',include('api.urls')),
    #endpoints for jwt
    path('api/token',TokenObtainPairView.as_view(),name='token_obtain_pair'),
    path('api/token/refresh',TokenRefreshView.as_view(),name='token_refresh'),
    path('api/token/verify',TokenVerifyView.as_view(),name='token_verify'),
    path('api/schema/',SpectacularAPIView.as_view(  ),name='schema'),
    path('api/docs/',SpectacularSwaggerView.as_view(url_name='schema'),name='swagger-ui'),
    path('api/redoc/',SpectacularRedocView.as_view(url_name='schema'),name='redoc'),

] + debug_toolbar_urls()

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
