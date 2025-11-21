"""
Dashboard views - role-specific dashboard pages.
"""
from typing import Any
from django.shortcuts import render, redirect
from ..decorators import (
    admin_required,
    operario_required,
    preparador_required,
    admin_or_operario_required
)
from ..services import dashboard_service


@admin_or_operario_required
def dashboard(request: Any):
    """Authenticated dashboard view - redirects based on role."""
    if hasattr(request.user, 'profile'):
        if request.user.profile.is_admin:
            return redirect('admin_dashboard')
        else:
            return redirect('operario_dashboard')
    return render(request, 'paginas/dashboard.html')


@admin_required
def admin_dashboard(request):
    """Administrative dashboard with statistics and reports."""
    context = dashboard_service.get_admin_dashboard_stats()
    return render(request, 'paginas/admin_dashboard.html', context)


@operario_required
def operario_dashboard(request):
    """Operario dashboard with quick access to common tasks."""
    context = dashboard_service.get_operario_dashboard_stats(request.user)
    return render(request, 'paginas/operario_dashboard.html', context)


@preparador_required
def preparador_dashboard(request):
    """Dashboard específico para preparadores de materias primas."""
    context = dashboard_service.get_preparador_dashboard_stats(request.user)
    return render(request, 'paginas/preparador_dashboard.html', context)
