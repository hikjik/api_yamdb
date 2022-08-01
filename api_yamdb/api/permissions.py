from rest_framework.permissions import SAFE_METHODS, BasePermission
from reviews.models import User


class IsAdminPermission(BasePermission):
    def has_permission(self, request, view):
        return (
            User.objects.get(username=request.user).role == 'admin' or request.user.is_superuser
         )


class IsAdminOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or request.user.is_admin()
        )


class IsAdminOrModeratorOrAuthorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or request.user.is_admin()
            or request.user.is_moderator()
            or request.user == obj.author
        )
