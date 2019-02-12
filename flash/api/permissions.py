from rest_framework import permissions

class IsFriend(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            if obj.to_user.id == request.user.id:
                return True
            if obj.from_user.id == request.user.id:
                return True