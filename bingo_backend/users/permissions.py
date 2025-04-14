from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsHost(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'host'


class IsPlayer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'player'
