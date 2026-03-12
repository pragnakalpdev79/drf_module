from django.shortcuts import render
from rest_framework import viewsets,status,generics,filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Actor
from .serializers import ActorSerializer
from .pagination import MyLimitOffsetPagination,MyCursorPagination

class ActorViewSet(viewsets.ModelViewSet):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer
    pagination_class = MyLimitOffsetPagination #OVER-RIDSES THE DEFAULT IMPLEMENTED PAGE-NUMBERPAGINATION