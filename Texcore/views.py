from typing import Any
from datetime import datetime, date
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages

from .forms import MateriaForm
from .models import Materia
from . import services
from .decorators import admin_required, operario_required, admin_or_operario_required

def inicio(request):
    """Landing page: public and minimal."""
    return render(request, 'paginas/inicio.html')

def login(request):
    """Authenticate and log the user in.

    Authentication logic is delegated to services.authenticate_user for easier
    testing and separation of concerns.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = services.authenticate_user(request, username, password)
        if user is not None:
            auth_login(request, user)
            # Redirect based on user role
            if hasattr(user, 'profile'):
                if user.profile.is_admin:
                    return redirect('admin_dashboard')
                else:
                    return redirect('operario_dashboard')
            return redirect('index')
        messages.error(request, 'Usuario o contraseña inválidos')
        return redirect('login')

    return render(request, 'paginas/login.html')


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
    # Get statistics
    total_materias = Materia.objects.count()
    total_cantidad = Materia.objects.aggregate(total=Sum('cantidad'))['total'] or 0
    
    # Materials by type
    materias_por_tipo = Materia.objects.values('tipo').annotate(
        total_cantidad=Sum('cantidad'),
        total_lotes=Count('id')
    ).order_by('-total_cantidad')
    
    # Monthly entries (last 6 months)
    materias_por_mes = Materia.objects.filter(
        fecha_ingreso__isnull=False
    ).annotate(
        month=TruncMonth('fecha_ingreso')
    ).values('month').annotate(
        total=Count('id'),
        cantidad_total=Sum('cantidad')
    ).order_by('-month')[:6]
    
    # Recent entries
    entradas_recientes = Materia.objects.select_related('usuario_registro').order_by('-id')[:10]
    
    context = {
        'total_materias': total_materias,
        'total_cantidad': total_cantidad,
        'materias_por_tipo': materias_por_tipo[:5],  # Top 5
        'materias_por_mes': list(materias_por_mes),
        'entradas_recientes': entradas_recientes,
    }
    
    return render(request, 'paginas/admin_dashboard.html', context)


@operario_required
def operario_dashboard(request):
    """Operario dashboard with quick access to common tasks."""
    # Get operario's recent entries
    mis_entradas = Materia.objects.filter(
        usuario_registro=request.user
    ).order_by('-id')[:5]
    
    # Get today's entries
    entradas_hoy = Materia.objects.filter(
        fecha_ingreso=date.today()
    ).count()
    
    context = {
        'mis_entradas': mis_entradas,
        'entradas_hoy': entradas_hoy,
    }
    
    return render(request, 'paginas/operario_dashboard.html', context)


@admin_or_operario_required
def listar_materias(request):
    """List all materias ordered by newest first."""
    materias = services.get_all_materias()
    return render(request, 'libros/index.html', {'materias': materias})


@operario_required
def crear_materia(request):
    """Create a new Materia.

    Uses a ModelForm to validate and persist data.
    """
    if request.method == 'POST':
        form = MateriaForm(request.POST)
        if form.is_valid():
            materia = form.save(commit=False)
            materia.usuario_registro = request.user
            materia.save()
            messages.success(request, 'Materia creada correctamente.')
            return redirect('index_materia')
    else:
        form = MateriaForm()
    return render(request, 'libros/crear.html', {'form': form})


@operario_required
def editar_materia(request, materia_id: int):
    """Edit an existing Materia identified by materia_id."""
    materia = get_object_or_404(Materia, pk=materia_id)
    if request.method == 'POST':
        form = MateriaForm(request.POST, instance=materia)
        if form.is_valid():
            form.save()
            messages.success(request, 'Materia actualizada correctamente.')
            return redirect('index_materia')
    else:
        form = MateriaForm(instance=materia)
    return render(request, 'libros/editar.html', {'form': form})


@operario_required
@require_POST
def eliminar_materia(request, materia_id: int):
    """Delete a Materia (POST only)."""
    materia = get_object_or_404(Materia, pk=materia_id)
    materia.delete()
    messages.success(request, 'Materia eliminada correctamente.')
    return redirect('index_materia')


def editar_materia_no_id(request):
    """Redirects edit without id to materias list.

    Keeps a graceful behavior for users who access the edit URL without an id.
    """
    return redirect('index_materia')


def logout(request):
    """Log out the current user and redirect to the public landing page."""
    auth_logout(request)
    return redirect('inicio')
