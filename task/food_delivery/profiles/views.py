from django.shortcuts import render
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAdminUser
from rest_framework import generics,status,viewsets,filters
from user.models import CustomUser,address
from .serializers import *


class CustomerProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = CustomProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        profile = CustomerProfile.objects.get(user=self.request.user)
        return profile
    
    # def put(self,request,*args,**kwargs):
    #     return self.update(request,*args,**kwargs)

class DriverProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = DriverProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        profile,created = DriverProfile.objects.get_or_create(
            user=self.request.user,
            defaults={'vehicle_number':'','license_number':'TEMP000temp'}
        )
        return profile

class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return address.objects.filter(user=self.request.user)