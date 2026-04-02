from rest_framework import serializers
from user.models import *
import logging,re
from PIL import Image

logger = logging.getLogger('user')

class AddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = address
        fields = ['adrname','address','is_default','adrofuser']
        #read_only_fields = ['adrofuser']

class CustomProfileSerializer(serializers.ModelSerializer):
    #test = serializers.SerializerMethodField()
    #all_address = AddressSerializer(many=True,read_only=True)
    #all_address = models.Serialzier
    #first_name = 
    class Meta:
        model = CustomerProfile
        #fields = '__all__'
        fields = ['user','avatar','total_orders','loyalty_points']
        #fields = ['all_address','user','avatar']
        #read_only_fields = ['all_address']
        #depth = 1

    #cadr = AddressSerializer()   
    # def get_test(self,obj):
    #     return f"{obj.saved_addresses}" 
    # def validate_logo(self,value):
    #     if value:
    #         if value.size > 5 * 1024 * 1024:
    #             raise serializers.ValidationError("Logo must be under 5MB")
    #         ext = value.name.split('.')[-1].lower()
    #         if ext not in ['jpg','jpeg','png']:
    #             raise serializers.ValidationError("Only jpg, jpeg, png allowed")
    #         logger.info(f"logo validated: {value.name}")
    #     return value
    
    def validate_avatar(self,value):
        if value:
            if value.size > 5*1024*1024:
                raise serializers.ValidationError("Image size cannot exceed 5mb")
            ext = value.name.split('.')[-1].lower()
            if ext not in ['jpg','jpeg','png']:
                raise serializers.ValidationError("Only jpg, jpeg, png allowed")
        try:
            img = Image.open(value)
            img.verify()
        except Exception:
            raise serializers.ValidationError("Invalid Image format")
        return value
        
    # def create(self,validated_data):



class DriverProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverProfile
        fields = "__all__"