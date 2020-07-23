from rest_framework import permissions


class RelationIsOwner(permissions.BasePermission):
    """relation update/delete user """

    def has_object_permission(self, request, view, obj):
        return obj.from_user == request.user


class IsOwner(permissions.BasePermission):
    """
    update/delete : is_owner
    list/create/retrieve : is_authenticated
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in ['delete', 'patch']:
            return obj.user == request.user
        return bool(request.user and request.user.is_authenticated)


class UserIsOwner(permissions.BasePermission):
    """
    update/delete : is_owner
    create : is_authenticated
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in ['delete', 'patch']:
            return obj.user == request.user
        return bool(request.user and request.user.is_authenticated)
