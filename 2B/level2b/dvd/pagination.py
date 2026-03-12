from rest_framework.pagination import CursorPagination #CURSOR PAGINATION
from rest_framework.pagination import LimitOffsetPagination

class MyLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 20
    limit_query_param ='limit'
    offset_query_param = 'offset'
    max_limit = 100 
    #COMPARING LIMITOFFSET VS PAGENUMBER
    # offset seems more easier in case we know our data but page number pagination is good for user experience
    

class MyCursorPagination(CursorPagination):
    page_size = 10
    ordering ='-created_at'
    cursor_query_param = 'cursor'

