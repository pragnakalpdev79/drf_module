from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db.models.signals import post_save,pre_save
from django.core.mail import send_mail
from django.conf import settings
from django.dispatch import receiver
from .models import *
from .tasks import assign_order_driver
from channels.layers import get_channel_layer
import asyncio
import websockets
import ssl
import json

logger = logging.getLogger(__name__)

def notify_user(message):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "customer",
        {
            "type" : "send_notification",
            "message" : message,
        }
    )

@receiver(post_save,sender=CustomUser)
def post_save_user(sender,instance,created,**kwargs):
    if created:
        if instance.check_if_customer:
            logger.info("A customer registered")
            newprofile = CustomerProfile.objects.create(user=instance)
            logger.info(f"New Customer Profile for {instance.email} Completed!!")
        if instance.check_if_restaurant:
            logger.info("A restaurant owner registered")
        if instance.check_if_driver:
            newprofile = DriverProfile.objects.create(user=instance)
            logger.info(f"New Driver Profile for {instance.email} Completed!!")


def assignorder_driver():
    pending_orders = Order.objects.filter(driver_id=None)
    available_drivers = DriverProfile.filter(is_available=True)
    total_orders = len(pending_orders)
    adrivers = len(available_drivers)
    print("order count",total_orders)
    print("active drivers",adrivers)
    j=0
    for i in available_drivers:
        pending_orders[j].driver = i
        j += 1 
        pending_orders[j].save(update_fields=['driver'])

async def hello():
    async with websockets.connect('ws://127.0.0.1:8000/ws/chatapp/orders/', close_timeout=500) as websocket:
        message = 'weird'
        data = {
                "type": "chat.message",
                "message" : message
            }
        await websocket.send(json.dumps(data))

        print(f"sent data {data}" )

@receiver(pre_save,sender=Order)
def order_status_changed(sender,instance,**kwargs):
    if not instance.pk:
        return
    try:
        old = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return
    if old.status != instance.status:
        logger.info(f"Order {instance.order_number}: {old.status} -> {instance.status}")
        
        #add loyalty points on delivery
        if instance.status == 'dl' and hasattr(instance.customer,'customer_profile'):
            profile = instance.customer.customer_profile
            points = int(instance.total_amount / 10)
            profile.loyalty_points += points
            profile.save(update_fields=['loyalty_points'])
            logger.info(f"Added {points} loyalty points to {instance.customer.email}")

        if instance.status == 'rd':
            print(old)
            logger.info(f"+++++++++++++++++++++++++++++++++++++++++++++")
            logger.info(f"Assign driver request for order -- {old}")
            drivers = DriverProfile.objects.filter(is_available=True)
            logger.info(drivers)
            
            logger.info("function complete")
            #async_task(assignorder_driver)
            #assign_order_driver.delay()
            #logger.info(f"celery result -- {result} ")
            logger.info("celery task called")
            #logger.info(drivers.driver_profile.is_available)



#===========================================================
# TO SEND EMAIL UPON REGISTRATION
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