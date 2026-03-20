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
    all_objects = models.Manager()
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
    #SOFT DELETE AND USER RESTORE FROM LEVEL 3B SOFT DELETE CODE
    @property
    def delete(self,using=None,keep_parents=False):
        self.deleted_at = timezone.now()
        logger.info("User deleted")

        self.save() #overrides default delete method
    @property
    def restore(self):
        self.deleted_at = None
        
        self.save()

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"
    
    class Meta: 
        permissions = [
            ('IsOwnerOrReadOnly',"AA owner can edit/delete, others read-only"),
            ('IsRestaurantOwner',"AA only restaurant owner can edit restaurant and menu items"),
            ('IsCustomer',"AA only customers can place orders and write reviews"),
            ('IsDriver',"AA only drivers can update delivery status and location"),
            ('IsOrderCustomer',"AA only order customer can view order details"),
            ('IsRestaurantOwnerOrDriver',"AA restaurant owner or assigned driver can update order status"),
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
            usradrs = address.objects.filter(adrofuser=self.adrofuser)
            usradrs.update(is_default=False)
        super().save(*args,**kwargs)

    def __str__(self):
        return f"User : {self.adrofuser}, Adress saved as : {self.adrname}, Full Address:  {self.address}"

############################################################################
#  3.CUSTOMER PROFILE
class CustomerProfile(TimestampedModel):
    user = models.OneToOneField('CustomUser',on_delete=models.RESTRICT,related_name='customer_profile',primary_key=True)
    avatar = models.ImageField(upload_to='user_avatars/',blank=True,null=True)
    #default_address = models.TextField(null=True,blank=True)
    #saved_addresses = models.ForeignKey(address,on_delete=models.DO_NOTHING,related_name="saved_adresses_for_user",null=True,blank=True)
    #default_address = models.ForeignKey(address,on_delete=models.DO_NOTHING,related_name="saved_adresses_for_user",null=True,blank=True)
    #total_orders = models.IntegerField()
    loyalty_points = models.IntegerField(default=0)

    @property
    def default_adress(self):
        defadr = address.objects.get(adrofuser=self.user,is_default=True)
        return defadr

    @property
    def saved_addresses(self):
        alladrs = address.objects.filter(adrofuser=self.user)
        return alladrs

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

############################################################################
#  4.DRIVER PROFILE
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
    total_deliveries = models.IntegerField(blank=True,null=True)
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
    delivery_fee = models.DecimalField(max_digits=4,decimal_places=2)
    minimum_order = models.DecimalField(default=0,decimal_places=0,max_digits=3)
    average_rating = models.DecimalField(max_digits=2,default=0,decimal_places=1)
    total_reviews = models.IntegerField(null=True,blank=True)

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
    STATE_PD = 'pd'
    STATE_CO = 'co'
    STATE_PR = 'pr'
    STATE_RD = 'rd'
    STATE_PU = 'pu'
    STATE_DL = 'dl'
    STATE_CD = 'cd'

    __current_status = None

    SC = (
        (STATE_PD,'Pending'),
        (STATE_CO,'Confiremd'),
        (STATE_PR,'Preparing'),
        (STATE_RD,'Ready'),
        (STATE_PU,'Picked Up'),
        (STATE_DL,'Delivered'),
        (STATE_CD,'Cancelled'),
    )
    TRANSITIONS = {
        STATE_PD: STATE_CO,
        STATE_PD: STATE_CD,
        STATE_CO: STATE_PR,
        STATE_PR: STATE_RD,
        STATE_RD: STATE_PU,
        STATE_PU: STATE_DL,
        STATE_DL: STATE_CD,
    }

    status = models.CharField(
        max_length=2,
        choices= SC,
        help_text = 'Order Status',
        db_index=True,
        default=STATE_PD,
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

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.__current_status = self.status #INTIATED WITH PENDING ORDER STATUS
    
    #save called,
    def save(self, 
             force_insert=False, #Forces an SQL INSERT if true
             force_update=False, # Forces an SQL UPDATE
             using=None,#Specifies which database to use
             update_fields=None): #Specifies which fields to update
        #next allowed is -> confirmed or cancelled

        allowed_next = self.TRANSITIONS[self.__current_status] 
        

        # CHECKS IF THE MODEL IS BEING CREATED OR UPDATED
        #IF THE STATE IS CHANGED ITS UPDATED HENCE SKIP VALIDATION
        # self.status(pending) != self.__current_status(pending) which means it is not updated yet hence False(Not Updated)
        updated = self.status != self.__current_status


        if self.pk and updated and allowed_next != self.status:
            raise Exception("Invalid Transition.",self.status,allowed_next)
        
        if self.pk and updated:
            self.__current_status = allowed_next

        return super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )
    
    def _transition(self):
        next_status = self.TRANSITIONS[self.status]
        self.status = next_status
        self.save()

    def raccept(self,driver):
        self._transition(self.STATE_CO)
    
    def rreject(self):
        self._transition(self.STATE_CD)

    def confiremd(self):
        self._transition(self.STATE_PR)
    
    def readytop(self):
        self._transition(self.STATE_RD)


class CartItem(models.Model):
    user = models.ForeignKey('CustomUser',on_delete=models.CASCADE,related_name='user_cart')
    menu_item = models.ForeignKey('MenuItem',on_delete=models.DO_NOTHING,related_name='added_item')
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"This is {self.user}'s cart for - {self.menu_item} with quantity {self.quantity}"



class OrderItem(models.Model):
    order = models.ForeignKey('Order',on_delete=models.DO_NOTHING,related_name='item_for')
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