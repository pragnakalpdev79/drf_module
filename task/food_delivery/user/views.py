import logging
from django.shortcuts import render
from django.contrib.auth.models import Group,Permission
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample, OpenApiResponse
from rest_framework import generics,status,viewsets,filters
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser,address
from .serializers import *


logger = logging.getLogger('user')

#===============================================================================================
#===============================================================================================
# USER-RELAYTED VIEWS
# 1.REGISTRATION - Allowany
# 2.LOGIN - Allowany
# 3.LOGOUT - Logged in user only
# 4. DELETE USER VIEW -Admin only
# 5. RESTORE USER VIEW - Admin Only

# 1.REGISTRATION - Allowany
class UserRegisterationView(generics.CreateAPIView):

    """
    API endpoint for new user registration.
    """
    #generics.CreateAPIView inherits from APIView
    #Extends with mixin CreateModelMixin
    #Specifcialy to handle create_only post method handler
    #only works with post requests
    serializer_class = CustomUserRegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self,request,*args,**kwargs):
        """
        API endpoint for new user registration. 123
        """
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
        #print(user.utype)
        perm_user = CustomUser.objects.get(email=user.email)

        if user.check_if_customer:
            group = Group.objects.get(name='Customers')
            # perm_user = CustomUser.objects.get(email=user.email)
            perm_user.groups.add(group)
            logger.info(f" {group}==>{perm_user}")
            # print(group,'==>',perm_user)
            #print(user.has_perm('user.IsRestaurantOwner'))
        if user.check_if_restaurant:
            group = Group.objects.get(name='RestrauntOwners')
            # perm_user = CustomUser.objects.get(email=user.email)
            perm_user.groups.add(group)
            logger.info(f" {group}==>{perm_user}")
            # print(group,'==>',perm_user)
            #print(user.has_perm('user.IsRestaurantOwner'))
        if user.check_if_driver:
            group = Group.objects.get(name='Drivers')
            # perm_user = CustomUser.objects.get(email=user.email)
            perm_user.groups.add(group)
            logger.info(f" {group}==>{perm_user}")
            # print(group,'==>',perm_user)

        # permissions = Permission.objects.filter(user=perm_user)
        # permissions = perm_user.get_user_permissions()
        # print("===================",permissions,"===============")
        # print(perm_user.groups)

        logger.info(f"{perm_user} added to group {group}")

        return Response( {
            'user' : serializer.data.get("email"),
            'message' : f"You have been successfully registered as a {group}",
            'refresh' : str(refresh),
            'access' : str(refresh.access_token),
        },status=status.HTTP_201_CREATED
        )
    
# 2.LOGIN - Allowany
class UserLoginView(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        logger.info("===========================================p2 -entering the Login-view ======================================================")
        serializer = CustomUserLoginSerializer(data=request.data)
        # print(serializer)
        serializer.is_valid(raise_exception=True)
        logger.info('p2.1   DATA FROM REQUEST VALIDATED AND IS VALID        ')
        # print(serializer.validated_data)
        logger.info("p2.2   authentication request for the following user  {serializer.validated_data['user']}      ")
        logger.info(f"p2.2         ")
        refresh = RefreshToken.for_user(serializer.validated_data['user'])
        return Response({
            'user' : serializer.validated_data['email'],
            'refresh' : str(refresh),
            'access' : str(refresh.access_token),
        },status=status.HTTP_201_CREATED)

# 3.LOGOUT - Logged in user only
class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        logger.info("===========================================entering the Logout-view ======================================================")
        try:
            refresh_token = request.data["refresh_token"]
            #print("db1")
            token = RefreshToken(refresh_token)
            #print("db2")
            token.blacklist()
            #print("db3")
            logger.info("Logout success")
            return Response({
                'message' : 'Log out successful',
            },status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            logger.info(f"An error occured in log out == {e}")
            return Response({
                'error' : 'something went wrong'
            },status=status.HTTP_400_BAD_REQUEST)

# 4. DELETE USER VIEW -Admin only
class DeleteUser(APIView):
    queryset = CustomUser
    permission_classes = [IsAdminUser] #FOR TESTING ONLY
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

# 5. RESTORE USER VIEW - Admin Only
class RestoreDeletedUserView(APIView):
    permission_classes = [IsAdminUser]

    def post(self,request,uname):
        logger.info("===========================================RESTORE 1 -entering the RESTORE view ======================================================")
        if uname is not None:
            try:
                user = CustomUser.all_objects.get(username=uname)
                logger.info("===========================================R1.1-USER FOUND  ======================================================")
            except CustomUser.DoesNotExist:
                logger.info("===========================================R1.1 -USER DOES NOT EXISTS ======================================================")
                return Response({
                    "error" : "The Requested User does not exist" 
                })
            user.restore
        logger.info("===========================================R1.2-USER FOUND AND DELETED ======================================================")
        
        return Response({
            'message' : 'User has been restored',
        })
    
#===============================================================================================
#===============================================================================================

