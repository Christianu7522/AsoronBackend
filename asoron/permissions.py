from rest_framework import permissions

class IsReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS 

class NoReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.method not in ['POST', 'PUT', 'DELETE']