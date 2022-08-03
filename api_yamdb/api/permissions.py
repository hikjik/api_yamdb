from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS, BasePermission
from reviews.models import User


class IsAdminPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return (
                User.objects.get(username=request.user).role == 'admin'
                or request.user.is_superuser
            )
        else:
            return False


class IsSuperUserPermission(BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_superuser)


class IsUserAuthenticatedPermission(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated

class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_admin


class IsAdminOrModeratorOrAuthorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or request.user.is_admin
            or request.user.is_moderator
            or request.user == obj.author
        )
