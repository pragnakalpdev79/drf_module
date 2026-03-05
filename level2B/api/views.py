from rest_framework import viewsets,status,generics,filters
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
from django_filters.rest_framework import DjangoFilterBackend
from .filters import TaskFilter,BookFilter
#from .pagination import BookLimitOffsetPagination


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly,IsOwnerOrReadOnly]
    #throttle_classes = [BookCreateThrottle]
    filter_backends = [DjangoFilterBackend,filters.SearchFilter,filters.OrderingFilter]
    filterset_class = BookFilter
    search_fields = ['title','author','description']
    ordering_fields = ['title','author','published_date','created_at']
    ordering = ['-created_at']
    def get_throttles(self):
        if self.action =='create':
            return [BookCreateThrottle()]
        return super().get_throttles()

    def perform_create(self,serializer):
        serializer.save(owner=self.request.user)

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    queryset = Task.objects.all()
    filterset_class = TaskFilter
    filter_backends = [filters.SearchFilter,filters.OrderingFilter]
    ordering_fields = ['title','completed','created_at','updated_at']
    ordering = ['-created_at']
    search_fields = ['title','desc']
    permission_classes = [IsAuthenticated]
    #pagination_class = BookLimitOffsetPagination
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
    # if this is implemented it overrides the filter settings...
    # def list(self,request,*args,**kwargs):
    #     queryset = self.filter_queryset(self.get_queryset())
    #     serializer = self.get_serializer(queryset,many=True)

    #     return Response(
    #         {
    #             'count' : queryset.count(),
    #             'message' : 'This is a custom response', #EXERCISE 4 INCLUDING CUSTOM RESPONSE FORMAT
    #             'results': serializer.data
    #         }
    #     )

    
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
    
