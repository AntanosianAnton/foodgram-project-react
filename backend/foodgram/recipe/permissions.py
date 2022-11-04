from rest_framework import permissions


class IsAuthorOrAdmin(permissions.BasePermission):
    """Permission для авторов и администраторов."""

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated and (
                request.user.is_admin
                or obj.author == request.user or request.method == 'POST'):
            return True
        return request.method in permissions.SAFE_METHODS