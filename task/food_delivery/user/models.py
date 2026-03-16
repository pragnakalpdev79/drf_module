from decimal import Decimal
from django.db import models
from django.db.models import Avg,Sum,F
from django.utils import timezone
from django.contrib.auth.models import AbstractUser,BaseUserManager
from django.core.validators import RegexValidator,MaxValueValidator,MinValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import uuid,logging


logger = logging.getLogger('user')

class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True,db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True 

############################################################################
#  0. USER MANAGER FOR CUSTOMUSER MODEL
class MyUserManager(BaseUserManager):
    # 0.1 FUNCTION TO HANDLE NEW NORMAL USER CREATION
    def create_user(self,email,password=None,**extra_fields):

        logger.info("p6-create function inside usermanager ")

        if not email:
            raise ValueError(_('The Email field must be set'))
        
        email = self.normalize_email(email)
        logger.info("----p6.1-email checkd -----")

        user = self.model(email=email,**extra_fields)
        logger.info("----p6.2-details stored -----")

        user.set_password(password)
        logger.info("----p6.3-password stored-----")

        user.save(using=self.db)
        logger.info("----p6.4-user saved-----")

        return user
    
    # 0.2 FUNCTION TO HANDLE NEW ADMIN/SUPERUSER CREATION 
    def create_superuser(self,email,password=None,**extra_fields):
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_superuser',True)
        extra_fields.setdefault('is_active',True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_('Superuser must have is_staff=True'))
        
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True'))
        
        return self.create_user(email,password,**extra_fields)
    
    # 0.3 USING ONLY NON-DELETED USERS
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

############################################################################
#  1. MAIN USER MODEL EXTENDED FROM ABSTRACTUSER
class CustomUser(AbstractUser):

    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False) #UUID
    email = models.EmailField(unique=True) #UNIQUE EMAIL
    first_name = models.CharField(max_length=20) # FIRST NAME
    last_name = models.CharField(max_length=20) # LAST NAME

    USER_TYPE = ( 
        ('c','Customer'),
        ('r','Restaurant'),
        ('d','Driver'),
    )
    utype = models.CharField(max_length=1,choices=USER_TYPE,blank=True,default='c',help_text='User Type') #USER TYPE

    created_at = models.DateTimeField(auto_now_add=True) # CREATED AT
    updated_at = models.DateTimeField(auto_now=True) # UPDATED AT

    phone_number = models.CharField(
        max_length=13,
        unique=True,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message='Phone number must be entered in the format: "+999999999".Up to 15 digits allowed.' 
        )],
    )
    
    deleted_at = models.DateTimeField(null=True,blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name','last_name','utype','phone_number']
    objects = MyUserManager()
    # METHODS TO CHECK TYPE OF USER
    @property
    def check_if_customer(self):
        result = (self.utype == 'c')
        return result
    
    @property
    def check_if_restaurant(self):
        result = (self.utype == 'r')
        return result
    
    @property
    def check_if_driver(self):
        result = (self.utype == 'd')
        return result
    #SOFT DELETE AND USER RESTORE
    @property
    def delete(self,using=None,keep_parents=False):
        self.deleted_at = timezone.now()
        logger.info("User deleted")

        self.save() #overrides default delete method
    def restore(self):
        self.deleted_at = None
        
        self.save()

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"
    
    class Meta: 
        permissions = [
            ('IsOwnerOrReadOnly',"owner can edit/delete, others read-only"),
            ('IsRestaurantOwner',"only restaurant owner can edit restaurant and menu items"),
            ('IsCustomer',"only customers can place orders and write reviews"),
            ('IsDriver',"only drivers can update delivery status and location"),
            ('IsOrderCustomer',"only order customer can view order details"),
            ('IsRestaurantOwnerOrDriver',"restaurant owner or assigned driver can update order status"),
        ]
############################################################################
#  2. ADDRESS MODEL TO STORE ALL ADDRESSES
class address(TimestampedModel):
    adrname = models.CharField(max_length=60,unique=True,help_text='Short name to identify the adress')
    address = models.TextField(help_text='Your full address')
    is_default = models.BooleanField()
    adrofuser = models.ForeignKey('CustomUser',on_delete=models.CASCADE,related_name="user_s_adress")

    def save(self,*args,**kwargs):
        if self.is_default:
            usradrs = address.objects.filter(user=self.user)
            usradrs.update(is_default=False)
        super().save(*args,**kwargs)

    def __str__(self):
        return f"User : {self.adrofuser}, Adress saved as : {self.adrname}, Full Address:  {self.address}"

############################################################################
#  3.CUSTOMER PROFILE
class CustomerProfile(TimestampedModel):
    user = models.OneToOneField('CustomUser',on_delete=models.RESTRICT,related_name='customer_profile',primary_key=True)
    avatar = models.ImageField(upload_to='user_avatars/',blank=True,null=True)
    default_address = models.ForeignKey(address,on_delete=models.DO_NOTHING,related_name="saved_adresses_for_user")
    total_orders = models.IntegerField()
    loyalty_points = models.IntegerField(default=0)

    @property
    def total_orders(self):
        return self.user.order_for.count()
    
    @property
    def total_spend(self):
        spend = self.user.order_for.filter(status='dl')
        spend = spend.aggregate(total=Sum('total_amount'))
        if spend['total']:
            return spend['total']
        return Decimal('0.00')
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"





class DriverProfile(TimestampedModel):
    user = models.ForeignKey('CustomUser',on_delete=models.RESTRICT,related_name='driver_profile')
    avatar = models.ImageField(upload_to='user_avatars/',blank=True,null=True)
    VTYPE = (
        ('b','Bike'),
        ('s','Scooter'),
        ('c','Car'),
    )
    vehicle_type = models.CharField(max_length=1,choices=VTYPE,blank=True,default='b',help_text="Delivery partner's Vehicle Type")
    vehicle_number = models.CharField(max_length=10)
    license_number = models.CharField(max_length=10)
    is_available = models.BooleanField(default=False)
    total_deliveries = models.IntegerField()
    average_rating = models.DecimalField(max_digits=2,decimal_places=1,default=0)

class RestrauntModel(TimestampedModel):
    owner = models.ForeignKey('CustomUser',on_delete=models.RESTRICT,related_name='restraunt_owner')
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
    address = models.TextField()
    phone_number = models.CharField(
        max_length=13,
        validators=[
            RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message='Phone number must be entered in the format: "+999999999".Up to 15 digits allowed.' ,
        )],)
    email = models.EmailField(unique=True) 
    logo = models.ImageField(upload_to='logos/',blank=True,null=True)
    banner = models.ImageField(upload_to='banners/',blank=True,null=True)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    is_open = models.BooleanField(default=False)
    delivery_fee = models.DecimalField(max_digits=2,decimal_places=2)
    minimum_order = models.DecimalField(default=0,decimal_places=0,max_digits=3)
    average_rating = models.DecimalField(max_digits=1,default=0,decimal_places=1)
    total_reviews = models.IntegerField()

    def __str__(self):
        return f"{self.name}"

