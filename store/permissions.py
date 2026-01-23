# permissions.py
from rest_framework.permissions import BasePermission
 

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
            # print("token : ",token)
            if token == "34135930-2025":
                print("special token access granted  ")
                return True
 
        return True
            
    
        return False
