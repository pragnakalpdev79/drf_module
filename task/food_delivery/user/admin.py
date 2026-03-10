from django.contrib import admin
from .models import *

admin.site.register(CustomUser)
admin.site.register(CustomerProfile)
admin.site.register(address)
admin.site.register(DriverProfile)
admin.site.register(RestrauntModel)
admin.site.register(MenuItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Review)