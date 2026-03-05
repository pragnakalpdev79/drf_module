from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords dont match")
        return data
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user

class UserSerilizer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','email']    

class TaskSerializer(serializers.ModelSerializer):
    owner = UserSerilizer(read_only=True)
    assigned_to = UserSerilizer(many=True,read_only=True)
    assigned_to_ids = serializers.ListField(
        child = serializers.IntegerField(),
        write_only=True,
        required=False
    )
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['id']

class TaskAttachmentSerializer(serializers.ModelSerializer):
    #file_size = serializers.SerializerMethodField()
    #file_type = serializers.SerializerMethodField()
    #file = serializers.FileField()
    class Meta:
        model = TaskAttachment
        fields = '__all__'
        read_only_fields = ['id','uploaded_at']
    
    def get_file_size(self,obj):
        if obj.file:
            return obj.file.size
        return None
    
    def get_file_type(self,obj):
        if obj.file:
            return obj.file.name.split('.')[-1].upper()
        return None
    
    def validate_file(self,value):
        max_size = 10 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError("File size cannot exceed 10mb")
        
        allowed_types = ['pdf','doc','docs','jpg','jpeg','png']
        file_ext = value.name.split('.')[-1].lower()
        if file_ext not in allowed_types:
            raise serializers.ValidationError(f"File type not allowed, ALLowed: {allowed_types}")
        
        return value


