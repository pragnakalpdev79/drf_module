import django_filters
from .models import Task,Book

class TaskFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    created_after = django_filters.DateFilter(field_name='created_at',lookup_expr='gte')
    created_before = django_filters.DateFilter(field_name='created_at',lookup_expr='lte')
    completed = django_filters.BooleanFilter()
    class Meta:
        model = Task
        fields = ['completed','title','created_after','created_before','priority']
        
class BookFilter(django_filters.FilterSet):
    author = django_filters.CharFilter(lookup_expr='icontain')
    published_after = django_filters.DateFilter(field_name='published_date',lookup_expr='gte')
    published_before = django_filters.DateFilter(field_name='published_date',lookup_expr='lte')
    class Meta:
        model = Book
        fields = ['author','published_after','published_before']