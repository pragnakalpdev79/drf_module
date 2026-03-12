from rest_framework.pagination import CursorPagination #CURSOR PAGINATION
from rest_framework.pagination import LimitOffsetPagination

class BookLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 20
    limit_query_param ='limit'
    offset_query_param = 'offset'
    max_limit = 100

class BookCursorPagination(CursorPagination):
    page_size = 10
    ordering ='-created_at'
    cursor_query_param = 'cursor'

