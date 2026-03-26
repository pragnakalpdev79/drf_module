from rest_framework.pagination import LimitOffsetPagination,PageNumberPagination
from rest_framework.response import Response

class RestoPagination(PageNumberPagination):
    page_size = 2
    page_size_query_param = 'page_size'
    max_page_size = 1
    # default_limit = 50
    # limit_query_param = 'limit'
    # offset_query_param = 'offset'
    # max_limit = 1000p