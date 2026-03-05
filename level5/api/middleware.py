import time
from django.utils.deprecation import MiddlewareMixin

class RequestLogginMiddleware(MiddlewareMixin):

    def process_request(self,request):
        request.start_time = time.time()
        return None
    
    def process_response(self,request,response):
        if hasattr(request,'start_time'):
            duration = time.time() - request.start_time
            print(f" {request.method} {request.path} - {response.status_code} - {duration:.2f} ")
        return response
    
class CustomHeaderMiddleware(MiddlewareMixin):

    def process_response(self,request,response):
        response['X-API-Version'] = '1.0'
        response['X-Powered-By'] = 'Django REST Framework'
        return response
    
    