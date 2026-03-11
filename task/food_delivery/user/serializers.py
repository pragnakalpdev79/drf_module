from rest_framework import serializers
from .models import *
import logging,re

logger = logging.getLogger('user')

class CustomUserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8,)
    password_confirm = serializers.CharField(write_only=True)
    class Meta:
        model = CustomUser
        fields = ['username','email','phone_number','password','password_confirm','first_name','last_name','utype']
    
    def validate_phone_number(self,value):
        regexf = r'^\+?1?\d{9,15}$'
        if not re.match(regexf,value):
            raise serializers.ValidationError("Please enter the phone number in proper format")
        logger.info("regx matched succesful")
        return value

    def validate(self,data): #for validating multiple fields
        logger.info("````p3-entering the serializer ````")
        logger.info("````p4-validating within the serializer``")
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords dont match")
        data.pop('password_confirm')
        return data

    def create(self,data):
        logger.info("p``p5-removing extra pass and calling create user function of customuser object `")
        #data.pop('password_confirm')
        user = CustomUser.objects.create_user(**data)
        logger.info("-part 6 over it returned the following")
        return user


class CustomProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = "__all__"
        
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
        
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = address
        fields = "__all__"

class DriverProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverProfile
        fields = "__all__"

class RestrauntSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestrauntModel
        fields = "__all__"

class MenuItemSerilizer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = "__all__"

class OrderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
