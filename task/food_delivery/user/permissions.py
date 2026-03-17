import logging
from rest_framework import permissions

logger = logging.getLogger('user')

class IsRestaurantOwner(permissions.BasePermission):

    def has_permission(self, request,obj):
        if request.user.is_authenticated and request.user.has_perm('user.add_restrauntmodel'):
            logger.info(f"The use has the permission to register a RESTRO")
            return True
        #print("error here")
        #print(request.user.check_if_restaurant)
        logger.info(f"The use does not have the permission to register a RESTRO")
        return False

        
