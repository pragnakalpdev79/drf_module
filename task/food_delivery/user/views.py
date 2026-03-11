import logging
from django.shortcuts import render
from django.contrib.auth.models import Group
from rest_framework import generics,status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
from .serializers import CustomUserRegistrationSerializer

logger = logging.getLogger(__name__)

class UserRegisterationView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserRegistrationSerializer
    permission_classes = []
    
    def create(self,request,*args,**kwargs):
        logger.info("===========================================p1-entering the view ======================================================")
        logger.info("p2-create function intiated")
        serializer = self.get_serializer(data=request.data)
        logger.info("Rasining an exception!")
        serializer.is_valid(raise_exception=True)
        logger.info("Raised!")
        logger.info("p2.1-serialzer validation successful ")
        user = serializer.save()
        logger.info("p2.3 -serialzer save successful")
        refresh = RefreshToken.for_user(user)
        logger.info("p2.4 token generation successful` ")
        logger.info("===========================================RETURNING THE RESPONSE ======================================================")
        print(user.utype)
        if user.utype == 'c':
            perm_user = CustomUser.objects.get(email=user.email)
            group = Group.objects.get(name='Customers')
            perm_user.groups.add(group)
            logger.info(f"{perm_user} added to group {group}")
        if user.utype == 'r':
            perm_user = CustomUser.objects.get(email=user.email)
            group = Group.objects.get(name='RestrauntOwners')
            perm_user.groups.add(group)
            logger.info(f"{perm_user} added to group {group}")
        if user.utype == 'd':
            perm_user = CustomUser.objects.get(email=user.email)
            group = Group.objects.get(name='Drivers')
            perm_user.groups.add(group)
            logger.info(f"{perm_user} added to group {group}")

        return Response( {
            'user' : serializer.data.get("email"),
            'refresh' : str(refresh),
            'access' : str(refresh.access_token),
        },status=status.HTTP_201_CREATED
        )

    
    