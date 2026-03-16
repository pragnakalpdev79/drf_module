import logging
from django.shortcuts import render
from django.contrib.auth.mixins import UserPassesTestMixin
from rest_framework import generics,status
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from user.models import RestrauntModel
from user.permissions import IsRestaurantOwner
from .serializers import RestoListSerializer

logger = logging.getLogger('user')

class RestoListView(APIView):
    permission_classes = [AllowAny]
    def get(self,request):
        tolist = RestrauntModel.objects.all()
        serializers = RestoListSerializer(tolist,many=True)
        return Response(serializers.data,status=status.HTTP_200_OK)


class RestoCreateView(APIView):

    # def test_func(self):UserPassesTestMixin
    #     print(self.request.user.has_perm("add_restrauntmodel"))
    #     return self.request.user.has_perm("add_restrauntmodel")
    
    permission_classes = [IsRestaurantOwner]
    def get(self,request):
        return Response({
            "message" : "permissions works!",
        })
