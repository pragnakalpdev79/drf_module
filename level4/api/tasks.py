from celery import shared_task
from django.core.mail import send_mail
from .models import Post

@shared_task
def send_post_notification(post_id):
    print("sending the mail")
    post = Post.objects.get(id=post_id)
    print(f" post intiated {post} ")
    send_mail(
        subject=f'New Post: {post.title}',
        message=post.content,
        from_email='noreply@mymail.com',
        recipient_list=['pragnakalp.dev79@gmail.com'],
    )
    print("mail sent")
