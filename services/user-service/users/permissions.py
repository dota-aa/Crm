from rest_framework.permissions import BasePermission


class CustomPermission(BasePermission):
    message = 'User does not have required permission'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_admin or request.user.is_superuser:
            return True

        permissions = getattr(view, 'required_permissions', None)
        print(permissions)
        if not permissions:
            return True

        for permission in permissions:
            if not request.user.has_permission(permission):
                return False

        return True
