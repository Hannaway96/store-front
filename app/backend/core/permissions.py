from rest_framework.permissions import BasePermission


class isOwner(BasePermission):
    """
    Custom Permission to only allow object access to user
    """

    def has_object_permission(self, request, view, obj):
        """Allow permission if the object belongs to the user"""
        if hasattr(obj, "user"):
            return obj.user == request.user
        if hasattr(obj, "user_id"):
            return obj.user_id == request.user.id
        if hasattr(obj, "id"):
            return obj.id == request.user.id
        return False


class isReadOnly(BasePermission):
    """
    Custom Permission to allow read access to all
    """

    def has_object_permission(self, request, view, obj):
        """Read permission allowed to all Users"""
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True


class isOwnerOrReadOnly(isReadOnly, isOwner):
    """
    Custom Permission combining isOwner and isReadOnly
    """

    def has_object_permission(self, request, view, obj):
        """Read permission allowed to all Users"""
        if super().has_object_permission(request, view, obj):
            return True
        return isOwner.has_object_permission(self, request, view, obj)
