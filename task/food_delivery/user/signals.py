from django.db.models.signals import pre_save,post_save,pre_delete,post_delete
from django.core.mail import send_mail
from django.conf import settings
from django.dispatch import receiver
from django.utils.text import slugify
from .models import *

logger = logging.getLogger(__name__)

@receiver(post_save,sender=CustomUser)
def post_save_user(sender,instance,created,**kwargs):
    if created:
        if instance.check_if_customer:
            logger.info("A customer registered")
            logger.info(type(instance))
            newprofile = CustomerProfile.objects.create(user=instance)
            #print(newprofile)
            # logger.info(f"New Customer Profile for {instance.email} Completed!!")
            # try:
            #     send_mail(
            #         subject="Registration Confirmation Food Delivery Sys",
            #         message=f"Your customer acount has been registered with us,with username : {instance.username} with email : {instance.email}  Upload your profile picture and update adress by using your profile ",
            #         from_email=settings.DEFAULT_FROM_EMAIL,
            #         recipient_list=[instance.email]
            #         fail_silently=True
            #              )
            #     logger.info(f"email sent to {instance.email}")
            # except Exception as e :
            #      logger.error(f"mail not sent error: -  {e}")
        if instance.check_if_restaurant:
            logger.info("A restaurant owner registered")
        if instance.check_if_driver:
            newprofile = DriverProfile.objects.create(user=instance)
            #print(newprofile)
            logger.info(f"New Driver Profile for {instance.email} Completed!!")
            # logger.info(f"New Driver Profile for {instance.email} Completed!!")
            # try:
            #     send_mail(
            #         subject="Registration Confirmation Food Delivery Sys",
            #         message=f"Your customer acount has been registered with us,with username : {instance.username} with email : {instance.email}  Upload your profile picture and complete your driver profile by using your profile ",
            #         from_email=settings.DEFAULT_FROM_EMAIL,
            #         recipient_list=[instance.email]
            #         fail_silently=True
            #              )
            #     logger.info(f"email sent to {instance.email}")
            # except Exception as e :
            #      logger.error(f"mail not sent error: -  {e}")
