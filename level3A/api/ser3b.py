from rest_framework import serializers
from .models import Post,User,Tag

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','enail','first_name','last_name']

class PostSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    author_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = Post
        fields = ['id','title','content','author','author_id','created_at']
        read_only_fields = ['id','created_at']
    def create(self,validated_data):
        author_id = validated_data.pop('author_id',None)
        if author_id:
            validated_data['author_id'] = author_id
        return Post.objects.create(**validated_data)