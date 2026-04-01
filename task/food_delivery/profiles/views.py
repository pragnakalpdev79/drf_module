from django.shortcuts import render
from drf_spectacular.utils import extend_schema,extend_schema_view
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

@extend_schema_view(
    get=extend_schema(
        summary=" P.1 Customer Profile",
        description="Your profile details",
        tags=["Customer-Profiles"]),
    patch=extend_schema(
        summary=" P.2 Update Customer Profile",
        description=" Update your profile details here",
        tags=['Customer-Profiles']
    ),
    put=extend_schema(
        summary=" P.3 This method is not allowed",
        description = "Please use patch method instead",
        tags=['Customer-Profiles']
    ),
)
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


@extend_schema_view(
    get=extend_schema(
        summary=" DP.1 Driver Profile",
        description="Your profile details",
        tags=["Driver-Profiles"]),
    patch=extend_schema(
        summary=" DP.2 Update Driver Profile",
        description=" Update your profile details here",
        tags=['Driver-Profiles']
    ),
    put=extend_schema(
        summary=" DP.3 This method is not allowed",
        description = "Please use patch method instead",
        tags=['Driver-Profiles']
    ),
)
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
    def put(self,request,*args,**kwargs):
        return Response({
            'message': 'This method is not allowed use patch'
        })
    

class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    http_method_names = ['get', 'post','patch']
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return address.objects.filter(adrofuser=self.request.user)