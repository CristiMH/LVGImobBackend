from rest_framework import permissions
from rest_framework.permissions import BasePermission

from rest_framework import permissions

class CanUpdateUser(permissions.BasePermission):
    def has_permission(self, request, view):
        # All users must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False

        acting_type = getattr(request.user.user_type, 'id', None)

        # Restrict creation (POST)
        if request.method == 'POST':
            target_type = request.data.get('user_type_id')

            if not target_type:
                return True

            if acting_type == 1:
                return target_type in ['2', '3']
            elif acting_type == 2:
                return target_type == '3'
            return False

        return True  # For other methods, go to object permission

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if not request.user or not request.user.is_authenticated:
            return False

        acting_user = request.user
        target_user = obj

        acting_type = getattr(acting_user.user_type, 'id', None)
        target_type = getattr(target_user.user_type, 'id', None)

         # Get new role being set (if any)
        new_type_aux = request.data.get('user_type_id')
        
        try:
            new_type = int(new_type_aux)
        except (TypeError, ValueError):
            # Handle invalid value or missing key, e.g. set to None or raise error
            new_type = None

        # Each user can update themselves
        if acting_user.id == target_user.id and acting_type == new_type:
            return True

        # Permissions by role
        if acting_type == 1:
            return target_type in [2, 3] and new_type in ['2', '3', 2, 3]
        elif acting_type == 2:
            return target_type == 3 and new_type in ['3', 3]
        return False

class IsUserType2Or3(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'user_type') and request.user.user_type.id in [1, 2]
    

class IsOwnerOfListing(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user.user_type.id in [1, 2]:
            return True

        return obj.listing.user == request.user