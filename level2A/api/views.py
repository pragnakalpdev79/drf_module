from rest_framework import viewsets,status,generics
from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .models import Book,Task,UserProfile
from .serializers import BookSerializer,TaskSerializer,UserRegistrationSerializer,UserProfileSerializer
import os
from rest_framework.permissions import IsAuthenticatedOrReadOnly,IsAuthenticated
from .permissions import IsOwnerOrReadOnly
from .throttles import BookCreateThrottle
from rest_framework.decorators import action

def custom_exception_handler(exc,context):
    response = exception_handler(exc,context)

    if response is not None:
        custom_response_data = {
            'error': {
                'status_code' : response.status_code,
                'message' : 'An error occured',
                'details' : response.data
            }
        }
        response.data = custom_response_data
    return response

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly,IsOwnerOrReadOnly]
    #throttle_classes = [BookCreateThrottle]
    def get_throttles(self):
        if self.action =='create':
            return [BookCreateThrottle()]
        return super().get_throttles()

    def perform_create(self,serializer):
        serializer.save(owner=self.request.user)

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user)
    def perform_create(self,serializer):
        print(self.request.user)
        serializer.save(owner=self.request.user)
    
    def create(self,request,*args,**kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {
                'success':True,
                'message':'Task created successfully',
                'data':serializer.data
            },
            status = status.HTTP_201_CREATED
        )
    def list(self,request,*args,**kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset,many=True)

        return Response(
            {
                'count' : queryset.count(),
                'message' : 'This is a custom response', #EXERCISE 4 INCLUDING CUSTOM RESPONSE FORMAT
                'results': serializer.data
            }
        )
    
class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = []
    def create(self,request,*args,**kwargs):
        os.system('clear')
        print("stage1")
        serializer = self.get_serializer(data=request.data)
        print("stage2")
        serializer.is_valid(raise_exception=True)
        print("stage3")
        user = serializer.save()
        print("stage4")
        refresh = RefreshToken.for_user(user)
        print("stage5")
        return Response({
            'user': serializer.data,
            'refresh': str(refresh),
            'access' : str(refresh.access_token),
        },status=status.HTTP_201_CREATED
        )
    
class UserProfileViewSet(viewsets.ModelViewSet):
    serialzer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)
    def perform_create(self,serializer):
        serializer.save(user=self.request.user)
    
