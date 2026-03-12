from django.db import models 
from django.contrib.auth.models import User

#================================================================================
# Base Model for created-at and updated-at DRY
class TimestampedModel(models.Model):
    '''
    Base model with timetamp fields
    '''
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True # this prevents db table creation from this model
#================================================================================
# USER-PROFILE
class UserProfile(TimestampedModel):
    #ONE-TO-ONE 
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='profile')
    bio = models.TextField(blank=True)
    phone_number = models.CharField(max_length=15,blank=True)
    avatar = models.ImageField(upload_to='avatars/',blank=True,null=True)
    website = models.URLField(blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"
#================================================================================
# TASK API MODELS
class Task(TimestampedModel):
    title = models.CharField(max_length=100)
    desc = models.TextField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    PRIORITY_CHOICE = ( #EXCERCISE 2 ENHACING TASK API -ADDED priority field and due dat field
        ('l','Low'),
        ('m','Medium'),
        ('h','High')
    )
    priority = models.CharField(max_length=1,
                                choices=PRIORITY_CHOICE,
                                blank=True,
                                default='m',
                                help_text='Task Priority,')
    due_date = models.DateField(null=True,blank=True,help_text='Task Deadline')
    owner = models.ForeignKey(User,on_delete=models.CASCADE,related_name='tasks')
    def __str__(self):
        return self.title
    class Meta:
        ordering = ['-created_at']
#================================================================================
# BOOK API MODELS
class Book(TimestampedModel):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    published_date = models.DateField()
    isbn = models.CharField(max_length=13, unique=True)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User,on_delete=models.CASCADE,related_name='books')
    def __str__(self):
        return self.title
    class Meta:
        ordering = ['-created_at']
    
#================================================================================
# BLOG API MODELS
# 1. Tag
class Tag(models.Model):
    name = models.CharField(max_length=50,unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name
# 3. Comment
class Comment(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    # MANY TO ONE RELATION FROM comments to user
    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name='commments')
    #post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name='post_comments')
# 2. Post
class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    #MANY-TO-ONE - fk
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    #MANY-TO-MANY
    tags = models.ManyToManyField(Tag,related_name='posts',blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    comments = models.ForeignKey(Comment,related_name='comments',blank=True)

    def __str__(self):
        return self.title



