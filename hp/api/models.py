from django.db import models 
from django.contrib.auth.models import User
from django.utils import timezone

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
# TASK API MODELS
class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

class Category(models.Model):
    name = models.CharField(max_length=50,unique=True)
    color = models.CharField(max_length=7,default='#000000')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Task(TimestampedModel):
    title = models.CharField(max_length=100)
    desc = models.TextField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    PRIORITY_CHOICE = (
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
    category = models.ForeignKey(Category,on_delete=models.SET_NULL,null=True,blank=True,related_name='tasks')
    assigned_to = models.ForeignKey(User,related_name='assigned_tasks',blank=True,on_delete=models.CASCADE,null=True)
    deleted_at = models.DateTimeField(null=True,blank=True)

    image = models.ImageField(upload_to='task_images/',blank=True,null=True)
    



    objects = SoftDeleteManager()
    all_objects = models.Manager()

    def delete(self,using=None,keep_parents=False):
        self.deleted_at = timezone.now()
        self.save()
    
    def restore(self):
        self.deleted_at = None
        self.save()

    def __str__(self):
        return self.title
    class Meta:
        ordering = ['-created_at']

#------------------------------
# File Uploads
class TaskAttachment(models.Model):
    task = models.ForeignKey(Task,on_delete=models.CASCADE,related_name='attachments')
    file = models.FileField(upload_to='attachments/')
    name = models.CharField(max_length=200)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
