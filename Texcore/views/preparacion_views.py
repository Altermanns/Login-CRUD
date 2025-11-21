"""
Preparacion views - material preparation process management.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from ..forms import PreparacionMateriaForm, DetallePreparacionForm, FiltroPreparacionForm
from ..models import PreparacionMateria, DetallePreparacion
from ..decorators import (
    admin_required,
    preparador_required,
    admin_or_preparador_required
)
from ..services import preparacion_service, materia_service, dashboard_service


@admin_or_preparador_required
def listar_preparaciones(request):
    """Lista todas las preparaciones con filtros."""
    preparaciones = preparacion_service.get_all_preparaciones()
    
    # Apply filters if they exist
    filtro_form = FiltroPreparacionForm(request.GET)
    if filtro_form.is_valid():
        preparaciones = preparacion_service.filtrar_preparaciones(
            estado=filtro_form.cleaned_data.get('estado'),
            tipo_proceso=filtro_form.cleaned_data.get('tipo_proceso'),
            fecha_desde=filtro_form.cleaned_data.get('fecha_desde'),
            fecha_hasta=filtro_form.cleaned_data.get('fecha_hasta')
        )
    
    context = {
        'preparaciones': preparaciones,
        'filtro_form': filtro_form,
    }
    return render(request, 'preparacion/lista.html', context)


@preparador_required
def crear_preparacion(request):
    """Crear una nueva preparación de materia prima."""
    if request.method == 'POST':
        form = PreparacionMateriaForm(request.POST)
        if form.is_valid():
            materia = form.cleaned_data['materia_prima']
            cantidad_requerida = form.cleaned_data['cantidad_procesada']
            
            # Validate stock using service
            is_valid, error_msg = preparacion_service.validar_stock_disponible(
                materia, cantidad_requerida
            )
            if not is_valid:
                messages.error(request, error_msg)
                return render(request, 'preparacion/crear.html', {
                    'form': form,
                    'materias_con_stock': materia_service.get_materias_disponibles_para_preparacion(),
                })
            
            # Check for low stock warning
            is_low, warning_msg = preparacion_service.verificar_stock_bajo(
                materia, cantidad_requerida
            )
            if is_low:
                messages.warning(request, warning_msg)
            
            try:
                # Create preparation using service
                preparacion = preparacion_service.crear_preparacion(
                    materia_prima=materia,
                    tipo_proceso=form.cleaned_data['tipo_proceso'],
                    cantidad_procesada=cantidad_requerida,
                    usuario_preparador=request.user,
                    porcentaje_mezcla=form.cleaned_data.get('porcentaje_mezcla'),
                    observaciones=form.cleaned_data.get('observaciones', ''),
                    calidad_resultado=form.cleaned_data.get('calidad_resultado')
                )
                
                messages.success(
                    request,
                    f'Preparación creada exitosamente. Se reservaron {cantidad_requerida}kg '
                    f'de {materia.tipo} para {preparacion.get_tipo_proceso_display()}.'
                )
                return redirect('detalle_preparacion', preparacion_id=preparacion.id)
                
            except ValueError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, f'Error al crear preparación: {str(e)}')
        else:
            for field, errors in form.errors.items():
                messages.error(request, f'{field}: {errors}')
    else:
        form = PreparacionMateriaForm()
    
    # Get additional info for template
    materias_con_stock = materia_service.get_materias_disponibles_para_preparacion()
    
    context = {
        'form': form,
        'materias_con_stock': materias_con_stock,
    }
    return render(request, 'preparacion/crear.html', context)


@admin_or_preparador_required
def detalle_preparacion(request, preparacion_id):
    """Ver detalles de una preparación específica."""
    preparacion = get_object_or_404(
        PreparacionMateria.objects.select_related(
            'materia_prima', 'usuario_preparador'
        ).prefetch_related('detalles'),
        pk=preparacion_id
    )
    detalles = preparacion.detalles.all()
    
    context = {
        'preparacion': preparacion,
        'detalles': detalles,
    }
    return render(request, 'preparacion/detalle.html', context)


@preparador_required
def iniciar_preparacion(request, preparacion_id):
    """Iniciar el proceso de una preparación pendiente."""
    preparacion = get_object_or_404(PreparacionMateria, pk=preparacion_id)
    
    # Use service to start preparation
    success, message = preparacion_service.iniciar_preparacion_proceso(
        preparacion, request.user
    )
    
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
    
    return redirect('detalle_preparacion', preparacion_id=preparacion.id)


@preparador_required
def completar_preparacion(request, preparacion_id):
    """Completar una preparación en proceso."""
    preparacion = get_object_or_404(PreparacionMateria, pk=preparacion_id)
    
    # Use service to complete preparation (includes stock update)
    success, message = preparacion_service.completar_preparacion_proceso(
        preparacion, request.user
    )
    
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
    
    return redirect('detalle_preparacion', preparacion_id=preparacion.id)


@preparador_required
def agregar_detalle_preparacion(request, preparacion_id):
    """Agregar detalles técnicos a una preparación."""
    preparacion = get_object_or_404(PreparacionMateria, pk=preparacion_id)
    
    # Only assigned preparador can add details
    if preparacion.usuario_preparador != request.user:
        messages.error(request, 'Solo puedes agregar detalles a tus propias preparaciones.')
        return redirect('listar_preparaciones')
    
    if request.method == 'POST':
        form = DetallePreparacionForm(request.POST)
        if form.is_valid():
            detalle = form.save(commit=False)
            detalle.preparacion = preparacion
            detalle.save()
            
            messages.success(request, 'Detalles técnicos agregados exitosamente.')
            return redirect('detalle_preparacion', preparacion_id=preparacion.id)
        else:
            for field, errors in form.errors.items():
                messages.error(request, f'{field}: {errors}')
    else:
        form = DetallePreparacionForm()
    
    context = {
        'form': form,
        'preparacion': preparacion,
    }
    return render(request, 'preparacion/agregar_detalle.html', context)


@preparador_required
def editar_preparacion(request, preparacion_id):
    """Editar una preparación (solo si está pendiente)."""
    preparacion = get_object_or_404(PreparacionMateria, pk=preparacion_id)
    
    # Only assigned preparador can edit
    if preparacion.usuario_preparador != request.user:
        messages.error(request, 'Solo puedes editar tus propias preparaciones.')
        return redirect('listar_preparaciones')
    
    # Can only edit if pending
    if preparacion.estado != 'pendiente':
        messages.error(request, 'Solo se pueden editar preparaciones pendientes.')
        return redirect('detalle_preparacion', preparacion_id=preparacion.id)
    
    if request.method == 'POST':
        form = PreparacionMateriaForm(request.POST, instance=preparacion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Preparación actualizada exitosamente.')
            return redirect('detalle_preparacion', preparacion_id=preparacion.id)
        else:
            for field, errors in form.errors.items():
                messages.error(request, f'{field}: {errors}')
    else:
        form = PreparacionMateriaForm(instance=preparacion)
    
    context = {
        'form': form,
        'preparacion': preparacion,
    }
    return render(request, 'preparacion/editar.html', context)


@admin_required
def eliminar_preparacion(request, preparacion_id):
    """Eliminar una preparación (solo admin y solo si está pendiente)."""
    preparacion = get_object_or_404(PreparacionMateria, pk=preparacion_id)
    
    if preparacion.estado != 'pendiente':
        messages.error(request, 'Solo se pueden eliminar preparaciones pendientes.')
        return redirect('detalle_preparacion', preparacion_id=preparacion.id)
    
    if request.method == 'POST':
        preparacion.delete()
        messages.success(request, 'Preparación eliminada exitosamente.')
        return redirect('listar_preparaciones')
    
    return render(request, 'preparacion/confirmar_eliminar.html', {'preparacion': preparacion})


@admin_or_preparador_required
def reporte_preparaciones(request):
    """Generar reporte de preparaciones."""
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    estado_filtro = request.GET.get('estado')
    
    # Use service to get report statistics
    context = dashboard_service.get_reporte_preparaciones_stats(
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        estado_filtro=estado_filtro
    )
    
    return render(request, 'preparacion/reporte.html', context)
