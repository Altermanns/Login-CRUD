"""
Views package - organized by domain.
"""
from .auth_views import inicio, login, logout
from .dashboard_views import dashboard, admin_dashboard, operario_dashboard, preparador_dashboard
from .materia_views import listar_materias, crear_materia, editar_materia, eliminar_materia, editar_materia_no_id
from .user_views import listar_usuarios, crear_usuario, editar_usuario, eliminar_usuario
from .preparacion_views import (
    listar_preparaciones,
    crear_preparacion,
    detalle_preparacion,
    iniciar_preparacion,
    completar_preparacion,
    agregar_detalle_preparacion,
    editar_preparacion,
    eliminar_preparacion,
    reporte_preparaciones,
)
from .hilatura_views import (
    listar_hilaturas,
    crear_hilatura,
    detalle_hilatura,
    iniciar_hilatura,
    completar_hilatura,
    agregar_detalle_hilatura,
    editar_hilatura,
    eliminar_hilatura,
    reporte_hilaturas,
)

__all__ = [
    'inicio',
    'login',
    'logout',
    'dashboard',
    'admin_dashboard',
    'operario_dashboard',
    'preparador_dashboard',
    'listar_materias',
    'crear_materia',
    'editar_materia',
    'eliminar_materia',
    'editar_materia_no_id',
    'listar_usuarios',
    'crear_usuario',
    'editar_usuario',
    'eliminar_usuario',
    'listar_preparaciones',
    'crear_preparacion',
    'detalle_preparacion',
    'iniciar_preparacion',
    'completar_preparacion',
    'agregar_detalle_preparacion',
    'editar_preparacion',
    'eliminar_preparacion',
    'reporte_preparaciones',
    'listar_hilaturas',
    'crear_hilatura',
    'detalle_hilatura',
    'iniciar_hilatura',
    'completar_hilatura',
    'agregar_detalle_hilatura',
    'editar_hilatura',
    'eliminar_hilatura',
    'reporte_hilaturas',
]
