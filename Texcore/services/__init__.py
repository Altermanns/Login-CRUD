"""
Services package for business logic.
"""
from .auth_service import authenticate_user
from .materia_service import (
    get_all_materias,
    crear_materia,
    actualizar_materia,
    eliminar_materia,
    get_materia_by_id,
)
from .preparacion_service import (
    crear_preparacion,
    iniciar_preparacion_proceso,
    completar_preparacion_proceso,
    validar_stock_disponible,
)
from .dashboard_service import (
    get_admin_dashboard_stats,
    get_operario_dashboard_stats,
    get_preparador_dashboard_stats,
)

__all__ = [
    'authenticate_user',
    'get_all_materias',
    'crear_materia',
    'actualizar_materia',
    'eliminar_materia',
    'get_materia_by_id',
    'crear_preparacion',
    'iniciar_preparacion_proceso',
    'completar_preparacion_proceso',
    'validar_stock_disponible',
    'get_admin_dashboard_stats',
    'get_operario_dashboard_stats',
    'get_preparador_dashboard_stats',
]