class MenuItem(TimestampedModel):
    restaurant = models.ForeignKey('RestrauntModel',on_delete=models.CASCADE,related_name='menu')
    name = models.CharField(max_length=50)
    description = models.TextField()
    price = models.DecimalField(max_digits=5,decimal_places=2)
    CAC = (
        ('a','Appteizer'),
        ('m','Main Course'),
        ('d','Desert'),
        ('b','Beverage'),
        ('s','Side Dish'),
    )
    category = models.CharField(
        max_length = 1,
        choices = CAC,
        help_text = 'Available Catagories',
    )
    DIC = (
        ('v1','Vegetarian'),
        ('v2','Vegan'),
        ('gf','Gluten-Free'),
        ('df','Dairy-Free'),
        ('no','None'),
    )
    dietary_info = models.CharField(
        max_length=2,
        choices = DIC,
        help_text= 'Diteray information',
    )
    def file_path(self):
        return f"{self.name}/menu_items"
    item_image = models.ImageField(upload_to=file_path,blank=True,null=True)
    is_available = models.BooleanField(default=True)
    preparation_time = models.PositiveIntegerField(default=3)

    def __str__(self):
        return f"{self.name}"

class Order(TimestampedModel):
    customer = models.ForeignKey('CustomUser',on_delete=models.DO_NOTHING,related_name='order_for',db_index=True)
    restaurant = models.ForeignKey('RestrauntModel',on_delete=models.DO_NOTHING,related_name='order_by',db_index=True)
    driver = models.ForeignKey('CustomUser',on_delete=models.DO_NOTHING,related_name='deliver_by',null=True)
    order_number = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    SC = (
        ('pd','Pending'),
        ('co','Confiremd'),
        ('pr','Preparing'),
        ('rd','Ready'),
        ('pu','Picked Up'),
        ('dl','Delivered'),
        ('cd','Cancelled'),
    )
    status = models.CharField(
        max_length=2,
        choices= SC,
        help_text = 'Order Status',
        db_index=True,
    )
    delivery_address = models.ForeignKey('address',on_delete=models.DO_NOTHING,related_name='delivery_adress')
    #subtotal =
    tax = models.DecimalField(max_digits=4,decimal_places=2,default=30)
    #total_amount
    special_instructions = models.TextField(null=True,blank=True)
    #estimated delivery time
    #actual delivery time
    def calculate_total(self):
        total = None



class OrderItem(models.Model):
    order = models.ForeignKey('CustomUser',on_delete=models.DO_NOTHING,related_name='item_for')
    menu_item = models.ForeignKey('MenuItem',on_delete=models.DO_NOTHING,related_name='item_from')
    quantity = models.PositiveIntegerField(blank=False,null=False)
    uprice = models.DecimalField(max_digits=5,decimal_places=2,help_text='snapshot of item price at order time')
    special_instructions = models.TextField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f" Order Item details : {self.menu_item} | Quantity : {self.quantity} | Special Instructions provided : {self.special_instructions}" 


class Review(TimestampedModel):
    customer = models.ForeignKey('CustomUser',on_delete=models.CASCADE,related_name='review_by')
    restaurant = models.ForeignKey('RestrauntModel',on_delete=models.CASCADE,related_name='review_for',null=True)
    menu_item = models.ForeignKey('MenuItem',on_delete=models.CASCADE,related_name='review_of',null=True)
    order = models.ForeignKey('Order',on_delete=models.CASCADE,related_name='order')
    rating = models.IntegerField(validators=[MinValueValidator(0),MaxValueValidator(5)])
    comment = models.TextField(null=True)

    def clean(self):
        if self.order.customer != self.customer:
            raise ValidationError("you can only review your own orders")
        if self.order.status != 'dl':
            raise ValidationError("can not review the orders which are not delivered")
        


    def __str__(self):
        return f"Review by {self.customer.email} for menu-item {self.menu_item} is {self.rating},which was order the {self.restaurant} "