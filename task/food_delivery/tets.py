from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager
from django.core.validators import RegexValidator,MaxValueValidator,MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models import Avg,Sum,F
from decimal import Decimal
import uuid,logging

logger = logging.getLogger('user')

#================================================================================
# BASE MODEL
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
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        #auto generate username from email if not given
        if not extra_fields.get('username'):
            extra_fields['username'] = email.split('@')[0]
        user = self.model(email=email,**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
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

############################################################################
#  1. MAIN USER MODEL EXTENDED FROM ABSTRACTUSER
class CustomUser(AbstractUser):

    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False) #UUID
    email = models.EmailField(unique=True) #UNIQUE EMAIL
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
        unique=True,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message='Phone number must be entered in the format: "+999999999".Up to 15 digits allowed.' 
        )],
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name','last_name','utype','phone_number']
    objects = MyUserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"
    

    @property
    def is_customer(self):
        return self.utype == 'c'
    @property
    def is_restaurant_owner(self):
        return self.utype == 'r'
    @property
    def is_driver(self):
        return self.utype == 'd'


class Address(TimestampedModel):
    user = models.ForeignKey('CustomUser',on_delete=models.CASCADE,related_name='addresses')
    label = models.CharField(max_length=50,help_text="eg Home, Office")
    address = models.TextField()
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Addresses'
        ordering = ['-is_default','-created_at']

    def __str__(self):
        return f"{self.label}: {self.address[:50]}"
    
    def save(self,*args,**kwargs):
        if self.is_default:
            Address.objects.filter(user=self.user,is_default=True).update(is_default=False)
        super().save(*args,**kwargs)

#================================================================================
# 3. PROFILES

class CustomerProfile(TimestampedModel):
    user = models.OneToOneField('CustomUser',on_delete=models.RESTRICT,related_name='customer_profile',primary_key=True)
    avatar = models.ImageField(upload_to='user_avatars/',blank=True,null=True)
    default_address = models.ForeignKey(Address,on_delete=models.SET_NULL,null=True,blank=True,related_name='+')
    loyalty_points = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    #CALCULATED - not storing as integerfield cause it goes stale
    @property
    def total_orders(self):
        return self.user.customer_orders.count()
    
    @property
    def total_spent(self):
        return self.user.customer_orders.filter(
            status='dl'
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')


class DriverProfile(TimestampedModel):
    user = models.OneToOneField('CustomUser',on_delete=models.RESTRICT,related_name='driver_profile',primary_key=True)
    avatar = models.ImageField(upload_to='user_avatars/',blank=True,null=True)
    VTYPE = (
        ('b','Bike'),
        ('s','Scooter'),
        ('c','Car'),
    )
    vehicle_type = models.CharField(max_length=1,choices=VTYPE,blank=True,default='b',help_text="Delivery partner's Vehicle Type")
    vehicle_number = models.CharField(max_length=10)
    license_number = models.CharField(max_length=20,unique=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"Driver: {self.user.first_name} ({self.get_vehicle_type_display()})"

    @property
    def total_deliveries(self):
        return self.user.driver_orders.filter(status='dl').count()

    @property
    def average_rating(self):
        avg = Review.objects.filter(
            order__driver=self.user
        ).aggregate(avg=Avg('rating'))['avg']
        return round(avg,1) if avg else 0.0

#================================================================================
# 4. RESTRAUNT MODEL
class RestrauntModel(TimestampedModel):
    owner = models.ForeignKey('CustomUser',on_delete=models.CASCADE,related_name='restaurants')
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
    delivery_fee = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('0.00'))
    minimum_order = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('0.00'))

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name}"
    
    #CALCULATED - always fresh from db
    @property
    def average_rating(self):
        avg = self.reviews.aggregate(avg=Avg('rating'))['avg']
        return round(avg,1) if avg else 0.0

    @property
    def total_reviews(self):
        return self.reviews.count()

    @property
    def is_currently_open(self):
        #check manual toggle first
        if not self.is_open:
            return False
        now = timezone.localtime().time()
        #normal hours eg 9am to 10pm
        if self.opening_time <= self.closing_time:
            return self.opening_time <= now <= self.closing_time
        #overnight hours eg 10pm to 2am
        return now >= self.opening_time or now <= self.closing_time

    @property
    def active_menu_count(self):
        return self.menu.filter(is_available=True).count()

#================================================================================
# 5. MENU ITEM
class MenuItem(TimestampedModel):
    restaurant = models.ForeignKey('RestrauntModel',on_delete=models.CASCADE,related_name='menu')
    name = models.CharField(max_length=50)
    description = models.TextField()
    price = models.DecimalField(max_digits=8,decimal_places=2)
    CAC = (
        ('a','Appetizer'),
        ('m','Main Course'),
        ('d','Dessert'),
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
        help_text= 'Dietary information',
        default='no',
    )
    item_image = models.ImageField(upload_to='menu_items/',blank=True,null=True)
    is_available = models.BooleanField(default=True)
    preparation_time = models.PositiveIntegerField(default=15,help_text='in minutes')

    class Meta:
        ordering = ['category','name']

    def __str__(self):
        return f"{self.name} - Rs.{self.price}"

    @property
    def average_rating(self):
        avg = self.reviews.aggregate(avg=Avg('rating'))['avg']
        return round(avg,1) if avg else 0.0

