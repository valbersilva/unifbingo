from rest_framework.permissions import BasePermission


class IsHostOrAdmin(BasePermission):
    """
    Allows only users with role 'host' or 'admin' to access.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['host', 'admin']
