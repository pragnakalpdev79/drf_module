from rest_framework import serializers
from .models import *

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','first_name','last_name']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id','name']

class  CommentSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    post_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = Comment
        fields = ['id','content','post_id','author','created_at']
        read_only_fields = ['id','author','created_at']


class PostSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    tags = TagSerializer(many=True,required=False)
    comments = CommentSerializer(many=True,read_only=True)
    comment_count = serializers.SerializerMethodField()
    class Meta:
        model = Post
        fields = ['id','title','content','author','tags','comments','comment_count','published','created_at','updated_at']
        read_only_fields = ['id','created_at','author','updated_at']

    def get_comment_count(self,obj):
        return obj.comments.count()

    def create(self,validated_data):
        tags_data = validated_data.pop('tags',[])
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
        instance.published = validated_data.get('published',instance.published)
        instance.save()

        if tags_data is not None:
            instance.tags.clear()
            for tag_data in tags_data:
                tag,created = Tag.objects.get_or_create(name=tag_data['name'])
                instance.tags.add(tag)
        return instance
    
class CategorySerializer(serializers.ModelSerializer):
    task_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id','name','color','task_count','created_at']
        read_only_fields = ['id','created_at']

    def get_task_count(self,obj):
        return obj.tasks.count()
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','email']

class TaskSerialzer(serializers.ModelSerializer):
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
    
