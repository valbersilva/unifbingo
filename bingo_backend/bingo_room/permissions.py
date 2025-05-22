from rest_framework.permissions import BasePermission

class IsHostOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['host', 'admin']
