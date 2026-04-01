import logging
from django.shortcuts import render
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.cache import cache
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema,extend_schema_view,OpenApiParameter
from rest_framework import generics,status,viewsets,permissions,renderers,filters
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny,IsAuthenticatedOrReadOnly,IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from user.models import RestrauntModel
from user.permissions import IsRestaurantOwner
from .serializers import *
from .pagination import RestoPagination,MenuItemPagination
from .filters import RestoFilter

logger = logging.getLogger('user')


@extend_schema_view(
    list=extend_schema(
        summary=" R.1 List of all restaurants",
        description="You can get a list of all restaurants available here",
        tags=["Restaurants"],
        # parameters=[
        #     OpenApiParameter("test",RestoListSerializer)
        # ],
        responses=RestoListSerializer,
        auth=[],
    ),
    retrieve=extend_schema(
        summary=" R.2 Get details of a restaurant",
        description="Pass the restaurant id to get all details about it",
        tags=["Restaurants"],
        auth=[],
    ),
    create=extend_schema(
        summary="R.3 Register Your restaurant",
        description="Enter your restaurant details and register a new one,this endpoint can be only accesed if you are a restaurnt owner" \
        " [Restaurant Owner Permission Required]",
        tags=["Restaurants"],
        auth=[{"tokenAuth": [], }],
    ),
    menu=extend_schema(
        summary=" R.4 Get Menu from a restaurant id",
        description="Pass Restaurant id to get its menu",
        tags=["Restaurants"],
        auth=[],
    ),
    popular=extend_schema(
        summary=" R.5 Check popular restaurants",
        description="Endpoint to fetch popular restaurants ordered by top rated",
        tags=["Restaurants"],
        auth=[],
    ),
    deleter=extend_schema(
        summary=" R.6 Delete a restaurant",
        description="Can be only accessed if user has restaurant owner permission",
        tags=["Restaurants"],
        auth=[{"tokenAuth": [], }],
    ),
    partial_update=extend_schema(
        summary=" R.7 Update restaurant details",
        description="Can be only accessed if user has restaurant owner permission",
        tags=["Restaurants"],
        auth=[{"tokenAuth": [], }],
    )
)
class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = RestrauntModel.objects.filter(deleted_at=None).annotate(items_count=Count('delivery_fee'))
    http_method_names = ['get', 'post','patch']
    #filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    #filterset_fields = ['cuisine_type','is_open','delivery_fee__lte','minimum_order__lte','average_rating__gte']
    pagination_class = RestoPagination
   # search_fields = ['name','cuisine_type']
    filterset_class = RestoFilter

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
        if self.action == 'deleter':
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

#6. DELETE A RESTO
    @action(detail=True,methods=['get'])
    def deleter(self,request,pk):
        print(request.user)
        resto = self.get_queryset().get(id=pk)
        print(type(resto))
        resto.delete()
        return Response({
            "message" : request.user.email
        })


#==============================================================================
#==============================================================================

class MenuItemViewSet(viewsets.ModelViewSet):
    #queryset = MenuItem.objects.all()
    permission_classes = [IsRestaurantOwner]
    serializer_class = MenuSerializer

    def get_queryset(self):
        user = self.request.user
        #if 
        qs = MenuItem.objects.filter().select_related('restaurant')
        return qs
    
    def create(self,request):
        test = self.get_queryset().first()

        return Response({
            "message": "worked",
            "email": request.user.email,
        })

    def perform_create(self,serializer):
        serializer.save()
