from rest_framework import serializers
from .models import *
import os

class ProfileSerializer(serializers.ModelSerializer):

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
        