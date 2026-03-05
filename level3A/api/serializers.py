from rest_framework import serializers,status
from rest_framework.response import Response
from .models import *
from django.contrib.auth.models import User
import os

#===================================================================
# USER-REGISTRATION SERIALIZER
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['username','email','password','password_confirm','first_name','last_name']
    def validate(self,data):
        os.system('clear')
        print("validating data")
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError('Passwords dont match')
        print(data)
        return data
    def create(self,validated_data):
        print("stage 3.1")
        validated_data.pop('password_confirm')
        os.system('clear')
        print(validated_data)
        user = User.objects.create_user(**validated_data)
        return user
#===================================================================
# USER-PROFILE SERIALIZER
class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username',read_only=True)
    email = serializers.EmailField(source='user.email',read_only=True)

    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ['id','created_at','updated_at']
#===================================================================
# BOOK SERIALIZER
class BookSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source='owner.username',read_only=True)

    class Meta:
        model = Book
        fields = '__all__'
        read_only_fields = ['id','created_at','updated_at','owner']
#===================================================================
# TASK SERIALIZER
class TaskSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source='owner.username',read_only=True)
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['id','created_at','updated_at','owner']
#===================================================================
# POST SERIALIZER
class PostSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username',read_only=True)
    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = ['created_at','author']
#===================================================================
# TAG SERIALIZER
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['name']
#===================================================================
# COMMENT SERIALIZER
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = []