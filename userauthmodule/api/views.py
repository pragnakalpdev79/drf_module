import os
from rest_framework import viewsets,status,generics,filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticatedOrReadOnly,IsAuthenticated
from rest_framework.parsers import MultiPartParser,FileUploadParser
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth.models import User
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from .serializers import *
from .models import *

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = []
    def create(self,request,*args,**kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)

        return Response({
            'user' : serializer.data,
            'refresh' : str(refresh),
            'access': str(refresh.access_token),
        },status=status.HTTP_201_CREATED)
    
class TaskViewSet(viewsets.ModelViewSet):
    permisssion_classes = [IsAuthenticated]
    #serializer_class = TaskSerializer

    def get_serializer_class(self):
        if self.request.version == 'v1':
            return TaskSerializer
        return TaskSerializer

    def get_queryset(self):
        # cache_key = f'tasks_under_{self.request.user.id}'
        # queryset = cache.get(cache_key)
        # if queryset is None:
        queryset = Task.objects.select_related('owner').filter(owner=self.request.user.id)
        #     cache.set(cache_key,queryset,300)
        # print("QUERYSET:---------",queryset)
        return queryset
    
    def perform_create(self,serializer):                                        
        print(self.request.user)
        serializer.save(owner=self.request.user)

    def create(self,request,*args,**kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        print(serializer.data)
        return Response({
            'sucess': True,
            'message' : 'Task Created Sucessfully',
            'data': 'serializer.data'
        },status=status.HTTP_201_CREATED)

class TaskAttachmentViewSet(viewsets.ModelViewSet):
    queryset = TaskAttachment.objects.all()
    serializer_class = TaskAttachmentSerializer
    permission_classes = [IsAuthenticated]

    @action(
            detail=True,
            methods=['POST'],
            parser_classes=[FileUploadParser],
            url_path=r"upload/(?P<filename>[a-zA-Z0-9_]+\.txt)"
    )
    def upload_file(self,request,**kwargs):
        task = self.get_object()
        os.systme('clear')
        print(task)
        if "file" not in request.data:
            raise ValidationError("There is no file in thev http body")
        file = request.data['file']
        task.file.save(file.name,file)
        return Response(TaskAttachmentSerializer(task).data)
    
# class HarryPotterViewSet(viewsets.ModelViewSet):

