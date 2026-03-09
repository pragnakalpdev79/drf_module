from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager
from django.core.validators import RegexValidator
import uuid

# username (unique)
# email (unique)
# phone_number (unique)
# first_name
# last_name
# user_type (choices: Customer, Restaurant Owner, Delivery Driver)
# is_active (boolean)
# created_at
# updated_at

class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True 

class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    email = models.EmailField(unique=True) #UNIQUE EMAIL
    #
    first_name = models.CharField(max_length=20) # FIRST NAME
    last_name = models.CharField(max_length=20) # LAST NAME
    USER_TYPE = (
        ('c','Customer'),
        ('r','Restraunt'),
        ('d','Driver'),
    )
    utype = models.CharField(max_length=1,choices=USER_TYPE,blank=True,default='c',help_text='User Type') #USER TYPE
    created_at = models.DateTimeField(auto_now_add=True) # CREATED AT
    updated_at = models.DateTimeField(auto_now=True) # UPDATED AT
    phone_number = models.CharField(
        max_length=13,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message='Phone number must be entered in the format: "+999999999".Up to 15 digits allowed.' 
        )]
    )


class CustomerProfile(TimestampedModel):
    user = models.ForeignKey('CustomUser',on_delete=models.RESTRICT,null=True)
    avatar = models.ImageField(upload_to='user_avatars/',blank=True,null=True)
    default_address = models.TextField()
    #
    total_orders = models.IntegerField()
    loyalty_points = models.IntegerField()

class DriverProfile(TimestampedModel):
    # user (ForeignKey to User)
    # avatar (image upload, max 5MB)
    # vehicle_type (choices: Bike, Scooter, Car)
    # vehicle_number
    # license_number
    # is_available (boolean, default True)
    # total_deliveries
    # average_rating (decimal, default 0)
    # created_at
    # updated_at
    user = models.ForeignKey('CustomUser',on_delete=models.RESTRICT)
    avatar = models.ImageField(upload_to='user_avatars/',blank=True,null=True)
    VTYPE = (
        ('b','Bike'),
        ('s','Scooter'),
        ('c','Car'),
    )
    vehicle_type = models.CharField(max_length=1,choices=VTYPE,blank=True,default='b',help_text="Delivery partner's Vehicle Type")
    vehicle_number = models.CharField(max_length=10)
    license_number = models.DecimalField(max_digits=10)
    is_available = models.BooleanField(default=False)
    total_deliveries = models.IntegerField()
    average_rating = models.DecimalField(max_digits=1,decimal_places=1,default=0)

class RestrauntModel(TimestampedModel):
    # owner (ForeignKey to User)
    # name
    # description
    # cuisine_type (choices: Italian, Chinese, Indian, Mexican, American, Japanese, Thai, Mediterranean)
    # address
    # phone_number
    # email
    # logo (image upload, max 5MB)
    # banner (image upload, max 10MB)
    # opening_time
    # closing_time
    # is_open (boolean)
    # delivery_fee (decimal)
    # minimum_order (decimal, default 0)
    # average_rating (decimal, default 0)
    # total_reviews
    # created_at
    # updated_at
    owner = models.ForeignKey('CustomUser',on_delete=models.RESTRICT)
    name = models.CharField(max_length=50)
    description = models.TextField()
    CC = (
        ('it','Italian'),
        ('ch','Chinese'),
        ('in','Indian'),
        ('me','Mexican'),
        ('am','American'),
        ('ja','Japanese'),
        ('th','Thai'),
        ('md','Mediterranean'),
    )
    cuisine_type = models.CharField(max_length=2,choices=CC,help_text='Available Cuisine')
    