from rest_framework.throttling import UserRateThrottle

class OrderCreateT(UserRateThrottle):
    rate = '200/hour'

class ReviewCreateT(UserRateThrottle):
    rate = '100/hour'    

class LocationUp(UserRateThrottle):
    rate = '500/hour'