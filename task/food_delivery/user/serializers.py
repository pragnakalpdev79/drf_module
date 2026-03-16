from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import *
import logging,re

logger = logging.getLogger('user')


#===============================================================
# SIGN UP VIEW SERIALIZER
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

#===============================================================
# LOGIN VIEW SERIALIZER
class CustomUserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    class Meta:
        model = CustomUser
        fields = ['email','password']
    def validate(self,data):

        logger.info('p2.0.1  checking if user is registered or not     ')
        user = authenticate(email=data['email'],password=data['password'])
        logger.info(f"p2.0.1  Result of authentication function == {user}")

        if not user:
            # this will check both if user is deleted or user was never registered as queryset only considers the non-deleted users
            # and is_active too.
            logger.info(f'p2.0.1 Requested User does not exist raising Validation Error      ')
            raise serializers.ValidationError("Please enter proper email and password")
        
        logger.info(f"p2.0.1  User object to be returned to the view : - [ {user} ]     ")
        data['user'] = user
        return data



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
