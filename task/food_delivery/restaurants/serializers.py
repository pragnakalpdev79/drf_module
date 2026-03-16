from rest_framework import serializers
from user.models import RestrauntModel
import logging,re

logger = logging.getLogger(__name__)

class RestoListSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = RestrauntModel
