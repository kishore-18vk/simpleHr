from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    Permission class that only allows admin users.
    """
    message = "Admin access required."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if user has an employee profile with admin role
        if hasattr(request.user, 'employee_profile'):
            return request.user.employee_profile.role == 'admin'
        
        # Superusers are also admins
        return request.user.is_superuser


class IsEmployee(permissions.BasePermission):
    """
    Permission class for authenticated employees.
    """
    message = "Employee access required."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Any authenticated user with employee profile can access
        if hasattr(request.user, 'employee_profile'):
            return True
        
        # Superusers can also access employee views
        return request.user.is_superuser


class IsAdminOrOwner(permissions.BasePermission):
    """
    Permission that allows admins full access, employees only their own data.
    """
    message = "You can only access your own data."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        # Admin has full access
        if hasattr(request.user, 'employee_profile'):
            if request.user.employee_profile.role == 'admin':
                return True
            # Employee can only access their own data
            if hasattr(obj, 'employee'):
                return obj.employee == request.user.employee_profile
            if hasattr(obj, 'user'):
                return obj.user == request.user
        
        return request.user.is_superuser
