import logging
from django.shortcuts import render
from django.contrib.auth.mixins import UserPassesTestMixin
from rest_framework import generics,status,viewsets,permissions,renderers
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny,IsAuthenticatedOrReadOnly,IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from user.models import RestrauntModel
from user.permissions import IsRestaurantOwner
from .serializers import *

logger = logging.getLogger('user')

class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = RestrauntModel.objects.all()
    http_method_names = ['get', 'post','patch']

    def get_serializer_class(self):
        if self.action == 'list':
            return RestoListSerializer
        elif self.action == 'create':
            return RestoCreateSerializer
        elif self.action == 'retrieve':
            return RestoSerializer
        return RestoListSerializer
    
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
    
#==============================================================================
# 1. GET ALL RESTAURANTS BY GET METHOOD
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
#==============================================================================
# 2. GET ONE RESTAURANT BY ITS ID
    def retrieve(self, request, pk=None):
        resto = RestrauntModel.objects.prefetch_related('menu','review_for').get(id=pk)
        serializer = self.get_serializer(resto)
        #print(resto.menu)
        return Response({
            "message" : "Here are the restaurant details",
            "resto_id" : pk,
            'details' : serializer.data,
        })
#==============================================================================
# 3. REGISTER A NEW RESTAURANT - BY OWNER ONLY
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
# 3.1 ACTUAL MODEL SAVE FOR NEW RESTO
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
#==============================================================================
# 4. GET MENU ITEMS OF A SPECIFC RESTAURANT IF YOU HAVE RESTO ID
    @action(detail=True,methods=['get'])
    def menu(self,request,pk=None):
        queryset = MenuItem.objects.filter(restaurant_id=pk)
        serializer = MenuItemSerializer(queryset,many=True)
        if not serializer.data:
            msg = "The requested menu does not exist"
            st = status.HTTP_404_NOT_FOUND
        else:
            msg = "Here is the menu for restaurant"
            st = status.HTTP_200_OK

        return Response({
            "message" : msg,
            "id": pk,
            "menu" : serializer.data,
        },
        status = st)
#==============================================================================
#==============================================================================
        

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
