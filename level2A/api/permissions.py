from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self,request,view,obj):

        if request.method in permissions.SAFE_METHODS: #SAFE METHODS WILL BE CHECKED HERE, LIKE GET,HEAD,OPTIONS
            return True #IT WILL PERMIT IF THE USER IS ASKING FOR READ ONLY AND GIVE PERMISSION
        return obj.owner == request.user #WILL RETURN TRUE IF OWNER IS USER ONLY
    
    