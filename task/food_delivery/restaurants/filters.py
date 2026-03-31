import django_filters
from user.models import *

class RestoFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = RestrauntModel
        fields = ['name']