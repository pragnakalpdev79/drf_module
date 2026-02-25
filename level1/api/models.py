from django.db import models 


# EXERCISE 1 - BOOK - API MODEL
class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    published_date = models.DateField()
    isbn = models.CharField(max_length=13, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']


class Task(models.Model):
    title = models.CharField(max_length=100)
    desc = models.TextField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
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
    def __str__(self):
        return self.title
    class Meta:
        ordering = ['-created_at']

# EXERCISE 3 - AUTHOR - API MODEL
class Author(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=200)
    bio = models.TextField(null=True,blank=True)

# EXERCISE 5 - PRODUCT API - MODEL
class Product(models.Model):
    name = models.CharField(max_length=200)
    desc = models.TextField(null=True,blank=True)
    price = models.DecimalField(max_digits=10,decimal_places=2)
    stock = models.IntegerField(default=0)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)   