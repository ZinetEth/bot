# apps/users/permissions.py

from rest_framework import permissions
from apps.CustomUser.models import UserRoles # Import Role enum from your CustomUser model

class IsAdmin(permissions.BasePermission):
    """
    Allows access only to Admin users.
    """
    def has_permission(self, request, view):
        # Assumes request.user is an instance of CustomUser and is authenticated
        return request.user and request.user.is_authenticated and request.user.role == Role.ADMIN

class IsStaff(permissions.BasePermission):
    """
    Allows access only to Staff users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == Role.STAFF

class IsAuditor(permissions.BasePermission):
    """
    Allows access only to Auditor users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == Role.AUDITOR

class IsStaffOrAdmin(permissions.BasePermission):
    """
    Allows access to Staff or Admin users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
               (request.user.role == Role.STAFF or request.user.role == Role.ADMIN)

class IsAdminOrAuditor(permissions.BasePermission):
    """
    Allows access to Admin or Auditor users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
               (request.user.role == Role.ADMIN or request.user.role == Role.AUDITOR)

# You can add more specific permissions if needed, e.g., IsOwner or IsSelf
class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Object-level permission to allow only owners of an object or admins to edit/view it.
    Assumes the model instance has a 'user' field.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated and request.user.role == Role.ADMIN:
            return True
        return obj.user == request.user