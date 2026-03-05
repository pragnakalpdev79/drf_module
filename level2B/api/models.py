from django.db import models 
from django.contrib.auth.models import User

class TimestampedModel(models.Model):
    '''
    Base model with timetamp fields
    '''
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True # this prevents db table creation from this model

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

class UserProfile(TimestampedModel):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='profile')
    bio = models.TextField(blank=True)
    phone_number = models.CharField(max_length=15,blank=True)
    avatar = models.ImageField(upload_to='avatars/',blank=True,null=True)
    website = models.URLField(blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"