#================================================================================
# 6. ORDER MODEL
class Order(TimestampedModel):
    SC = (
        ('pd','Pending'),
        ('co','Confirmed'),
        ('pr','Preparing'),
        ('rd','Ready'),
        ('pu','Picked Up'),
        ('dl','Delivered'),
        ('cd','Cancelled'),
    )

    #which statuses can go to which - state machine
    VALID_TRANSITIONS = {
        'pd': ['co','cd'],       #pending -> confirmed or cancelled
        'co': ['pr','cd'],       #confirmed -> preparing or cancelled
        'pr': ['rd','cd'],       #preparing -> ready or cancelled
        'rd': ['pu','cd'],       #ready -> picked up or cancelled
        'pu': ['dl'],            #picked up -> delivered only
        'dl': [],                #delivered is final
        'cd': [],                #cancelled is final
    }

    order_number = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    customer = models.ForeignKey('CustomUser',on_delete=models.PROTECT,related_name='customer_orders',db_index=True)
    restaurant = models.ForeignKey('RestrauntModel',on_delete=models.PROTECT,related_name='restaurant_orders',db_index=True)
    driver = models.ForeignKey('CustomUser',on_delete=models.SET_NULL,null=True,blank=True,related_name='driver_orders')
    status = models.CharField(max_length=2,choices=SC,help_text='Order Status',default='pd',db_index=True)

    delivery_address = models.ForeignKey('Address',on_delete=models.PROTECT,related_name='orders')
    special_instructions = models.TextField(null=True,blank=True)


    subtotal = models.DecimalField(max_digits=10,decimal_places=2,default=Decimal('0.00'))
    delivery_fee = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('0.00'))
    tax = models.DecimalField(max_digits=8,decimal_places=2,default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=10,decimal_places=2,default=Decimal('0.00'))

 
    estimated_delivery_time = models.DateTimeField(null=True,blank=True)
    actual_delivery_time = models.DateTimeField(null=True,blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.order_number} - {self.get_status_display()}"

    def calculate_totals(self,tax_rate=Decimal('0.05')):
        #recalculate from order items
        self.subtotal = self.items.aggregate(
            total=Sum(F('unit_price') * F('quantity'))
        )['total'] or Decimal('0.00')

        self.delivery_fee = self.restaurant.delivery_fee
        self.tax = (self.subtotal * tax_rate).quantize(Decimal('0.01'))
        self.total_amount = self.subtotal + self.delivery_fee + self.tax
        self.save(update_fields=['subtotal','delivery_fee','tax','total_amount'])

    def transition_to(self,new_status):
        #enforce valid transitions only
        allowed = self.VALID_TRANSITIONS.get(self.status,[])
        if new_status not in allowed:
            raise ValueError(
                f"Cannot go from '{self.get_status_display()}' to '{new_status}'. "
                f"Allowed: {allowed}"
            )
        self.status = new_status
        #auto set delivery time when delivered
        if new_status == 'dl':
            self.actual_delivery_time = timezone.now()
        self.save(update_fields=['status','actual_delivery_time','updated_at'])
        return True

    def estimate_delivery_time(self):
        #max prep time from all items + 30 min buffer for delivery
        max_prep = self.items.aggregate(
            max_prep=models.Max('menu_item__preparation_time')
        )['max_prep'] or 15
        return self.created_at + timezone.timedelta(minutes=max_prep + 30)

    @property
    def is_cancellable(self):
        return self.status in ['pd','co','pr','rd']

    @property
    def is_completed(self):
        return self.status in ['dl','cd']

#================================================================================
# 7. ORDER ITEM - through model for order -> menu items
class OrderItem(models.Model):
    order = models.ForeignKey('Order',on_delete=models.CASCADE,related_name='items')
    menu_item = models.ForeignKey('MenuItem',on_delete=models.PROTECT,related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=8,decimal_places=2,help_text='price snapshot at order time')
    special_instructions = models.TextField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['order','menu_item'] #no duplicate items just increase qty

    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name}"

    @property
    def line_total(self):
        return self.unit_price * self.quantity

    def save(self,*args,**kwargs):
        #auto snapshot the price from menu if not already set
        if not self.unit_price:
            self.unit_price = self.menu_item.price
        super().save(*args,**kwargs)

#================================================================================
# 8. REVIEW
class Review(TimestampedModel):
    customer = models.ForeignKey('CustomUser',on_delete=models.CASCADE,related_name='reviews')
    restaurant = models.ForeignKey('RestrauntModel',on_delete=models.CASCADE,related_name='reviews',null=True)
    menu_item = models.ForeignKey('MenuItem',on_delete=models.CASCADE,related_name='reviews',null=True)
    order = models.ForeignKey('Order',on_delete=models.CASCADE,related_name='reviews')
    rating = models.IntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)])
    comment = models.TextField(null=True,blank=True)

    class Meta:
        ordering = ['-created_at']
      
        constraints = [
            models.UniqueConstraint(fields=['customer','order'],name='unique_review_per_order')
        ]

    def __str__(self):
        return f"{self.customer.first_name} -> {self.restaurant.name}: {self.rating} stars"

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.order.status != 'dl':
            raise ValidationError('Can only review delivered orders')

        if self.order.customer != self.customer:
            raise ValidationError('Can only review your own orders')

