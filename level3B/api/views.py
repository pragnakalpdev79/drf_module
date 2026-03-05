from rest_framework import viewsets,status,generics,filters
from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .models import *
from .serializers import *
import os
from rest_framework.permissions import IsAuthenticatedOrReadOnly,IsAuthenticated
from .permissions import IsOwnerOrReadOnly
from .throttles import BookCreateThrottle
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .filters import TaskFilter,BookFilter
from django.db.models import Count
from .tasks import send_post_notification

#====================================================================================
# REGISTRATION VIEW 
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
#====================================================================================
# USER-PROFILE VIEW SET 
class UserProfileViewSet(viewsets.ModelViewSet):
    serialzer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)
    def perform_create(self,serializer):
        serializer.save(user=self.request.user)

#====================================================================================
# BOOK VIEW SET
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
#====================================================================================
# TASK VIEW SET
class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    queryset = Task.objects.all() #takes 4 queroes to list tasks    
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
    
    def get_queryset(self):
        queryset = Task.objects.select_related('owner','category').prefetch_related(
            'assigned_to'
        ).filter(owner=self.request.user)
        if self.request.query_params.get('overdue') == 'true':
            from django.utils import timezone 
            queryset = queryset.filter(due_date__lt=timezone.now(),completed=False)

        return queryset

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
#====================================================================================
# POST VIEW SET
class PostViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = PostSerializer
    filter_backends = [DjangoFilterBackend,filters.SearchFilter,filters.OrderingFilter]
    filterset_fields = ['published','author']
    search_fields = ['title','content']
    ordering_fields = ['created_at','title']
    ordering = ['-created_at']

    def get_queryset(self):
        return Post.objects.select_related('author').prefetch_related(
            'tags'
            'comments',
            'comments__author'
        ).annotate(comment_count=Count('comments')).all()
    
    # def perform_create(self,serializer):
    #     serializer.save(author=self.request.user)
    #     send_post_notification.delay(post.id) #---> Aynsc Task

    # def create(self,request,*args,**kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)
    #     return Response(
    #         {
    #             'success':True,
    #             'message':'New Post Published',
    #             'data':serializer.data
    #         },
    #         status = status.HTTP_201_CREATED
    #     )
#====================================================================================
# TAG VIEW SET
class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
#====================================================================================
# COMMENT VIEW SET
class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        post_id = self.request.query_params.get('post',None)
        queryset = Comment.objects.select_related('author','post').all()
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        return queryset
    
    def perform_create(self,serializer):
        post_id = serializer.validated_data.get('post_id')
        serializer.save(author=self.request.user,post_id=post_id)


