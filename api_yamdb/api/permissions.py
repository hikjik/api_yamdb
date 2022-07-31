from rest_framework import permissions
from reviews.models import User


class IsAdminPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            User.objects.get(username=request.user).role == 'admin'
        )