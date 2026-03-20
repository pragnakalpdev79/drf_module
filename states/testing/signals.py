from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver
from .models import *
import logging

logger = logging.getLogger('user')

@receiver(post_save,sender=PickUp)
def post_save_pickup(sender,instance,created,**kwargs):
    logger.info("testing! 2")
    if created:
        logger.info("boom!! a new customer to pick up!!")

@receiver(pre_save,sender=PickUp)
def pre_save_pickup(sender,instance,**kwargs):
    logger.info("testing! 1 ")


