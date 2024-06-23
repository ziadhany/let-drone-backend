from rest_framework import permissions


class IsPharmacist(permissions.BasePermission):
    def has_permission(self, request, view):
        # Implement your logic here
        # For example, allow access only to users with a specific role or staff status
        if request.user.is_authenticated and request.user.pharmacist:
            return True

        return True


class IsPatient(permissions.BasePermission):
    def has_permission(self, request, view):
        # Implement your logic here
        # For example, allow access only to users with a specific role or staff status
        if request.user.is_authenticated and request.user.patient:
            return True

        return True
