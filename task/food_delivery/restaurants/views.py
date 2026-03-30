import logging
from django.shortcuts import render
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import generics,status,viewsets,permissions,renderers,filters
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny,IsAuthenticatedOrReadOnly,IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from user.models import RestrauntModel
from user.permissions import IsRestaurantOwner
from .serializers import *
from .pagination import RestoPagination,MenuItemPagination

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
        elif self.action == 'menu':
            print("heollo!!")
            return MenuItemSerializer
        print("none")
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
    @extend_schema(
            parameters = [
                {
                    'name': 'name1',
                    'hello':'hi,'
                }
            ]
    )
    def list(self,request): #list does not have incoming data,so not passing data into serializer
        if request.version == 'v2':
            # ZERO QUERIES AFTER FIRST RUN
            logger.info("using v2")
            #ADDING REDIS CACHE IN VERSION 2
            self.cache_key = 'resto_list'
            self.cached_data = cache.get(self.cache_key)
            print(type(self.cached_data))
            if self.cached_data is None:
                logger.info("not cached yet")
                queryset = self.filter_queryset(self.get_queryset())
                page = self.paginate_queryset(queryset)
                if page is not None:
                    print(page)
                    serializer = self.get_serializer(page,many=True)
                    self.cached_data = serializer.data
                    cache.set(self.cache_key,self.cached_data,300)
                    return self.get_paginated_response(serializer.data)
                
            return Response(self.cached_data)
        # by defualt v1
        logger.info("using v1")
        queryset = self.get_queryset()
        page = self.paginate_queryset(self.get_queryset())
        if page is not None:
            logger.info(page)
            serializer = self.get_serializer(page,many=True)
            logger.info(f"returning {self.get_paginated_response(serializer.data)}")
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset,many=True) #this tells drf that the queryset contains multiple items
        logger.info(f"Listing all rests : -  {type(serializer.data)}")
        #print(self.get_paginated_response(serializer.data))
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
                self.cached_data = serializer.data
                cache.set(self.cache_key,self.cached_data,600)
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
    @action(detail=True,methods=['get'],
            pagination_class=MenuItemPagination)
    def menu(self,request,pk=None):
        queryset = MenuItem.objects.filter(restaurant_id=pk)
        logger.info(f"details requested for {pk} with version {request.version}")
        #for v1 only pagination
        #for v2 pagination + per page caching
        if request.version == 'v2':
            logger.info("using v2")
            self.cache_key = f"menuof__{pk}"
            self.cache_data = cache.get(self.cache_key)
            if self.cached_data is None:
                logger.info("not cached yet")
                page = self.paginate_queryset(queryset)
                if page is not None:
                    serializer = self.get_serializer(page,many=True)
                    self.cache_data = serializer.data
                    cache.set(self.cache_key,self.cache_data,900) #menu items by restaurant cached for 15 minutes
                    return self.get_paginated_response(serializer.data)
            return Response(self.cached_data)
        logger.info("using v1")
        page = self.paginate_queryset(queryset)
        if page is not None:
            serialzier = self.get_serializer(page,many=True)
            return self.get_paginated_response(serialzier.data)
    
        serializer = self.get_serializer(queryset,many=True)
        logger.info("listing all menu items")

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
# 5. POPULAR RESTOS
    @action(detail=False,methods=['get'])
    def popular(self,request):
        queryset = RestrauntModel.objects.order_by('-total_reviews')
        serializer = self.get_serializer(queryset,many=True)
        logger.info("listing popular restos")
        logger.info("using v1")
        return Response(serializer.data)



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
