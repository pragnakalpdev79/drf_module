from rest_framework import viewsets,status
from rest_framework.response import Response
from rest_framework.views import exception_handler
from .models import Book,Task,Author,Product
from .serializers import BookSerializer,TaskSerializer,AuthorSerializer,ProductSerializer

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

# EXERCISE 1 - BOOK - BookViewSet
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

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

# EXERCISE 3 - AUTHOR - AuthorViewSet
class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

    def create(self,request,*args,**kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(
            {
                'success' : True,
                'message': 'You have successfully registered a new author',
                'data' : serializer.data
            },
            status = status.HTTP_201_CREATED
        )

#EXERCISE 5 PRODUCT API VIEW
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    