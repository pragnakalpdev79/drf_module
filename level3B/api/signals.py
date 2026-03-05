from django.db.models.signals import pre_save,post_save,pre_delete,post_delete
from django.dispatch import receiver
from django.utils.text import slugify
from .models import Post

@receiver(pre_save,sender=Post)
def pre_save_post(sender,instance,**kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.title)

@receiver(post_save,sender=Post)
def post_save_post(sender,instance,created,**kwargs):
    if created:
        print(f"New Post Created: {instance.title}")

@receiver(pre_delete,sender=Post)
def pre_delete_post(sender,instance,**kwargs):
    print(f"Post being delted: {instance.title}")

    