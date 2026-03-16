from django.contrib import admin
from django.urls import path,include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/',include('user.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),   
]

admin.site.site_title = 'Delivery system admin dahsboard'
admin.site.site_header = 'Delivery system admin'
admin.site.index_title = 'Dashboard'