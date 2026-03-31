from django.shortcuts import render
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAdminUser
from rest_framework import generics,status,viewsets,filters
from rest_framework.response import Response
from user.models import CustomUser,address
from .serializers import *

logger = logging.getLogger('user')

# class CustomerProfileView1(viewsets.ModelViewSet):
#     queryset = CustomerProfile.objects.select_related('user')
#     permission_classes = [IsAuthenticated]
#     serializer_class = CustomProfileSerializer
#     http_method_names = ['get','patch']

    # def retrieve(self,request,pk=None):
    #     print("profile details")
    #     profile = CustomerProfile.objects.select_related('user').get(user=self.request.user)
    #     serializer = self.get_serializer(profile)
    #     return Response({
    #         "message": "here are your profile details",
    #         "user_id": pk,
    #         "details" : serializer.data,
    #     })

    
    # def get(self,request,*args,**kwargs):
    #     print("here")
    #     myprofile = self.get_object()

    #     return Response({
    #         'message': 'you can upload your avatar here through patch request',
    #         'first_name' : myprofile.user.first_name,
    #         'last_name' : myprofile.user.last_name,
    #         'email' : myprofile.user.email,
    #         'phone_number': myprofile.user.phone_number,
    #         'default adress' : myprofile.default_adress.address,

    #     })

    # def put(self,request,*args,**kwargs):
    #     return Response({
    #         'message': 'This method is not allowed use patch'
    #     })   

class CustomerProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = CustomProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        profile = CustomerProfile.objects.select_related('user').get(user=self.request.user)
        serializer = CustomProfileSerializer(profile)
        #logger.info('step3')
        #print(profile.default_adress.address)
        return profile
    
    def get(self,request,*args,**kwargs):
        myprofile = self.get_object()

        return Response({
            'message': 'you can upload your avatar here through patch request',
            'first_name' : myprofile.user.first_name,
            'last_name' : myprofile.user.last_name,
            'email' : myprofile.user.email,
            'phone_number': myprofile.user.phone_number,
            'default adress' : myprofile.default_adress.address,

        })

    def put(self,request,*args,**kwargs):
        return Response({
            'message': 'This method is not allowed use patch'
        })

class DriverProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = DriverProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        profile = DriverProfile.objects.select_related('user').get(user=self.request.user)
        return profile
    
    def get(self,request,*args,**kwargs):
        myprofile = self.get_object()

        return Response({
            'message': 'you can only upload your avatar,license number and vehicle number here through patch request',
            'first_name' : myprofile.user.first_name,
            'last_name' : myprofile.user.last_name,
            'email' : myprofile.user.email,
            'phone_number': myprofile.user.phone_number,
            'vehicle type' :  myprofile.vehicle_type,
            'vehicle number' :  myprofile.vehicle_number,
            'license number' :  myprofile.license_number,
            'total deliveries' :  myprofile.total_deliveries,
            'average rating' :  myprofile.average_rating,
        })

class AddressViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing patients.
    Full ViewSet for Patient model:
    - POST /api/v1/patients/ (create)
    - GET /api/v1/patients/ (list all)
    - GET /api/v1/patients/{id}/ (retrieve)
    - PUT /api/v1/patients/{id}/ (update)
    """
    
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return address.objects.filter(adrofuser=self.request.user)