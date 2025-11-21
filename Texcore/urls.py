from django.urls import path
from .views import (
    auth_views,
    dashboard_views,
    materia_views,
    user_views,
    preparacion_views,
)

urlpatterns = [
    path('', auth_views.inicio, name='inicio'),
    path('inicio/', auth_views.inicio, name='inicio_slash'),
    path('login/', auth_views.login, name='login'),
    path('logout/', auth_views.logout, name='logout'),
    path('libros/', dashboard_views.dashboard, name='index'),  # Legacy redirect
    path('dashboard/admin/', dashboard_views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/operario/', dashboard_views.operario_dashboard, name='operario_dashboard'),
    path('dashboard/preparador/', dashboard_views.preparador_dashboard, name='preparador_dashboard'),
    path('materias/', materia_views.listar_materias, name='index_materia'),
    path('materias/crear/', materia_views.crear_materia, name='crear_materia'),
    path('materias/editar/', materia_views.editar_materia_no_id, name='editar_materia_no_id'),
    path('materias/editar/<int:materia_id>/', materia_views.editar_materia, name='editar_materia'),
    path('materias/eliminar/<int:materia_id>/', materia_views.eliminar_materia, name='eliminar_materia'),
    
    # Gestión de usuarios (solo admin)
    path('usuarios/', user_views.listar_usuarios, name='listar_usuarios'),
    path('usuarios/crear/', user_views.crear_usuario, name='crear_usuario'),
    path('usuarios/editar/<int:user_id>/', user_views.editar_usuario, name='editar_usuario'),
    path('usuarios/eliminar/<int:user_id>/', user_views.eliminar_usuario, name='eliminar_usuario'),
    
    # Preparación de materias primas (preparador + admin)
    path('preparaciones/', preparacion_views.listar_preparaciones, name='listar_preparaciones'),
    path('preparaciones/crear/', preparacion_views.crear_preparacion, name='crear_preparacion'),
    path('preparaciones/<int:preparacion_id>/', preparacion_views.detalle_preparacion, name='detalle_preparacion'),
    path('preparaciones/<int:preparacion_id>/iniciar/', preparacion_views.iniciar_preparacion, name='iniciar_preparacion'),
    path('preparaciones/<int:preparacion_id>/completar/', preparacion_views.completar_preparacion, name='completar_preparacion'),
    path('preparaciones/<int:preparacion_id>/editar/', preparacion_views.editar_preparacion, name='editar_preparacion'),
    path('preparaciones/<int:preparacion_id>/eliminar/', preparacion_views.eliminar_preparacion, name='eliminar_preparacion'),
    path('preparaciones/<int:preparacion_id>/detalle/', preparacion_views.agregar_detalle_preparacion, name='agregar_detalle_preparacion'),
    path('preparaciones/reporte/', preparacion_views.reporte_preparaciones, name='reporte_preparaciones'),
]