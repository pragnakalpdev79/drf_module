from .services import ExternalAPIService
from .models import *
from .serializers import *
from rest_framework import viewsets,status,generics,filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly,IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken 

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
        },status=status.HTTP_201_CREATED
        )



class HpViewSet(viewsets.ModelViewSet):
    @action(detail=True,methods=['get'])
    def sync_external(self,request,pk=None):
        service = ExternalAPIService()

        try:
            data = service.get_data('characters')
            return Response({'status':'sucessful',
                             'characters': data,
                             })
        except request.exceptions.RequestException as e:
            return Response({'error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class TaskViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    #versioning
    def get_serializer_class(self):
        version = self.request.version
        if version == 'v1':
            print("---------------selected serializer v1----------------")
            return TaskSerializerV1
        elif version == 'v2':
            print("---------------selected serializer v1----------------")
            return TaskSerializerV2
        else:
            return TaskSerializerV1
    def get_queryset(self):
        queryset = Task.objects.select_related('owner','category').prefetch_related('assigned_to').filter(owner=self.request.user)
        if self.request.query_params.get('overdue') == 'true':
            from django.utils import timezone
            queryset = queryset.filter(due_date__lt=timezone.now(),completed=False)
    def perform_create(self,serializer):
        os.system('clear')
        print(self.request.user)
        serializer.save(owner=self.request.user.id)
    def create(self,request,*args,**kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_Create(serializer)
        return Response({
            'sucess' : True,
            'message' : 'Task Created Sucessfully',
            'data' : 'serializer.data'
        },status = status.HTTP_201_CREATED
        )