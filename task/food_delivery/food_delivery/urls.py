from django.contrib import admin
from django.urls import path,include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/',include('user.urls')),
    path('user/token/',TokenObtainPairView.as_view(),name='token_obtain_pair'), #LOGIN
    path('user/token/refresh/',TokenRefreshView.as_view(),name='token_refresh'), #REFRESH
    path('user/token/verify/',TokenVerifyView.as_view(),name='token_verify'), #VERIFY
]

admin.site.site_title = 'Delivery system admin dahsboard'
admin.site.site_header = 'Delivery system admin'
admin.site.index_title = 'Dashboard'