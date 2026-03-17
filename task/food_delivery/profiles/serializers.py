from rest_framework import serializers
from user.models import *
import logging,re

logger = logging.getLogger('user')

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = address
        fields = ['adrname','address','is_default','adrofuser']
        read_only_fields = ['adrofuser']

class CustomProfileSerializer(serializers.ModelSerializer):
    adr = AddressSerializer(read_only=True)
    class Meta:
        model = CustomerProfile
        fields = ['user','avatar','adr']
        
    def validate_image(self,value):
        if value:
            if value.size > 5*1024*1024:
                raise serializers.ValidationError("Image size cannot exceed 5mb")
        from PIL import Image
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