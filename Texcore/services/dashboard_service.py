"""
Dashboard service - handles business logic for dashboard statistics.
"""
from datetime import date
from typing import Dict, Any
from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncMonth
from django.contrib.auth.models import User
from ..models import Materia, PreparacionMateria


def get_admin_dashboard_stats() -> Dict[str, Any]:
    """
    Get comprehensive statistics for admin dashboard.
    
    Returns:
        Dictionary with all dashboard statistics
    """
    # Materia Prima Statistics
    total_materias = Materia.objects.count()
    total_cantidad = Materia.objects.aggregate(total=Sum('cantidad'))['total'] or 0
    
    # Materials by type
    materias_por_tipo = Materia.objects.values('tipo').annotate(
        total_cantidad=Sum('cantidad'),
        total_lotes=Count('id')
    ).order_by('-total_cantidad')[:5]
    
    # Monthly entries (last 6 months)
    materias_por_mes = list(
        Materia.objects.filter(
            fecha_ingreso__isnull=False
        ).annotate(
            month=TruncMonth('fecha_ingreso')
        ).values('month').annotate(
            total=Count('id'),
            cantidad_total=Sum('cantidad')
        ).order_by('-month')[:6]
    )
    
    # Recent entries
    entradas_recientes = Materia.objects.select_related(
        'usuario_registro'
    ).order_by('-id')[:10]
    
    # Preparation Statistics
    total_preparaciones = PreparacionMateria.objects.count()
    preparaciones_pendientes = PreparacionMateria.objects.filter(estado='pendiente').count()
    preparaciones_en_proceso = PreparacionMateria.objects.filter(estado='en_proceso').count()
    preparaciones_completadas = PreparacionMateria.objects.filter(estado='completada').count()
    
    # Processed materials by type
    materiales_procesados = PreparacionMateria.objects.filter(
        estado='completada'
    ).values('materia_prima__tipo').annotate(
        cantidad_procesada=Sum('cantidad_procesada'),
        total_preparaciones=Count('id')
    ).order_by('-cantidad_procesada')[:5]
    
    # Recent preparations
    preparaciones_recientes = PreparacionMateria.objects.select_related(
        'materia_prima', 'usuario_preparador'
    ).order_by('-fecha_inicio')[:8]
    
    # Most active preparadores
    preparadores_activos = PreparacionMateria.objects.values(
        'usuario_preparador__first_name',
        'usuario_preparador__last_name'
    ).annotate(
        total_preparaciones=Count('id'),
        completadas=Count('id', filter=Q(estado='completada')),
        cantidad_total=Sum('cantidad_procesada', filter=Q(estado='completada'))
    ).order_by('-total_preparaciones')[:5]
    
    return {
        # Materia Prima stats
        'total_materias': total_materias,
        'total_cantidad': total_cantidad,
        'materias_por_tipo': materias_por_tipo,
        'materias_por_mes': materias_por_mes,
        'entradas_recientes': entradas_recientes,
        
        # Preparation stats
        'total_preparaciones': total_preparaciones,
        'preparaciones_pendientes': preparaciones_pendientes,
        'preparaciones_en_proceso': preparaciones_en_proceso,
        'preparaciones_completadas': preparaciones_completadas,
        'materiales_procesados': materiales_procesados,
        'preparaciones_recientes': preparaciones_recientes,
        'preparadores_activos': preparadores_activos,
    }


def get_operario_dashboard_stats(usuario: User) -> Dict[str, Any]:
    """
    Get statistics for operario dashboard.
    
    Args:
        usuario: Operario user
        
    Returns:
        Dictionary with operario-specific statistics
    """
    # Get operario's recent entries
    mis_entradas = Materia.objects.filter(
        usuario_registro=usuario
    ).order_by('-id')[:5]
    
    # Get today's entries
    entradas_hoy = Materia.objects.filter(
        fecha_ingreso=date.today()
    ).count()
    
    return {
        'mis_entradas': mis_entradas,
        'entradas_hoy': entradas_hoy,
    }


