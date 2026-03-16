import logging
from rest_framework import permissions

logger = logging.getLogger('user')

class IsRestaurantOwner(permissions.BasePermission):
    def has_object_permission(self,request,view,obj):
        logger.info("test!!")
        logger.info(self.request.user.has_perm("add_restrauntmodel"))
        if request.user.has_perm('add_restrauntmodel'):
            print("hello")
            return True
        return False

        
