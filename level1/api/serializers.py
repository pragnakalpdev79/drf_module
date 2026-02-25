from rest_framework import serializers,status
from rest_framework.response import Response
from .models import Book,Task,Author,Product

# EXERCISE 1 - BOOK - BookSerializer
class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'
        read_only_fields = ['id','created_at']


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['id','created_at','updated_at']


# EXERCISE 3 - AUTHOR - AuthorSerializer
class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'

# EXERCISE 5 - PRODUCT API - Serializer
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['id','created_at','updated_at']
    def validate(self,data):
        if data['stock'] <= 0:
            raise serializers.ValidationError("The stock must be a postive number")
        if data['price'] <= 0:
            raise serializers.ValidationError("The price must be greater then zero")
        return data
        