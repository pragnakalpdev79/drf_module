import strawberry
from strawberry.django import DjangoModelType
#from strawberry.django.auth import login, logout
from strawberry.types import Info
from .models import Task,Book
from django.contrib.auth.models import User

@strawberry.type
class Mutation:
    @strawberry.mutation
    def login(self,info:Info,username:str,password:str) -> bool:
        from django.contrib.auth import authenticate
        user = authenticate(username=username,password=password)
        if user:
            login(info.context.request,user)
            return True
        return False


@strawberry.django.type(Task)
class TaskType(DjangoModelType):
    class Meta:
        model = Task
        fields = ['id','title','desc','completed','created_at']

@strawberry.django.type(Book)
class BookType(DjangoModelType):
    model = Book
    fields = ['id','title','author','published_date']

@strawberry.type
class Query:
    @strawberry.field
    def tasks(self) -> list[TaskType]:
        return Task.objects.all()
    
    @strawberry.field
    def task(self,id:int) -> TaskType:
        return Task.objects.get(id=id)
    
    @strawberry.field
    def books(self) -> list[BookType]:
        return Book.objects.all()
    
@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_task(self,title: str,desc: str = None) -> TaskType:
        task = Task.objects.create(title=title,desc=desc)
        return task
    
    @strawberry.mutation
    def update_task(self,id: int,completed: bool) -> TaskType:
        task = Task.objects.get(id=id)
        task.completed = completed
        task.save()
        return task
    
schema = strawberry.Schema(query=Query,mutation=Mutation)