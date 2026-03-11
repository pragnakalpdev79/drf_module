from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import *
from .serializers import *
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token

@api_view(['GET'])
def get_books(request):
    book_objs = Book.objects.all()
    serializer = BookSerializer(book_objs,many=True)
    return Response({
        'status' : 200,
        'payload' : serializer.data
    })
    