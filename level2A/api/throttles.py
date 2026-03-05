from rest_framework import throttling
from django.core.cache import cache

class BookCreateThrottle(throttling.BaseThrottle):
    def allow_request(self,request,view):
        ip = self.get_ident(request)
        cache_key = f'throttle_{ip}'
        request_count = cache.get(cache_key,0)
        if request_count >= 5:
            return False
        print(request_count)
        cache.set(cache_key,request_count+1,60)
        return True


    