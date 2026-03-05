import os
import requests
import json
import asyncio
import aiohttp
from rest_framework import viewsets,status,generics,filters
from rest_framework.response import Response
from rest_framework.views import exception_handler,APIView
from rest_framework_simplejwt.tokens import RefreshToken 
from rest_framework.permissions import IsAuthenticatedOrReadOnly,IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets
from django.core.cache import cache
from django.contrib.auth.models import User
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from django.http import JsonResponse
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from drf_spectacular.utils import extend_schema,OpenApiParameter
from .models import *
from .serializers import *
from .permissions import IsOwnerOrReadOnly
from .throttles import BookCreateThrottle
from .filters import TaskFilter,BookFilter
from .tasks import send_post_notification
from .services import ExternalAPIService


#===================================================================
#CUSTOM SCHEMA
class TaskViewSet(viewsets.ModelViewSet):
    @extend_schema(
        summary='List Tasks',
        description="Get a list of all tasks",
        parameters=[
            OpenApiParameter(
                name='completed',
                description='Filter by completeion status',
                required=False,
                type=bool
            )
        ],
        responses={200:TaskSerializer(many=True)}
    )
    def list(self,request):
        return super().list(request)
    


#====================================================================================
# ASYNC IN DJANGO
async def async_external_api_call():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://hp-api.onrender.com/api/characters/') as response:
            return await response.json()
# ASYNC FBV
async def async_task_list(request):
    os.system('clear')
    print("calling external api")
    data = await async_external_api_call()
    print(data[0].get('name'))
    print(data[0].get('house'))
    print(data[0].get('actor'))
    print(data[0].get('species'))
    print(data[0].get('patronus'))
    print(data[0].get('dateOfBirth'))
    print(data[0].get('alive'))
    print(data[0].get('image'))
    return JsonResponse(data[0])
# ASYNC CBV
@method_decorator(csrf_exempt,name='dispatch')
class AsyncHPView(View):
    async def get(self,request):
        data = await async_external_api_call()
        return JsonResponse(data)
    async def post(self,request):
        body = json.loads(request.body)
        return JsonResponse({'status':'created'})
#====================================================================================
# ASYNC IN DRF
class AsyncBookView(APIView):
    async def get(self,request):
        data = await asyncio.gather(
            self.fetch_books(),
            self.fetch_authors(),
        )
        return Response({
            'books': data[0],
            'authors' : data[1]
        })
    async def fetch_books(self):
        await asyncio.sleep(1)
        return list(Book.objects.values())
#====================================================================================
# CHARACTERS
class CharacterView(APIView):
    async def get(self,request):
        data = await async_external_api_call()
        return JsonResponse(data)
    
    
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
#@method_decorator(cache_page(60*15),name='dispatch')
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
    
    def list(self,request,*args,**kwargs):
        cache_key = 'books_list'
        cached_data = cache.get(cache_key)
        if cached_data is None:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset,many=True)
            cached_data = serializer.data
            cache.set(cache_key,cached_data,300)
    
    def create(self,request,*args,**kwargs):
        response = super().create(request,*args,**kwargs)
        cache.delete('book_list')
        return response
#====================================================================================
# TASK VIEW SET
class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    #queryset = Task.objects.all() #takes 4 queroes to list tasks    
    filterset_class = TaskFilter
    filter_backends = [DjangoFilterBackend,filters.SearchFilter,filters.OrderingFilter]
    filterset_fields =['title','desc']
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
# TASK VIEW SET
class TaskAttchmentViewSet(viewsets.ModelViewSet):
    queryset = TaskAttachment.objects.all()
    serializer_class = TaskAttachmentSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False,methoda=['post'],url_path='upload')
    def upload_file(self,request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)
    
    @action(detail=True,methods=['post'])
    def sync_external(self,request,pk=None):
        task = self.get_object()
        service = ExternalAPIService()
        try:
            data = service.post_data(
                'tasks',
                {
                    'title' : task.title,
                    'decription' : task.desc,
                }
            )
            return Response({
                'status' : 'synced',
                'external_id' : data['id']
            }
            )
        except requests.exceptions.RequestException as e:
            return Response({'error': str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    


#====================================================================================
# POST VIEW SET
class PostViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = PostSerializer
    filter_backends = [DjangoFilterBackend,filters.SearchFilter,filters.OrderingFilter]
    filterset_fields = ['author']
    search_fields = ['title','content']
    ordering_fields = ['created_at','title']
    ordering = ['-created_at']

    def get_queryset(self):
        return Post.objects.select_related('author').prefetch_related(
            'tags'
            'comments',
            'comments__author'
        ).annotate(comment_count=Count('comments')).all()
    
    def perform_create(self,serializer):
        post = serializer.save()
        send_post_notification(post.id) #---> Aynsc Task

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


