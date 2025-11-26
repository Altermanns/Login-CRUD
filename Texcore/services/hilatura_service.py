"""
Hilatura service - handles business logic for spinning operations.
"""
from typing import Optional, Dict, Any, List
from decimal import Decimal
from django.db import transaction
from django.db.models import QuerySet, Q, Sum, Avg
from django.contrib.auth.models import User
from django.utils import timezone
from ..models import ProcesoHilatura, DetalleHilatura, PreparacionMateria


def get_all_hilaturas() -> QuerySet[ProcesoHilatura]:
    """
    Get all procesos de hilatura with optimized queries.
    
    Returns:
        QuerySet of ProcesoHilatura objects
    """
    return ProcesoHilatura.objects.select_related(
        'preparacion_origen',
        'usuario_operador'
    ).order_by('-fecha_inicio')


def get_hilatura_by_id(hilatura_id: int) -> Optional[ProcesoHilatura]:
    """
    Get a single proceso de hilatura by ID with related data.
    
    Args:
        hilatura_id: ID of the hilatura
        
    Returns:
        ProcesoHilatura object or None
    """
    try:
        return ProcesoHilatura.objects.select_related(
            'preparacion_origen',
            'usuario_operador'
        ).prefetch_related('detalles').get(pk=hilatura_id)
    except ProcesoHilatura.DoesNotExist:
        return None


