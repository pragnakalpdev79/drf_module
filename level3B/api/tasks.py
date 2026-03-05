from celery import shared_task
from django.core.mail import send_mail
from .models import Post

@shared_task
def send_post_notification(post_id):
    post = Post.objects.get(id=post_id)
    send_mail(
        subject=f'New Post: {post.title}',
        message=post.content,
        from_email='noreply@mymail.com',
        recipient_list=['user@yourmail.com'],
    )