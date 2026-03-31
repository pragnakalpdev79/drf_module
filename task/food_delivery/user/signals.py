from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db.models.signals import post_save,pre_save
from django.core.mail import send_mail
from django.conf import settings
from django.dispatch import receiver
from .models import *
from .tasks import assign_order_driver
from channels.layers import get_channel_layer
import logging

logger = logging.getLogger(__name__)


# @receiver(pre_save,sender=CustomUser)
# def pre_save_post(sender,instance,**kwargs)



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


def send_noti_user(message,orderid,room):
    logger.info("here")
    if room == 'customer':
        gc = f"customer_{orderid}"
    #gc = 'order'
    if room == 'restaurant':
        gc = f'restaurant_{orderid}'
    if room == 'driver':
        gc = "drivers"
    channel_layer = get_channel_layer()
    print("--------------------Sending notification!!----------------------")
    print(f"-------------------- to : - {gc} ")
    async_to_sync(channel_layer.group_send)(
        gc,{
            "type"  : "chat.message",
            "message": message,
        }
    )

@receiver(pre_save,sender=Order)
def new_order(sender,instance,**kwargs):
    if instance.status == 'pd':
        # 1. Resto
        message = f"New Order for {instance.total_amount}"
        room = 'restaurant'
        restoid = instance.restaurant.owner_id
        #=====================================
        # SENDING NOTI TO RESTO
        #=====================================
        send_noti_user(message,restoid,room)
        #2. Customer
        message = "Your Order has been placed"
        room = 'customer'
        custid = instance.customer.pk
        #=====================================
        # SENDING NOTI TO CUSTOMER
        #=====================================
        send_noti_user(message,custid,room)    

@receiver(pre_save,sender=Order)
def order_status_changed(sender,instance,**kwargs):
    if not instance.pk:
        return
    try:
        old = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return
    if old.status != instance.status:
        print("1.order status changed!!----------------------")
        logger.info(f"Order {instance.order_number}: {old.status} -> {instance.status}")
        message = f"status updated {instance.order_number}: {old.status} -> {instance.status} "
        orderid = instance.customer.pk
        room = 'customer'
        #=====================================
        # SENDING NOTI TO CUSTOMER
        #=====================================
        send_noti_user(message,orderid,room)

        if instance.status == 'pd':
            # 1. Resto
            message = f"New Order for {instance.total_amount}"
            room = 'restaurant'
            restoid = instance.resaturant
        #=====================================
        # SENDING NOTI TO RESTO
        #=====================================
            send_noti_user(message,restoid,room)
            #2. Customer
            message = "Your Order has been placed"
            room = 'customer'
            custid = instance.customer.pk
        #=====================================
        # SENDING NOTI TO CUSTOMER
        #=====================================
            send_noti_user(message,custid,room)
        
        if instance.status == 'co':
            #1. Customer
            message = "Your Order has been accepted by restaurant"
            room = 'customer'
            custid = instance.customer.pk
        #=====================================
        # SENDING NOTI TO CUSTOMER
        #=====================================
            send_noti_user(message,custid,room)
            #2. Driver
            message = f"New Delivery {instance.pk} for amount {instance.total_amount}"
            room = 'driver'
            ordid = instance.customer.pk
        #=====================================
        # SENDING NOTI TO DRIVER
        #=====================================
            send_noti_user(message,ordid,room)


        
        #add loyalty points on delivery
        if instance.status == 'dl' and hasattr(instance.customer,'customer_profile'):
            profile = instance.customer.customer_profile
            points = int(instance.total_amount / 10)
            profile.loyalty_points += points
            profile.save(update_fields=['loyalty_points'])
            logger.info(f"Added {points} loyalty points to {instance.customer.email}")

# def assignorder_driver():
#     pending_orders = Order.objects.filter(driver_id=None)
#     available_drivers = DriverProfile.filter(is_available=True)
#     total_orders = len(pending_orders)
#     adrivers = len(available_drivers)
#     print("order count",total_orders)
#     print("active drivers",adrivers)
#     j=0
#     for i in available_drivers:
#         pending_orders[j].driver = i
#         j += 1 
#         pending_orders[j].save(update_fields=['driver']