def get_preparador_dashboard_stats(usuario: User) -> Dict[str, Any]:
    """
    Get statistics for preparador dashboard.
    
    Args:
        usuario: Preparador user
        
    Returns:
        Dictionary with preparador-specific statistics
    """
    # User's preparations
    preparaciones_usuario = PreparacionMateria.objects.filter(
        usuario_preparador=usuario
    )
    
    total_preparaciones = preparaciones_usuario.count()
    en_proceso = preparaciones_usuario.filter(estado='en_proceso').count()
    completadas_hoy = preparaciones_usuario.filter(
        fecha_completado__date=date.today()
    ).count()
    pendientes = preparaciones_usuario.filter(estado='pendiente').count()
    
    # Recent preparations
    preparaciones_recientes = preparaciones_usuario.select_related(
        'materia_prima'
    ).order_by('-fecha_inicio')[:5]
    
    # Available materials for processing
    materias_disponibles = Materia.objects.filter(
        preparacionmateria__isnull=True,
        cantidad__gt=0
    ).count()
    
    return {
        'total_preparaciones': total_preparaciones,
        'en_proceso': en_proceso,
        'completadas_hoy': completadas_hoy,
        'pendientes': pendientes,
        'preparaciones_recientes': preparaciones_recientes,
        'materias_disponibles': materias_disponibles,
    }


def get_reporte_preparaciones_stats(
    fecha_inicio: str = None,
    fecha_fin: str = None,
    estado_filtro: str = None
) -> Dict[str, Any]:
    """
    Get statistics for preparation reports.
    
    Args:
        fecha_inicio: Optional start date filter
        fecha_fin: Optional end date filter
        estado_filtro: Optional state filter
        
    Returns:
        Dictionary with report statistics
    """
    # Base queryset
    preparaciones = PreparacionMateria.objects.select_related(
        'materia_prima', 'usuario_preparador'
    ).order_by('-fecha_inicio')
    
    # Apply filters
    if fecha_inicio:
        preparaciones = preparaciones.filter(fecha_inicio__date__gte=fecha_inicio)
    
    if fecha_fin:
        preparaciones = preparaciones.filter(fecha_inicio__date__lte=fecha_fin)
    
    if estado_filtro:
        preparaciones = preparaciones.filter(estado=estado_filtro)
    
    # General statistics
    total_preparaciones = preparaciones.count()
    preparaciones_completadas = preparaciones.filter(estado='completada').count()
    preparaciones_en_proceso = preparaciones.filter(estado='en_proceso').count()
    preparaciones_pendientes = preparaciones.filter(estado='pendiente').count()
    
    # Total processed quantity
    total_cantidad_procesada = preparaciones.filter(
        estado='completada'
    ).aggregate(total=Sum('cantidad_procesada'))['total'] or 0
    
    # Summary by material type
    resumen_por_material = list(
        preparaciones.values(
            'materia_prima__tipo'
        ).annotate(
            total_preparaciones=Count('id'),
            cantidad_total=Sum('cantidad_procesada')
        ).order_by('-cantidad_total')
    )
    
    # Calculate percentages for charts
    max_cantidad = resumen_por_material[0]['cantidad_total'] if resumen_por_material else 1
    for material in resumen_por_material:
        material['porcentaje'] = (
            (material['cantidad_total'] / max_cantidad * 100) if max_cantidad else 0
        )
    
    return {
        'preparaciones': preparaciones,
        'total_preparaciones': total_preparaciones,
        'preparaciones_completadas': preparaciones_completadas,
        'preparaciones_en_proceso': preparaciones_en_proceso,
        'preparaciones_pendientes': preparaciones_pendientes,
        'total_cantidad_procesada': total_cantidad_procesada,
        'resumen_por_material': resumen_por_material,
    }
