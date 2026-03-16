from django.db.models.signals import pre_save,post_save,pre_delete,post_delete
from django.dispatch import receiver
from django.utils.text import slugify
from .models import CustomUser

@receiver(post_save,sender=CustomUser)
def post_save_user(sender,instance,created,**kwargs):
    if created:
        print(sender,instance)
        print("boom!!")
