from rest_framework.pagination import PageNumberPagination,LimitOffsetPagination,CursorPagination
from rest_framework.response import Response

class StandardResultSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'param_size'
    max_page_size = 100

class LargeResultSetPagination(LimitOffsetPagination):
    default_limit = 50
    limit_query_param = 'limit'
    offset_query_param = 'offset'
    max_limit = 1000

class TaskCursorPagination(CursorPagination):
    page_size = 25
    ordering = '-created_at'
    cursor_query_param = 'cursor'

class CustomPagination(PageNumberPagination):
    page_size = 20
    def get_paginated_response(self,data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous' : self.get_previous_link(),
            }
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page' : self.page.number,
            'results' : data,
        })