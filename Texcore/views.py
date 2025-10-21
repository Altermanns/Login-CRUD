from typing import Any

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages

from .forms import MateriaForm
from .models import Materia
from . import services

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
            return redirect('index')
        messages.error(request, 'Usuario o contraseña inválidos')
        return redirect('login')

    return render(request, 'paginas/login.html')


@login_required
@login_required
def dashboard(request: Any):
    """Authenticated dashboard view."""
    return render(request, 'paginas/dashboard.html')


@login_required
@login_required
def listar_materias(request):
    """List all materias ordered by newest first."""
    materias = services.get_all_materias()
    return render(request, 'libros/index.html', {'materias': materias})


@login_required
@login_required
def crear_materia(request):
    """Create a new Materia.

    Uses a ModelForm to validate and persist data.
    """
    if request.method == 'POST':
        form = MateriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Materia creada correctamente.')
            return redirect('index_materia')
    else:
        form = MateriaForm()
    return render(request, 'libros/crear.html', {'form': form})


@login_required
@login_required
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


@login_required
@require_POST
@login_required
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
