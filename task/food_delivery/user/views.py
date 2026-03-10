import os
from django.shortcuts import render
from rest_framework import generics,status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
from .serializers import CustomUserRegistrationSerializer


class UserRegisterationView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserRegistrationSerializer
    permission_classes = []
    
    def create(self,request,*args,**kwargs):
        os.system('clear')
        print("`````````````````````````````````````````````````p1-entering the view `````````````````````````````````````````````````")
        print("`````````````````````````````````````````````````p2-create function intiated `````````````````````````````````````````````````")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        print("`````````````````````````````````````````````````p2.1-serialzer validation successful`````````````````````````````````````````````````")
        user = serializer.save()
        print("`````````````````````````````````````````````````p2.3 -serialzer save successful`````````````````````````````````````````````````")
        refresh = RefreshToken.for_user(user)
        print("`````````````````````````````````````````````````p2.4 token generation successful`````````````````````````````````````````````````")
        print(user)
        serializer.data.pop('password')
        return Response( {
            'user' : serializer.data,
            'refresh' : str(refresh),
            'access' : str(refresh.access_token),
        },status=status.HTTP_201_CREATED
        )

    
    