from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)

class Book(models.Model):
    cat = models.ForeignKey(Category,on_delete=models.CASCADE)
    book_tittle = models.CharField(max_length=100)
