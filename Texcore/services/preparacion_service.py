"""
Preparacion service - handles business logic for material preparation operations.
"""
from typing import Optional, Dict, Any
from decimal import Decimal
from django.db import transaction
from django.db.models import QuerySet, Q
from django.contrib.auth.models import User
from django.utils import timezone
from ..models import PreparacionMateria, Materia, DetallePreparacion


def get_all_preparaciones() -> QuerySet[PreparacionMateria]:
    """
    Get all preparaciones with optimized queries.
    
    Returns:
        QuerySet of PreparacionMateria objects
    """
    return PreparacionMateria.objects.select_related(
        'materia_prima',
        'usuario_preparador'
    ).order_by('-fecha_inicio')


def get_preparacion_by_id(preparacion_id: int) -> Optional[PreparacionMateria]:
    """
    Get a single preparacion by ID with related data.
    
    Args:
        preparacion_id: ID of the preparacion
        
    Returns:
        PreparacionMateria object or None
    """
    try:
        return PreparacionMateria.objects.select_related(
            'materia_prima',
            'usuario_preparador'
        ).prefetch_related('detalles').get(pk=preparacion_id)
    except PreparacionMateria.DoesNotExist:
        return None


def validar_stock_disponible(materia: Materia, cantidad_requerida: Decimal) -> tuple[bool, str]:
    """
    Validate if there's sufficient stock for preparation.
    
    Args:
        materia: Materia to validate
        cantidad_requerida: Amount required for preparation
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if materia.cantidad < cantidad_requerida:
        return False, (
            f'Stock insuficiente. Disponible: {materia.cantidad}kg, '
            f'Requerido: {cantidad_requerida}kg para {materia.tipo}.'
        )
    return True, ""


def verificar_stock_bajo(materia: Materia, cantidad_requerida: Decimal) -> tuple[bool, str]:
    """
    Check if processing will leave low stock.
    
    Args:
        materia: Materia to check
        cantidad_requerida: Amount to be processed
        
    Returns:
        Tuple of (is_low, warning_message)
    """
    stock_restante = materia.cantidad - cantidad_requerida
    if stock_restante < (materia.cantidad * Decimal('0.2')):  # Less than 20%
        return True, (
            f'¡Advertencia! Después de procesar quedarán solo {stock_restante}kg '
            f'de {materia.tipo} (menos del 20% del stock original).'
        )
    return False, ""


@transaction.atomic
def crear_preparacion(
    materia_prima: Materia,
    tipo_proceso: str,
    cantidad_procesada: Decimal,
    usuario_preparador: User,
    porcentaje_mezcla: Optional[Decimal] = None,
    observaciones: str = "",
    calidad_resultado: Optional[str] = None
) -> PreparacionMateria:
    """
    Create a new preparation with stock validation.
    Uses atomic transaction to ensure data consistency.
    
    Args:
        materia_prima: Materia to process
        tipo_proceso: Type of process
        cantidad_procesada: Amount to process
        usuario_preparador: User creating the preparation
        porcentaje_mezcla: Optional percentage in mix
        observaciones: Optional observations
        calidad_resultado: Optional quality result
        
    Returns:
        Created PreparacionMateria object
        
    Raises:
        ValueError: If stock is insufficient
    """
    # Validate stock
    is_valid, error_msg = validar_stock_disponible(materia_prima, cantidad_procesada)
    if not is_valid:
        raise ValueError(error_msg)
    
    preparacion = PreparacionMateria.objects.create(
        materia_prima=materia_prima,
        tipo_proceso=tipo_proceso,
        cantidad_procesada=cantidad_procesada,
        usuario_preparador=usuario_preparador,
        porcentaje_mezcla=porcentaje_mezcla,
        observaciones=observaciones,
        calidad_resultado=calidad_resultado,
        estado='pendiente'
    )
    
    return preparacion


@transaction.atomic
def iniciar_preparacion_proceso(preparacion: PreparacionMateria, usuario: User) -> tuple[bool, str]:
    """
    Start a pending preparation process.
    
    Args:
        preparacion: PreparacionMateria to start
        usuario: User starting the process
        
    Returns:
        Tuple of (success, message)
    """
    # Validate user permission
    if preparacion.usuario_preparador != usuario:
        return False, 'Solo puedes iniciar tus propias preparaciones.'
    
    # Validate state
    if preparacion.estado != 'pendiente':
        return False, 'Solo se pueden iniciar preparaciones pendientes.'
    
    preparacion.estado = 'en_proceso'
    preparacion.save()
    
    return True, 'Preparación iniciada exitosamente.'


@transaction.atomic
def completar_preparacion_proceso(preparacion: PreparacionMateria, usuario: User) -> tuple[bool, str]:
    """
    Complete a preparation process and update stock.
    Uses atomic transaction to ensure stock consistency.
    
    Args:
        preparacion: PreparacionMateria to complete
        usuario: User completing the process
        
    Returns:
        Tuple of (success, message)
    """
    # Validate user permission
    if preparacion.usuario_preparador != usuario:
        return False, 'Solo puedes completar tus propias preparaciones.'
    
    # Validate state
    if preparacion.estado != 'en_proceso':
        return False, 'Solo se pueden completar preparaciones en proceso.'
    
    # Get materia and validate stock
    materia = preparacion.materia_prima
    cantidad_procesada = preparacion.cantidad_procesada
    
    if materia.cantidad < cantidad_procesada:
        return False, (
            f'No hay suficiente stock. Disponible: {materia.cantidad}kg, '
            f'Requerido: {cantidad_procesada}kg'
        )
    
    # Update stock
    materia.cantidad -= cantidad_procesada
    materia.save()
    
    # Complete preparation
    preparacion.estado = 'completada'
    preparacion.fecha_completado = timezone.now()
    preparacion.save()
    
    success_msg = (
        f'Preparación completada exitosamente. Se procesaron {cantidad_procesada}kg de {materia.tipo}. '
        f'Stock restante: {materia.cantidad}kg'
    )
    
    return True, success_msg


def agregar_detalle_preparacion(
    preparacion: PreparacionMateria,
    temperatura: Optional[Decimal] = None,
    humedad: Optional[Decimal] = None,
    tiempo_proceso: Optional[int] = None,
    equipo_utilizado: str = "",
    rendimiento: Optional[Decimal] = None,
    merma: Optional[Decimal] = None,
    notas_tecnicas: str = ""
) -> DetallePreparacion:
    """
    Add technical details to a preparation.
    
    Args:
        preparacion: PreparacionMateria to add details to
        temperatura: Optional temperature
        humedad: Optional humidity
        tiempo_proceso: Optional process time in minutes
        equipo_utilizado: Equipment used
        rendimiento: Optional yield percentage
        merma: Optional waste percentage
        notas_tecnicas: Technical notes
        
    Returns:
        Created DetallePreparacion object
    """
    detalle = DetallePreparacion.objects.create(
        preparacion=preparacion,
        temperatura=temperatura,
        humedad=humedad,
        tiempo_proceso=tiempo_proceso,
        equipo_utilizado=equipo_utilizado,
        rendimiento=rendimiento,
        merma=merma,
        notas_tecnicas=notas_tecnicas
    )
    
    return detalle


def filtrar_preparaciones(
    estado: Optional[str] = None,
    tipo_proceso: Optional[str] = None,
    fecha_desde: Optional[str] = None,
    fecha_hasta: Optional[str] = None
) -> QuerySet[PreparacionMateria]:
    """
    Filter preparations by various criteria.
    
    Args:
        estado: Optional state filter
        tipo_proceso: Optional process type filter
        fecha_desde: Optional start date
        fecha_hasta: Optional end date
        
    Returns:
        Filtered QuerySet of PreparacionMateria
    """
    preparaciones = get_all_preparaciones()
    
    if estado:
        preparaciones = preparaciones.filter(estado=estado)
    
    if tipo_proceso:
        preparaciones = preparaciones.filter(tipo_proceso=tipo_proceso)
    
    if fecha_desde:
        preparaciones = preparaciones.filter(fecha_inicio__date__gte=fecha_desde)
    
    if fecha_hasta:
        preparaciones = preparaciones.filter(fecha_inicio__date__lte=fecha_hasta)
    
    return preparaciones


def get_preparaciones_usuario(usuario: User) -> QuerySet[PreparacionMateria]:
    """
    Get all preparations for a specific user.
    
    Args:
        usuario: User to get preparations for
        
    Returns:
        QuerySet of PreparacionMateria
    """
    return PreparacionMateria.objects.filter(
        usuario_preparador=usuario
    ).select_related('materia_prima').order_by('-fecha_inicio')
