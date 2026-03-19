from django.shortcuts import render
from rest_framework import status,viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from user.models import *
from user.permissions import IsRestaurantOwner,IsCustomer,IsDriver
from .serializers import *


logger = logging.getLogger('user')

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @action(detail=False,methods=['post'],permission_classes=[IsCustomer])
    def place(self,request):
        #print(request.user.objects.prefetch_related('user_s_adress'))
        user = CustomUser.objects.get(id=request.user.id)
        dadr = user.customer_profile.default_adress.address
        #serializer = CustomUser
    
        return Response({
            "message" : "It works",
            "delivery address" : dadr, 
        })
