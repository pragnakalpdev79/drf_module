from typing import List
import strawberry
import strawberry_django
from strawberry import auto
from .models import Book

@strawberry_djangp.type(Book)
class BookType:
    id: auto
    title: auto
    author: auto
    published_date: auto

@strawberry.type
class Query:
    books = List[BookType] = strawberry_django.field()

schema = strawberry.Schema(query=Query)