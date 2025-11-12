from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages


def role_required(role):
    """
    Decorator to require a specific role.
    Usage: @role_required('admin') or @role_required('operario')
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            # Check if user has a profile
            if not hasattr(request.user, 'profile'):
                messages.error(request, 'Tu usuario no tiene un perfil asignado. Contacta al administrador.')
                return redirect('inicio')
            
            # Check if user has the required role
            if request.user.profile.role != role:
                messages.error(request, f'No tienes permisos para acceder a esta página. Se requiere rol: {role}')
                return redirect('inicio')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def admin_required(view_func):
    """
    Decorator to require admin role.
    Usage: @admin_required
    """
    return role_required('admin')(view_func)


def operario_required(view_func):
    """
    Decorator to require operario role.
    Usage: @operario_required
    """
    return role_required('operario')(view_func)


def admin_or_operario_required(view_func):
    """
    Decorator that allows both admin and operario roles.
    Usage: @admin_or_operario_required
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        # Check if user has a profile
        if not hasattr(request.user, 'profile'):
            messages.error(request, 'Tu usuario no tiene un perfil asignado. Contacta al administrador.')
            return redirect('inicio')
        
        # Check if user has admin or operario role
        if request.user.profile.role not in ['admin', 'operario']:
            messages.error(request, 'No tienes permisos para acceder a esta página.')
            return redirect('inicio')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view