# permissions.py
from rest_framework.permissions import BasePermission
 
from .mongo import users
from .auth_views import get_user_by_id
class HasTokenPermission(BasePermission):
    
    """
    Allows access only if the request has an Authorization header with a token.
    """

    def has_permission(self, request, view):
        print(" \n\n\n ============")
        print(request)
        # return True
        auth_header = request.headers.get('Authorization')
        if auth_header :
            token = auth_header.split(' ')[1]
            user = users.find_one({"token": token})
            if user:
                return True
            else:
                return False
 
        return False
