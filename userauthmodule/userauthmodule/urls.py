
from django.contrib import admin
from django.urls import path,include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,  # POST /api/token/ - Get tokens (login)
    TokenRefreshView,     # POST /api/token/refresh/ - Get new access token
    TokenVerifyView,      # POST /api/token/verify/ - Check if token is valid
)
from drf_spectacular.views import SpectacularAPIView,SpectacularSwaggerView,SpectacularRedocView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/<str:version>/', include('api.urls')),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('schema/',SpectacularAPIView.as_view(),name='schema'),
    path('docs/',SpectacularSwaggerView.as_view(url_name='schema'),name='swagger-ui'),
    path('redoc/',SpectacularRedocView.as_view(url_name='schema'),name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)