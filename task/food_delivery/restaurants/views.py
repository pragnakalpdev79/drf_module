import logging
from django.shortcuts import render
from django.contrib.auth.mixins import UserPassesTestMixin
from rest_framework import generics,status,viewsets,permissions,renderers
from rest_framework.permissions import AllowAny,IsAuthenticatedOrReadOnly,IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from user.models import RestrauntModel
from user.permissions import IsRestaurantOwner
from .serializers import *

logger = logging.getLogger('user')

class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = RestrauntModel.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return RestoListSerializer
        elif self.action == 'create':
            return RestoCreateSerializer
    
    def get_permissions(self):
        #logger.info("Current action",self.action)
        print(self.action)
        if self.action == 'list':
            return [AllowAny()]
        if self.action == 'create':
            logger.info("Create action detected")
            #print(self.request.user.check_if_restaurant,self.request.user.get_user_permissions())
            return [IsRestaurantOwner()]
        return [IsAuthenticatedOrReadOnly()]

    def list(self,request): #list does not have incoming data,so not passing data into serializer
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset,many=True) #this tells drf that the queryset contains multiple items
        # serializer.is_valid(raise_exception=True)
        logger.info(f"Listing all rests : -  {serializer.data}")
        #serializer(self.queryset)
        return Response(serializer.data)    # def has_permission(self, request, view):
    #     logger.info("test!!")
    #     logger.info(request.user.has_perm("add_restrauntmodel"))
    #     return False
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


    def create(self,request,*args,**kwargs): #this create is to handle post request not to actually create something!
        logger.info(request.user.has_perm("add_restrauntmodel"))
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {
            'success': True,
            'message' : "Your restaurant has been successfully registered with us",
            'data' : serializer.data,
        },
        status=status.HTTP_201_CREATED)


        

# class RestoListView(APIView):
#     permission_classes = [AllowAny]
#     def get(self,request):
#         tolist = RestrauntModel.objects.all()
#         serializers = RestoListSerializer(tolist,many=True)
#         return Response(serializers.data,status=status.HTTP_200_OK)


# class RestoCreateView(APIView):

#     # def test_func(self):UserPassesTestMixin
#     #     print(self.request.user.has_perm("add_restrauntmodel"))
#     #     return self.request.user.has_perm("add_restrauntmodel")
    
#     permission_classes = [IsRestaurantOwner]
#     def get(self,request):
#         return Response({
#             "message" : "permissions works!",
#         })
