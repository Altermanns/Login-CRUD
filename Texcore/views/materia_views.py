"""
Materia Prima views - CRUD operations for raw materials.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages
from ..forms import MateriaForm
from ..models import Materia
from ..decorators import admin_or_operario_required, operario_required
from ..services import materia_service


@admin_or_operario_required
def listar_materias(request):
    """List all materias ordered by newest first."""
    materias = materia_service.get_all_materias()
    return render(request, 'libros/index.html', {'materias': materias})


@operario_required
def crear_materia(request):
    """
    Create a new Materia.
    
    Uses a ModelForm to validate and persist data.
    Delegates business logic to materia_service.
    """
    if request.method == 'POST':
        form = MateriaForm(request.POST)
        
        if form.is_valid():
            materia = form.save(commit=False)
            materia.usuario_registro = request.user
            
            try:
                materia.save()
                messages.success(request, 'Materia creada correctamente.')
                return redirect('index_materia')
            except Exception as e:
                messages.error(request, f'Error al guardar: {e}')
        else:
            for field, errors in form.errors.items():
                messages.error(request, f'{field}: {errors}')
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
    """
    Redirects edit without id to materias list.
    
    Keeps a graceful behavior for users who access the edit URL without an id.
    """
    return redirect('index_materia')
