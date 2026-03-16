from rest_framework import serializers 
from .models import Post,Comment,Tag
from django.contrib.auth.models import User

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','email','first_name','last_name']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id','name']
    
class CommentSerializer(serializers.ModelSerializer):
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
        fields = ['id','title','content','author','tags','comments','comment_count','created_at','updated_at']
        read_only_fields = ['id','created_at']
    
    def get_comment_count(self,obj):
        return obj.comments.count()
    

    def create(self,validated_data):
        tags_data = validated_data.pop('tags',[])
        request = self.context.get('request')
        # if not request or not request.user.is_authenticated:
        #     raise serializers.ValidationError("Authentication required to create posts")
        post = Post.objects.create(author=request.user,**validated_data)
        for tag_data in tags_data:
            tag, created = Tag.objects.get_or_create(name=tag_data['name'])
            post.tags.add(tag)

        return post
    
    def update(self,instance,validated_data):
        tags_data = validated_data.pop('tags',None)
        instance.title = validated_data.get('title',instance.title)
        instance.content = validated_data.get('content',instance.content)
        #
        #instance.published = validated_data.get('published',instance.published)
        instance.save()

        if tags_data is not None:
            instance.tags.clear()
            for tag_data in tags_data:
                tag,created = Tag.objects.get_or_create(name=tag_data['name'])
                instance.tags.add(tag)
        return instance