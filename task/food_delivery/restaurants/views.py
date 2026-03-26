import logging
from django.shortcuts import render
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics,status,viewsets,permissions,renderers,filters
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny,IsAuthenticatedOrReadOnly,IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from user.models import RestrauntModel
from user.permissions import IsRestaurantOwner
from .serializers import *
from .pagination import RestoPagination

logger = logging.getLogger('user')

class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = RestrauntModel.objects.all()
    http_method_names = ['get', 'post','patch']
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['cuisine_type','is_open']
    pagination_class = RestoPagination

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
        if request.version == 'v2':
            # ZERO QUERIES AFTER FIRST RUN
            logger.info("using v2")
            #ADDING REDIS CACHE IN VERSION 2
            self.cache_key = 'resto_list'
            self.cached_data = cache.get(self.cache_key)
            if self.cached_data is None:
                logger.info("not cached yet")
                queryset = self.filter_queryset(self.get_queryset())
                serializer = self.get_serializer(queryset,many=True)
                self.cached_data = serializer.data
                cache.set(self.cache_key,self.cached_data,300)
            return Response(self.cached_data)
        # by defualt v1
        logger.info("using v1")
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset,many=True) #this tells drf that the queryset contains multiple items
        logger.info(f"Listing all rests : -  {serializer.data}")
        print(self.get_paginated_response(serializer.data))
        return Response(serializer.data)
    
#==============================================================================
# 2. GET ONE RESTAURANT BY ITS ID
    def retrieve(self, request, pk=None):
        if request.version == 'v2':
            logger.info("using v2")
            self.cache_key = f"resto_{pk}"
            self.cached_data = cache.get(self.cache_key)
            if self.cached_data is None:
                resto = RestrauntModel.objects.prefetch_related('menu','review_for').get(id=pk)
                serializer = self.get_serializer(resto)
                return Response({
                    "message" : "Here are the restaurant details",
                    "resto_id" : pk,
                    'details' : serializer.data,
                })
        resto = RestrauntModel.objects.prefetch_related('menu','review_for').get(id=pk)
        serializer = self.get_serializer(resto)
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
        if self.cached_data:
            logger("updating cached data")
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
