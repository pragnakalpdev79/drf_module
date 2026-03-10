from rest_framework import serializers
from .models import *
import os

class CustomUserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    class Meta:
        model = CustomUser
        fields = ['email','password','password_confirm','first_name','last_name']
    
    def validate(self,data):
        print("`````````````````````````````````````````````````p3-entering the serializer `````````````````````````````````````````````````")
        print(data)
        print("`````````````````````````````````````````````````p4-validating within the serializer`````````````````````````````````````````````````")
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords dont match")
        data.pop('password_confirm')
        print(data)
        return data

    def create(self,data):
        print("`````````````````````````````````````````````````p5-removing extra pass and calling create user function of customuser object `````````````````````````````````````````````````")
        #data.pop('password_confirm')
        print(data)
        user = CustomUser.objects.create_user(**data)
        print('-------part 6 over it returned the following------------')
        print(user)
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
