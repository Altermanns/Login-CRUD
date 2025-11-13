from typing import Any
from datetime import datetime, date
from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncMonth
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone

from .forms import MateriaForm, PreparacionMateriaForm, DetallePreparacionForm, FiltroPreparacionForm
from .models import Materia, Profile, PreparacionMateria, DetallePreparacion
from . import services
from .decorators import (admin_required, operario_required, admin_or_operario_required, 
                        preparador_required, admin_or_preparador_required)

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
                elif user.profile.is_preparador:
                    return redirect('preparador_dashboard')
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
    # Get statistics for materias primas
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
    
    # ======== NUEVAS ESTADÍSTICAS DE PREPARACIÓN ========
    
    # Estadísticas de preparación
    from .models import PreparacionMateria
    total_preparaciones = PreparacionMateria.objects.count()
    preparaciones_pendientes = PreparacionMateria.objects.filter(estado='pendiente').count()
    preparaciones_en_proceso = PreparacionMateria.objects.filter(estado='en_proceso').count()
    preparaciones_completadas = PreparacionMateria.objects.filter(estado='completada').count()
    
    # Materiales procesados por tipo (cantidad total procesada)
    materiales_procesados = PreparacionMateria.objects.filter(
        estado='completada'
    ).values('materia_prima__tipo').annotate(
        cantidad_procesada=Sum('cantidad_procesada'),
        total_preparaciones=Count('id')
    ).order_by('-cantidad_procesada')
    
    # Preparaciones recientes
    preparaciones_recientes = PreparacionMateria.objects.select_related(
        'materia_prima', 'usuario_preparador'
    ).order_by('-fecha_inicio')[:8]
    
    # Preparadores más activos
    preparadores_activos = PreparacionMateria.objects.values(
        'usuario_preparador__first_name',
        'usuario_preparador__last_name'
    ).annotate(
        total_preparaciones=Count('id'),
        completadas=Count('id', filter=Q(estado='completada')),
        cantidad_total=Sum('cantidad_procesada', filter=Q(estado='completada'))
    ).order_by('-total_preparaciones')[:5]
    
    context = {
        # Estadísticas originales
        'total_materias': total_materias,
        'total_cantidad': total_cantidad,
        'materias_por_tipo': materias_por_tipo[:5],  # Top 5
        'materias_por_mes': list(materias_por_mes),
        'entradas_recientes': entradas_recientes,
        
        # Nuevas estadísticas de preparación
        'total_preparaciones': total_preparaciones,
        'preparaciones_pendientes': preparaciones_pendientes,
        'preparaciones_en_proceso': preparaciones_en_proceso,
        'preparaciones_completadas': preparaciones_completadas,
        'materiales_procesados': materiales_procesados[:5],
        'preparaciones_recientes': preparaciones_recientes,
        'preparadores_activos': preparadores_activos,
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
    """Redirects edit without id to materias list.

    Keeps a graceful behavior for users who access the edit URL without an id.
    """
    return redirect('index_materia')


def logout(request):
    """Log out the current user and redirect to the public landing page."""
    auth_logout(request)
    return redirect('inicio')


# ====== GESTIÓN DE USUARIOS (SOLO ADMIN) ======

@admin_required
def listar_usuarios(request):
    """List all users with their roles - Admin only."""
    usuarios = User.objects.select_related('profile').all().order_by('username')
    context = {
        'usuarios': usuarios,
    }
    return render(request, 'usuarios/lista.html', context)


@admin_required  
def crear_usuario(request):
    """Create new user with role assignment - Admin only."""
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        role = request.POST.get('role')
        
        # Validaciones
        if not all([username, first_name, last_name, email, password, role]):
            messages.error(request, 'Todos los campos son obligatorios.')
            return render(request, 'usuarios/crear.html')
        
        if password != confirm_password:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'usuarios/crear.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya existe.')
            return render(request, 'usuarios/crear.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'El email ya está registrado.')
            return render(request, 'usuarios/crear.html')
        
        try:
            # Crear usuario
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            # Asignar rol
            profile, created = Profile.objects.get_or_create(user=user)
            profile.role = role
            profile.save()
            
            messages.success(request, f'Usuario {username} creado exitosamente con rol {profile.get_role_display()}.')
            return redirect('listar_usuarios')
            
        except Exception as e:
            messages.error(request, f'Error al crear usuario: {str(e)}')
            return render(request, 'usuarios/crear.html')
    
    return render(request, 'usuarios/crear.html')


@admin_required
def editar_usuario(request, user_id):
    """Edit existing user and role - Admin only."""
    usuario = get_object_or_404(User, pk=user_id)
    
    # No permitir que el admin se edite a sí mismo para evitar bloqueos
    if usuario == request.user:
        messages.warning(request, 'No puedes editar tu propio usuario.')
        return redirect('listar_usuarios')
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        role = request.POST.get('role')
        is_active = request.POST.get('is_active') == 'on'
        
        # Validaciones
        if not all([first_name, last_name, email, role]):
            messages.error(request, 'Todos los campos son obligatorios.')
            return render(request, 'usuarios/editar.html', {'usuario': usuario})
        
        # Verificar email único (excluyendo el usuario actual)
        if User.objects.filter(email=email).exclude(pk=usuario.pk).exists():
            messages.error(request, 'El email ya está registrado por otro usuario.')
            return render(request, 'usuarios/editar.html', {'usuario': usuario})
        
        try:
            # Actualizar usuario
            usuario.first_name = first_name
            usuario.last_name = last_name
            usuario.email = email
            usuario.is_active = is_active
            usuario.save()
            
            # Actualizar rol
            profile, created = Profile.objects.get_or_create(user=usuario)
            profile.role = role
            profile.save()
            
            messages.success(request, f'Usuario {usuario.username} actualizado exitosamente.')
            return redirect('listar_usuarios')
            
        except Exception as e:
            messages.error(request, f'Error al actualizar usuario: {str(e)}')
    
    return render(request, 'usuarios/editar.html', {'usuario': usuario})


@admin_required
@require_POST
def eliminar_usuario(request, user_id):
    """Delete user (soft delete by deactivating) - Admin only."""
    usuario = get_object_or_404(User, pk=user_id)
    
    # No permitir eliminar al propio usuario
    if usuario == request.user:
        messages.error(request, 'No puedes eliminar tu propio usuario.')
        return redirect('listar_usuarios')
    
    # No eliminar, solo desactivar
    usuario.is_active = False
    usuario.save()
    
    messages.success(request, f'Usuario {usuario.username} desactivado exitosamente.')
    return redirect('listar_usuarios')


# ====== PREPARACIÓN DE MATERIAS PRIMAS (PREPARADOR + ADMIN) ======

@preparador_required
def preparador_dashboard(request):
    """Dashboard específico para preparadores de materias primas."""
    # Estadísticas del preparador
    preparaciones_usuario = PreparacionMateria.objects.filter(
        usuario_preparador=request.user
    )
    
    total_preparaciones = preparaciones_usuario.count()
    en_proceso = preparaciones_usuario.filter(estado='en_proceso').count()
    completadas_hoy = preparaciones_usuario.filter(
        fecha_completado__date=date.today()
    ).count()
    pendientes = preparaciones_usuario.filter(estado='pendiente').count()
    
    # Preparaciones recientes del usuario
    preparaciones_recientes = preparaciones_usuario.order_by('-fecha_inicio')[:5]
    
    # Materias disponibles para procesar
    materias_disponibles = Materia.objects.filter(
        preparacionmateria__isnull=True
    ).count()
    
    context = {
        'total_preparaciones': total_preparaciones,
        'en_proceso': en_proceso,
        'completadas_hoy': completadas_hoy,
        'pendientes': pendientes,
        'preparaciones_recientes': preparaciones_recientes,
        'materias_disponibles': materias_disponibles,
    }
    
    return render(request, 'paginas/preparador_dashboard.html', context)


@admin_or_preparador_required
def listar_preparaciones(request):
    """Lista todas las preparaciones con filtros."""
    preparaciones = PreparacionMateria.objects.select_related(
        'materia_prima', 'usuario_preparador'
    ).order_by('-fecha_inicio')
    
    # Aplicar filtros si existen
    filtro_form = FiltroPreparacionForm(request.GET)
    if filtro_form.is_valid():
        if filtro_form.cleaned_data['estado']:
            preparaciones = preparaciones.filter(
                estado=filtro_form.cleaned_data['estado']
            )
        if filtro_form.cleaned_data['tipo_proceso']:
            preparaciones = preparaciones.filter(
                tipo_proceso=filtro_form.cleaned_data['tipo_proceso']
            )
        if filtro_form.cleaned_data['fecha_desde']:
            preparaciones = preparaciones.filter(
                fecha_inicio__date__gte=filtro_form.cleaned_data['fecha_desde']
            )
        if filtro_form.cleaned_data['fecha_hasta']:
            preparaciones = preparaciones.filter(
                fecha_inicio__date__lte=filtro_form.cleaned_data['fecha_hasta']
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
            preparacion = form.save(commit=False)
            preparacion.usuario_preparador = request.user
            preparacion.estado = 'pendiente'
            
            # Validar que hay suficiente stock
            materia = preparacion.materia_prima
            cantidad_requerida = preparacion.cantidad_procesada
            
            if materia.cantidad < cantidad_requerida:
                messages.error(request, 
                    f'Stock insuficiente. Disponible: {materia.cantidad}kg, '
                    f'Requerido: {cantidad_requerida}kg para {materia.tipo}.')
                return render(request, 'preparacion/crear.html', {'form': form})
            
            # Advertir si queda poco stock
            stock_restante = materia.cantidad - cantidad_requerida
            if stock_restante < (materia.cantidad * 0.2):  # Menos del 20%
                messages.warning(request, 
                    f'¡Advertencia! Después de procesar quedarán solo {stock_restante}kg '
                    f'de {materia.tipo} (menos del 20% del stock original).')
            
            preparacion.save()
            
            messages.success(request, 
                f'Preparación creada exitosamente. Se reservaron {cantidad_requerida}kg '
                f'de {materia.tipo} para {preparacion.get_tipo_proceso_display()}.')
            return redirect('detalle_preparacion', preparacion_id=preparacion.id)
        else:
            for field, errors in form.errors.items():
                messages.error(request, f'{field}: {errors}')
    else:
        form = PreparacionMateriaForm()
    
    # Obtener información adicional para el template
    materias_con_stock = Materia.objects.filter(cantidad__gt=0).order_by('tipo', '-cantidad')
    
    context = {
        'form': form,
        'materias_con_stock': materias_con_stock,
    }
    return render(request, 'preparacion/crear.html', context)


@admin_or_preparador_required
def detalle_preparacion(request, preparacion_id):
    """Ver detalles de una preparación específica."""
    preparacion = get_object_or_404(PreparacionMateria, pk=preparacion_id)
    detalles = DetallePreparacion.objects.filter(preparacion=preparacion)
    
    context = {
        'preparacion': preparacion,
        'detalles': detalles,
    }
    return render(request, 'preparacion/detalle.html', context)


@preparador_required
def iniciar_preparacion(request, preparacion_id):
    """Iniciar el proceso de una preparación pendiente."""
    preparacion = get_object_or_404(PreparacionMateria, pk=preparacion_id)
    
    # Solo el preparador asignado puede iniciar
    if preparacion.usuario_preparador != request.user:
        messages.error(request, 'Solo puedes iniciar tus propias preparaciones.')
        return redirect('listar_preparaciones')
    
    if preparacion.estado != 'pendiente':
        messages.error(request, 'Solo se pueden iniciar preparaciones pendientes.')
        return redirect('detalle_preparacion', preparacion_id=preparacion.id)
    
    preparacion.estado = 'en_proceso'
    preparacion.save()
    
    messages.success(request, 'Preparación iniciada exitosamente.')
    return redirect('detalle_preparacion', preparacion_id=preparacion.id)


@preparador_required
def completar_preparacion(request, preparacion_id):
    """Completar una preparación en proceso."""
    preparacion = get_object_or_404(PreparacionMateria, pk=preparacion_id)
    
    # Solo el preparador asignado puede completar
    if preparacion.usuario_preparador != request.user:
        messages.error(request, 'Solo puedes completar tus propias preparaciones.')
        return redirect('listar_preparaciones')
    
    if preparacion.estado != 'en_proceso':
        messages.error(request, 'Solo se pueden completar preparaciones en proceso.')
        return redirect('detalle_preparacion', preparacion_id=preparacion.id)
    
    # Actualizar el stock de la materia prima
    materia = preparacion.materia_prima
    cantidad_procesada = preparacion.cantidad_procesada
    
    # Verificar que hay suficiente stock
    if materia.cantidad < cantidad_procesada:
        messages.error(request, f'No hay suficiente stock. Disponible: {materia.cantidad}kg, Requerido: {cantidad_procesada}kg')
        return redirect('detalle_preparacion', preparacion_id=preparacion.id)
    
    # Reducir el stock de la materia prima
    materia.cantidad -= cantidad_procesada
    materia.save()
    
    # Completar la preparación
    preparacion.estado = 'completada'
    preparacion.fecha_completado = timezone.now()
    preparacion.save()
    
    messages.success(request, f'Preparación completada exitosamente. Se procesaron {cantidad_procesada}kg de {materia.tipo}.')
    messages.info(request, f'Stock restante de {materia.tipo}: {materia.cantidad}kg')
    return redirect('detalle_preparacion', preparacion_id=preparacion.id)


@preparador_required
def agregar_detalle_preparacion(request, preparacion_id):
    """Agregar detalles técnicos a una preparación."""
    preparacion = get_object_or_404(PreparacionMateria, pk=preparacion_id)
    
    # Solo el preparador asignado puede agregar detalles
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
    
    # Solo el preparador asignado puede editar
    if preparacion.usuario_preparador != request.user:
        messages.error(request, 'Solo puedes editar tus propias preparaciones.')
        return redirect('listar_preparaciones')
    
    # Solo se puede editar si está pendiente
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
    # Filtros de fecha
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    estado_filtro = request.GET.get('estado')
    
    # QuerySet base
    preparaciones = PreparacionMateria.objects.select_related(
        'materia_prima', 'usuario_preparador'
    ).order_by('-fecha_inicio')
    
    # Aplicar filtros
    if fecha_inicio:
        preparaciones = preparaciones.filter(fecha_inicio__date__gte=fecha_inicio)
    
    if fecha_fin:
        preparaciones = preparaciones.filter(fecha_inicio__date__lte=fecha_fin)
    
    if estado_filtro:
        preparaciones = preparaciones.filter(estado=estado_filtro)
    
    # Estadísticas generales
    total_preparaciones = preparaciones.count()
    preparaciones_completadas = preparaciones.filter(estado='completada').count()
    preparaciones_en_proceso = preparaciones.filter(estado='en_proceso').count()
    preparaciones_pendientes = preparaciones.filter(estado='pendiente').count()
    
    # Cantidad total procesada
    total_cantidad_procesada = preparaciones.filter(
        estado='completada'
    ).aggregate(total=Sum('cantidad_procesada'))['total'] or 0
    
    # Resumen por tipo de material
    resumen_por_material = preparaciones.values(
        'materia_prima__tipo'
    ).annotate(
        total_preparaciones=Count('id'),
        cantidad_total=Sum('cantidad_procesada')
    ).order_by('-cantidad_total')
    
    # Calcular porcentajes para el gráfico
    max_cantidad = resumen_por_material.first()['cantidad_total'] if resumen_por_material else 1
    for material in resumen_por_material:
        material['porcentaje'] = (material['cantidad_total'] / max_cantidad * 100) if max_cantidad else 0
    
    context = {
        'preparaciones': preparaciones,
        'total_preparaciones': total_preparaciones,
        'preparaciones_completadas': preparaciones_completadas,
        'preparaciones_en_proceso': preparaciones_en_proceso,
        'preparaciones_pendientes': preparaciones_pendientes,
        'total_cantidad_procesada': total_cantidad_procesada,
        'resumen_por_material': resumen_por_material,
    }
    
    return render(request, 'preparacion/reporte.html', context)
