from rest_framework import serializers
from user.models import *
import logging

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'