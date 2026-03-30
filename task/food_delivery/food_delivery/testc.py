# from django.core.cache import cache,cache_page
# from functools import wraps
# from django_redis import get_redis_connection


# redis_client = get_redis_connection("default")

# keys = redis_client.keys("menu_page:pgno_*")

# def delete_pattern(pattern):
#     redis_client = get_redis_connection("defualt")
#     keys = redis_client.keys(pattern)
#     if keys: 
#         redis_client.delete(*keys)

# def cache_page_for_anonymous(timeout):
#     def decorator(view_func):
#     @wraps(view_func)
#         def wrapper(request,*args,**kwargs):
#             if request.user.is_authenticated:
#                 return view_func(request,*args,**kwargs)
#             cached_view = cache_page(timeout)(view_func)
#             return cached_view(request,*args,**kwargs)
#         return wrapper
#     return decorator


# @cache_page_for_anonymous(60*15)
# def homepage(request):
#     return {
#         "message" : "Homepage"
#     }