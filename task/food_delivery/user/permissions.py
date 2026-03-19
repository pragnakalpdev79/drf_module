import logging
from rest_framework import permissions

logger = logging.getLogger('user')

class IsRestaurantOwner(permissions.BasePermission):

    def has_permission(self, request,obj):
        if request.user.is_authenticated and request.user.has_perm('user.IsRestaurantOwner'):
            logger.info(f"The use has the permission to register a RESTRO")
            return True
        #print("error here")
        #print(request.user.check_if_restaurant)
        logger.info(f"The use does not have the permission to register a RESTRO")
        return False

        
class IsCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.has_perm('user.IsCustomer'):
            logger.info("The user has permission to place order as a customer")
            return True
        logger.info("The user does not has permission to place an order")
        return False
    
class IsDriver(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.has_perm('user.IsDriver'):
            logger.info("The user has permission to take the order as a driver")
            return True
        logger.info("The user does not have the permission to accpet the order as a driver")
        return False
    