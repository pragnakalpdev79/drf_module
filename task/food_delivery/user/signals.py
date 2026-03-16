from django.db.models.signals import pre_save,post_save,pre_delete,post_delete
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
            logger.info(f"New Customer Profile for {instance.email} Completed!!")
        if instance.check_if_restaurant:
            logger.info("A restaurant owner registered")
        if instance.check_if_driver:
            newprofile = DriverProfile.objects.create(user=instance)
            #print(newprofile)
            logger.info(f"New Driver Profile for {instance.email} Completed!!")
