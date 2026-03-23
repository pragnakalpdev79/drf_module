from celery import shared_task
from celery.utils.log import get_task_logger
from .models import *
import logging


logger = get_task_logger(__name__)

@shared_task(name="driver_assignment",ignore_result=True)
def assign_order_driver():
    
    pending_orders = Order.objects.filter(driver_id=None)
    available_drivers = DriverProfile.filter(is_available=True)
    total_orders = len(pending_orders)
    adrivers = len(available_drivers)
    j=0
    for i in available_drivers:
        pending_orders[j].driver = i
        j += 1 
        pending_orders[j].save(update_fields=['driver'])



