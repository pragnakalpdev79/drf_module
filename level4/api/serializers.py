from rest_framework import serializers
from .models import *
import os

#-------------------------------------------------------------------------
# Custom Upper-Case Field
class UppercaseCharField(serializers.CharField):
    def to_represenation(self,value):
        return super().to_representation(value).upper() if value else value
#-------------------------------------------------------------------------
# Custom Age Field with Validation
class AgeField(serializers.IntegerField):
    def to_internal_value(self,data):
        age = super().to_internal_value(data)
        if age < 0 or age > 150:
            raise serializers.ValidationError("Age must be between 0 & 150")
        return age
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
    age = AgeField()

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
# AUTHOR SERIALIZER
class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','first_name','last_name']
#===================================================================
# TAG SERIALIZER
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id','name']
#===================================================================
# COMMENT SERIALIZER
class  CommentSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    post_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = Comment
        fields = ['id','content','post_id','author','created_at']
        read_only_fields = ['id','author','created_at']
#===================================================================
# POST SERIALIZER
class PostSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    tags = TagSerializer(many=True,required=False)
    comments = CommentSerializer(many=True,read_only=True)
    comment_count = serializers.SerializerMethodField()
    title = UppercaseCharField()


    class Meta:
        model = Post
        fields = ['id','title','content','author','tags','comments','comment_count','created_at']
        read_only_fields = ['id','created_at','updated_at']
        

    def get_comment_count(self,obj):
        return obj.comments.count()

    def create(self,validated_data):
        tags_data = validated_data.pop('tags',[])
        validated_data.pop('author',[])
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError('Authentication required to create posts')
        post = Post.objects.create(author=request.user,**validated_data)
        for tag_data in tags_data:
            tag,created = Tag.objects.get_or_create(name=tag_data['name'])
            post.tags.add(tag)
        return post
    def update(self,instance,validated_data):
        tags_data = validated_data.pop('tags',None)
        instance.tittle = validated_data.get('title',instance.title)
        instance.save()

        if tags_data is not None:
            instance.tags.clear()
            for tag_data in tags_data:
                tag,created = Tag.objects.get_or_create(name=tag_data['name'])
                instance.tags.add(tag)
        return instance
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
# USER SERIALIZER
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','email']
#===================================================================
# TASK SERIALIZER
class TaskSerializer(serializers.ModelSerializer):
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
    
#===================================================================
# TASK ATTACHMENT SERIALIZER
class TaskAttachmentSerializer(serializers.ModelSerializer):
    file_size = serializers.SerializerMethodField()
    file_type = serializers.SerializerMethodField()

    class Meta:
        model = TaskAttachment
        fields = ['id','task','file','name','file_size','file_type','uploaded_at']
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
                raise serializers.ValidationError('FIle size cannot exceed 10MB')
            
            allowed_types = ['pdf','doc','docx','jpg','jpeg','png']
            file_ext = value.name.split('.')[-1].lower()
            if file_ext not in allowed_types:
                raise serializers.ValidationError(f"File type not allowed,ALLOWED : {allowed_types}")
            return value
        