def validar_preparacion_disponible(preparacion: PreparacionMateria) -> tuple[bool, str]:
    """
    Validate if a preparacion is available for hilatura process.
    
    Args:
        preparacion: PreparacionMateria to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not preparacion:
        return False, "La preparación no existe"
    
    if preparacion.estado != 'completada':
        return False, "La preparación debe estar completada antes de iniciar el proceso de hilatura"
    
    if preparacion.cantidad_procesada <= 0:
        return False, "La preparación no tiene cantidad procesada disponible"
    
    return True, ""


@transaction.atomic
def crear_proceso_hilatura(
    etapa: str,
    preparacion_origen: Optional[PreparacionMateria],
    cantidad_fibra_entrada: Decimal,
    usuario_operador: User,
    titulo_hilo: str = "",
    observaciones: str = ""
) -> tuple[Optional[ProcesoHilatura], str]:
    """
    Create a new proceso de hilatura.
    
    Args:
        etapa: Etapa del proceso (cardado, peinado, hilado)
        preparacion_origen: Preparación de materia prima de origen
        cantidad_fibra_entrada: Cantidad de fibra de entrada
        usuario_operador: Usuario que realiza el proceso
        titulo_hilo: Título del hilo
        observaciones: Observaciones del proceso
        
    Returns:
        Tuple of (ProcesoHilatura, error_message)
    """
    try:
        # Validar preparación si se proporciona
        if preparacion_origen:
            is_valid, error_msg = validar_preparacion_disponible(preparacion_origen)
            if not is_valid:
                return None, error_msg
        
        # Create the hilatura process
        hilatura = ProcesoHilatura.objects.create(
            etapa=etapa,
            preparacion_origen=preparacion_origen,
            cantidad_fibra_entrada=cantidad_fibra_entrada,
            titulo_hilo=titulo_hilo,
            observaciones=observaciones,
            usuario_operador=usuario_operador,
            estado='pendiente'
        )
        
        return hilatura, "Proceso de hilatura creado exitosamente"
        
    except Exception as e:
        return None, f"Error al crear proceso de hilatura: {str(e)}"


@transaction.atomic
def iniciar_proceso_hilatura(hilatura_id: int) -> tuple[bool, str]:
    """
    Iniciar un proceso de hilatura.
    
    Args:
        hilatura_id: ID del proceso de hilatura
        
    Returns:
        Tuple of (success, message)
    """
    try:
        hilatura = get_hilatura_by_id(hilatura_id)
        if not hilatura:
            return False, "Proceso de hilatura no encontrado"
        
        if hilatura.estado != 'pendiente':
            return False, "Solo se pueden iniciar procesos pendientes"
        
        hilatura.estado = 'en_proceso'
        hilatura.save()
        
        return True, "Proceso de hilatura iniciado"
        
    except Exception as e:
        return False, f"Error al iniciar proceso: {str(e)}"


@transaction.atomic
def completar_proceso_hilatura(
    hilatura_id: int,
    cantidad_hilo_salida: Decimal,
    calidad_resultado: str,
    torsion: Optional[Decimal] = None,
    resistencia: Optional[Decimal] = None
) -> tuple[bool, str]:
    """
    Completar un proceso de hilatura.
    
    Args:
        hilatura_id: ID del proceso de hilatura
        cantidad_hilo_salida: Cantidad de hilo producido
        calidad_resultado: Calidad del resultado
        torsion: Torsión del hilo (opcional)
        resistencia: Resistencia del hilo (opcional)
        
    Returns:
        Tuple of (success, message)
    """
    try:
        hilatura = get_hilatura_by_id(hilatura_id)
        if not hilatura:
            return False, "Proceso de hilatura no encontrado"
        
        if hilatura.estado == 'completada':
            return False, "El proceso ya está completado"
        
        hilatura.cantidad_hilo_salida = cantidad_hilo_salida
        hilatura.calidad_resultado = calidad_resultado
        if torsion is not None:
            hilatura.torsion = torsion
        if resistencia is not None:
            hilatura.resistencia = resistencia
        hilatura.estado = 'completada'
        hilatura.fecha_completado = timezone.now()
        hilatura.save()
        
        return True, "Proceso de hilatura completado exitosamente"
        
    except Exception as e:
        return False, f"Error al completar proceso: {str(e)}"


@transaction.atomic
def agregar_detalle_hilatura(
    hilatura_id: int,
    detalle_data: Dict[str, Any]
) -> tuple[Optional[DetalleHilatura], str]:
    """
    Agregar detalle a un proceso de hilatura.
    
    Args:
        hilatura_id: ID del proceso de hilatura
        detalle_data: Datos del detalle
        
    Returns:
        Tuple of (DetalleHilatura, error_message)
    """
    try:
        hilatura = get_hilatura_by_id(hilatura_id)
        if not hilatura:
            return None, "Proceso de hilatura no encontrado"
        
        detalle = DetalleHilatura.objects.create(
            hilatura=hilatura,
            **detalle_data
        )
        
        return detalle, "Detalle agregado exitosamente"
        
    except Exception as e:
        return None, f"Error al agregar detalle: {str(e)}"


def filtrar_hilaturas(
    estado: Optional[str] = None,
    etapa: Optional[str] = None,
    fecha_desde: Optional[str] = None,
    fecha_hasta: Optional[str] = None
) -> QuerySet[ProcesoHilatura]:
    """
    Filtrar procesos de hilatura.
    
    Args:
        estado: Estado del proceso
        etapa: Etapa del proceso
        fecha_desde: Fecha inicial
        fecha_hasta: Fecha final
        
    Returns:
        QuerySet filtrado
    """
    queryset = get_all_hilaturas()
    
    if estado:
        queryset = queryset.filter(estado=estado)
    
    if etapa:
        queryset = queryset.filter(etapa=etapa)
    
    if fecha_desde:
        queryset = queryset.filter(fecha_inicio__gte=fecha_desde)
    
    if fecha_hasta:
        queryset = queryset.filter(fecha_inicio__lte=fecha_hasta)
    
    return queryset


def obtener_estadisticas_hilatura() -> Dict[str, Any]:
    """
    Obtener estadísticas generales de hilatura.
    
    Returns:
        Diccionario con estadísticas
    """
    total_procesos = ProcesoHilatura.objects.count()
    procesos_completados = ProcesoHilatura.objects.filter(estado='completada').count()
    procesos_en_proceso = ProcesoHilatura.objects.filter(estado='en_proceso').count()
    procesos_pendientes = ProcesoHilatura.objects.filter(estado='pendiente').count()
    
    # Estadísticas por etapa
    cardados = ProcesoHilatura.objects.filter(etapa='cardado').count()
    peinados = ProcesoHilatura.objects.filter(etapa='peinado').count()
    hilados = ProcesoHilatura.objects.filter(etapa='hilado').count()
    
    # Producción total
    produccion_total = ProcesoHilatura.objects.filter(
        estado='completada'
    ).aggregate(
        total=Sum('cantidad_hilo_salida')
    )['total'] or 0
    
    # Rendimiento promedio
    rendimiento_avg = ProcesoHilatura.objects.filter(
        estado='completada',
        cantidad_fibra_entrada__gt=0
    ).aggregate(
        avg_rendimiento=Avg('cantidad_hilo_salida') / Avg('cantidad_fibra_entrada') * 100
    )
    
    return {
        'total_procesos': total_procesos,
        'procesos_completados': procesos_completados,
        'procesos_en_proceso': procesos_en_proceso,
        'procesos_pendientes': procesos_pendientes,
        'cardados': cardados,
        'peinados': peinados,
        'hilados': hilados,
        'produccion_total': produccion_total,
        'rendimiento_promedio': rendimiento_avg.get('avg_rendimiento', 0) if rendimiento_avg else 0,
    }


def get_preparaciones_disponibles() -> QuerySet[PreparacionMateria]:
    """
    Get preparaciones that are completed and available for hilatura.
    
    Returns:
        QuerySet of PreparacionMateria objects
    """
    return PreparacionMateria.objects.filter(
        estado='completada'
    ).select_related('materia_prima', 'usuario_preparador').order_by('-fecha_completado')


@transaction.atomic
def actualizar_proceso_hilatura(
    hilatura_id: int,
    datos_actualizados: Dict[str, Any]
) -> tuple[bool, str]:
    """
    Actualizar un proceso de hilatura.
    
    Args:
        hilatura_id: ID del proceso
        datos_actualizados: Datos a actualizar
        
    Returns:
        Tuple of (success, message)
    """
    try:
        hilatura = get_hilatura_by_id(hilatura_id)
        if not hilatura:
            return False, "Proceso de hilatura no encontrado"
        
        # No permitir editar procesos completados
        if hilatura.estado == 'completada' and 'estado' not in datos_actualizados:
            return False, "No se pueden editar procesos completados"
        
        for key, value in datos_actualizados.items():
            if hasattr(hilatura, key):
                setattr(hilatura, key, value)
        
        hilatura.save()
        return True, "Proceso actualizado exitosamente"
        
    except Exception as e:
        return False, f"Error al actualizar proceso: {str(e)}"


@transaction.atomic
def eliminar_proceso_hilatura(hilatura_id: int) -> tuple[bool, str]:
    """
    Eliminar un proceso de hilatura.
    
    Args:
        hilatura_id: ID del proceso
        
    Returns:
        Tuple of (success, message)
    """
    try:
        hilatura = get_hilatura_by_id(hilatura_id)
        if not hilatura:
            return False, "Proceso de hilatura no encontrado"
        
        # Solo permitir eliminar procesos pendientes o rechazados
        if hilatura.estado not in ['pendiente', 'rechazada']:
            return False, "Solo se pueden eliminar procesos pendientes o rechazados"
        
        hilatura.delete()
        return True, "Proceso eliminado exitosamente"
        
    except Exception as e:
        return False, f"Error al eliminar proceso: {str(e)}"
