"""
Materia service - handles business logic for Materia Prima operations.
"""
from typing import Optional
from django.db.models import QuerySet
from django.contrib.auth.models import User
from ..models import Materia


def get_all_materias() -> QuerySet[Materia]:
    """
    Return queryset of all Materias ordered by newest first.
    Optimized with select_related for usuario_registro.
    
    Returns:
        QuerySet of Materia objects
    """
    return Materia.objects.select_related('usuario_registro').order_by('-id')


def get_materia_by_id(materia_id: int) -> Optional[Materia]:
    """
    Get a single Materia by ID.
    
    Args:
        materia_id: ID of the materia to retrieve
        
    Returns:
        Materia object or None if not found
    """
    try:
        return Materia.objects.select_related('usuario_registro').get(pk=materia_id)
    except Materia.DoesNotExist:
        return None


def crear_materia(form_data: dict, usuario: User) -> Materia:
    """
    Create a new Materia with the given data.
    
    Args:
        form_data: Dictionary with materia data
        usuario: User creating the materia
        
    Returns:
        Created Materia object
    """
    materia = Materia(**form_data)
    materia.usuario_registro = usuario
    materia.save()
    return materia


def actualizar_materia(materia: Materia, form_data: dict) -> Materia:
    """
    Update an existing Materia with new data.
    
    Args:
        materia: Materia object to update
        form_data: Dictionary with updated data
        
    Returns:
        Updated Materia object
    """
    for field, value in form_data.items():
        setattr(materia, field, value)
    materia.save()
    return materia


def eliminar_materia(materia: Materia) -> None:
    """
    Delete a Materia.
    
    Args:
        materia: Materia object to delete
    """
    materia.delete()


def get_materias_disponibles_para_preparacion() -> QuerySet[Materia]:
    """
    Get Materias available for preparation (with positive stock).
    
    Returns:
        QuerySet of available Materias
    """
    from django.db.models import Q
    
    return Materia.objects.filter(
        cantidad__gt=0
    ).filter(
        Q(preparacionmateria__isnull=True) |
        Q(preparacionmateria__estado__in=['completada', 'rechazada'])
    ).distinct().order_by('tipo', '-cantidad')


def validar_stock_suficiente(materia: Materia, cantidad_requerida: float) -> tuple[bool, str]:
    """
    Validate if there's sufficient stock for an operation.
    
    Args:
        materia: Materia to check
        cantidad_requerida: Amount required
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if materia.cantidad < cantidad_requerida:
        return False, (
            f'Stock insuficiente. Disponible: {materia.cantidad}{materia.unidad_medida}, '
            f'Requerido: {cantidad_requerida}{materia.unidad_medida}'
        )
    return True, ""


def calcular_stock_restante(materia: Materia, cantidad_procesada: float) -> dict:
    """
    Calculate remaining stock and warnings.
    
    Args:
        materia: Materia to check
        cantidad_procesada: Amount to be processed
        
    Returns:
        Dictionary with stock info and warnings
    """
    stock_restante = materia.cantidad - cantidad_procesada
    stock_bajo = stock_restante < (materia.cantidad * 0.2)  # Less than 20%
    
    return {
        'stock_restante': stock_restante,
        'stock_bajo': stock_bajo,
        'porcentaje_restante': (stock_restante / materia.cantidad * 100) if materia.cantidad > 0 else 0,
    }
