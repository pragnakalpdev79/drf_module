import logging
from django.shortcuts import render
from django.contrib.auth.models import Group
from rest_framework import generics,status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
from .serializers import CustomUserRegistrationSerializer


logger = logging.getLogger(__name__)

class UserRegisterationView(generics.CreateAPIView):
    serializer_class = CustomUserRegistrationSerializer
    permission_classes = [AllowAny]
    
    #POST METHOD
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

        if user.check_if_customer:
            group = Group.objects.get(name='Customers')
        if user.check_if_restaurant:
            group = Group.objects.get(name='RestrauntOwners')
        if user.check_if_driver:
            group = Group.objects.get(name='Drivers')

        perm_user = CustomUser.objects.get(email=user.email)
        perm_user.groups.add(group)

        logger.info(f"{perm_user} added to group {group}")

        return Response( {
            'user' : serializer.data.get("email"),
            'refresh' : str(refresh),
            'access' : str(refresh.access_token),
        },status=status.HTTP_201_CREATED
        )

    

class DeleteUser(APIView):
    queryset = CustomUser
    permission_classes = [AllowAny] #FOR TESTING ONLY
    def delete(self,request,uname):
        logger.info("===========================================DELETE 1 -entering the view ======================================================")
        #uname=self.request.GET.get('uname',None)
        if uname is not None:
            try:
                user = CustomUser.objects.get(username=uname)
                logger.info("===========================================D1.1-USER FOUND  ======================================================")
            except CustomUser.DoesNotExist:
                logger.info("===========================================D1.1 -USER DOES NOT EXISTS ======================================================")
                return Response({
                    "error" : "The Requested User does not exist" 
                })
            user.delete
        logger.info("===========================================D1.2-USER FOUND AND DELETED ======================================================")
        return Response({
            'message' : 'User has been deleted',
        })