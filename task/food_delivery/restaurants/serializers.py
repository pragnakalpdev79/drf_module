from rest_framework import serializers
from user.models import *
#from django.utils.timezone import datetime
import datetime
import logging,re
#from .pagination import RestoPagination

logger = logging.getLogger('user')

class RestoListSerializer(serializers.ModelSerializer):
    logger.info("in serializer")
    is_open_now = serializers.SerializerMethodField()
    #pagination_class = RestoPagination
    class Meta:
        model = RestrauntModel
        fields = ['id','name','description','cuisine_type','address',
                  'phone_number','email','logo','banner','delivery_fee',
                  'minimum_order','is_open_now','minimum_order',
                  'average_rating','total_reviews']
    
    def get_is_open_now(self,obj): #TO CHECK IF THE RESTO IS OPEN OR NOT AT GIVEN TIME
        logger.info(f"======================{datetime.datetime.now().time()}=================")
        if obj.opening_time <= datetime.datetime.now().time() <= obj.closing_time:
            logger.info('Restro is Open')
            return True
        logger.info('Restro is Closed')
        return False

    
class RestoCreateSerializer(serializers.ModelSerializer):
    # logger.info('Starting restro Create serializer')
    
    is_open = serializers.SerializerMethodField()

    def get_is_open(self,obj):
        logger.info(f"Current Time : ---- {datetime.datetime.now().time()}")
        print('Starting restro Create serializer')
        print(type(obj.opening_time))
        if obj.opening_time <= datetime.datetime.now().time() <= obj.closing_time:
            logger.info('Restro is Open')
            return True
        logger.info('Restro is Closed while being registered')
        return False 
    
    class Meta:

        fields = ['owner','name','description','cuisine_type','address','phone_number','email','logo','banner',
                  'opening_time','closing_time','delivery_fee','minimum_order','is_open']
        read_only_fields = ['owner']
        model = RestrauntModel
    
    def validate_phone_number(self,value):
        regexf = r'^\+?1?\d{9,15}$'
        if not re.match(regexf,value):
            raise serializers.ValidationError("Please enter the phone number in proper format")
        logger.info("regx matched succesful")
        return value
    
        
class MenuItemSerializer(serializers.ModelSerializer):
    #restaurant = RestoSerializer()
    class Meta:
        fields = ['id','name','description','price','category','dietary_info','is_available','preparation_time']
        model = MenuItem
        #depth = 0

class RestoSerializer(serializers.ModelSerializer):
    menu = MenuItemSerializer(many=True)
    class Meta:
        fields = ['name','description','cuisine_type','is_open','opening_time','closing_time','menu','review_for']
        model = RestrauntModel

class MenuSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ["name",'description','price','category','dietary_info','is_available','preparation_time']
        model = MenuItem