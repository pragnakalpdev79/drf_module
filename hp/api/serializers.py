from rest_framework import serializers
from .models import *
import os

#===================================================================
# USER-REGISTRATION SERIALIZER
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['username','email','password','password_confirm','first_name','last_name']
    #VALIDATION
    def validate(self,data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError('Passwords dont match')
        return data
    #CREATING THE USER AND REMOVING EXTRA CONFIRM PASSWORFD FIELD
    def create(self,validated_data):
        os.system('clear')
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        print(user)
        return user


#===================================================================
# USER SERIALIZER
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','email']
#===================================================================
# CATEGORY SERIALIZER  
class CategorySerializer(serializers.ModelSerializer):
    task_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id','name','color','task_count','created_at']
        read_only_fields = ['id','created_at']

    def get_task_count(self,obj):
        return obj.tasks.count()
#===================================================================
# TASK SERIALIZER
#----------------------
# SERIALIZER V1
class TaskSerializerV1(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True,required=False,allow_null=True)
    assigned_to = UserSerializer(many=True,read_only=True)
    assigned_to_ids = serializers.ListField(
        child = serializers.IntegerField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Task
        # fields = ['id', 'title', 'desc', 'completed', 'priority', 'due_date','deleted',
        #           'owner', 'category', 'category_id', 'assigned_to', 'assigned_to_ids',
        #            'created_at', 'updated_at']
        fields = '__all__'
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at','deleted']
#----------------------
# SERIALIZER V2
class TaskSerializerV2(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True,required=False,allow_null=True)
    assigned_to = UserSerializer(many=True,read_only=True)
    assigned_to_ids = serializers.ListField(
        child = serializers.IntegerField(),
        write_only=True,
        required=False
    )
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'title', 'desc', 'completed', 'priority', 'due_date',
                  'owner', 'category', 'category_id', 'assigned_to', 'assigned_to_ids',
                  'is_overdue', 'created_at', 'updated_at']
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']
    # DUE DATE VALIDATION
    def get_is_overdue(self,obj):
        if obj.due_date and not obj.completed:
            from django.utils import timezone
            return obj.due_date < timezone.now()
        return False
    
    def create(self,validated_data):
        assigned_to_ids = validated_data.pop('assigned_to_ids',[])
        category_id = validated_data.pop('category_id',None)
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required to create tasks")
        task = Task.objects.create(owner=request.user,**validated_data)

        if category_id is not None:
            task.category_id = category_id
            task.save()

        if assigned_to_ids:
            task.assigned_to.set(self.assigned_to_ids)
    
    def update(self,instance,validated_data):
        self.assigned_to_ids = validated_data.pop('assigned_to_ids', None)
        self.category_id = validated_data.pop('category_id',None)
        instance.title = validated_data.get('title', instance.title)
        instance.desc = validated_data.get('desc', instance.desc)
        instance.completed = validated_data.get('completed', instance.completed)
        instance.priority = validated_data.get('priority', instance.priority)
        instance.due_date = validated_data.get('due_date', instance.due_date)
        if self.category_id is not None:
            instance.category_id = self.category_id

        instance.save()

        if self.assigned_to_ids is not None:
            instance.assigned_to.set(self.assigned_to_ids)
        return instance
    
    def validate_image(self,value):
        if value:
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError("Image size cannot exceed 5 mb")
            from PIL import Image
            try:
                img = Image.open(value)
                img.verify()
            except Exception:
                raise serializers.ValidationError("Invalid Image Format")
        return value
 