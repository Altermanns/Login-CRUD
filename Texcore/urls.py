from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('inicio/', views.inicio, name='inicio_slash'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('libros/', views.dashboard, name='index'),  # Legacy redirect
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/operario/', views.operario_dashboard, name='operario_dashboard'),
    path('dashboard/preparador/', views.preparador_dashboard, name='preparador_dashboard'),
    path('materias/', views.listar_materias, name='index_materia'),
    path('materias/crear/', views.crear_materia, name='crear_materia'),
    path('materias/editar/', views.editar_materia_no_id, name='editar_materia_no_id'),
    path('materias/editar/<int:materia_id>/', views.editar_materia, name='editar_materia'),
    path('materias/eliminar/<int:materia_id>/', views.eliminar_materia, name='eliminar_materia'),
    
    # Gestión de usuarios (solo admin)
    path('usuarios/', views.listar_usuarios, name='listar_usuarios'),
    path('usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    path('usuarios/editar/<int:user_id>/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/eliminar/<int:user_id>/', views.eliminar_usuario, name='eliminar_usuario'),
    
    # Preparación de materias primas (preparador + admin)
    path('preparaciones/', views.listar_preparaciones, name='listar_preparaciones'),
    path('preparaciones/crear/', views.crear_preparacion, name='crear_preparacion'),
    path('preparaciones/<int:preparacion_id>/', views.detalle_preparacion, name='detalle_preparacion'),
    path('preparaciones/<int:preparacion_id>/iniciar/', views.iniciar_preparacion, name='iniciar_preparacion'),
    path('preparaciones/<int:preparacion_id>/completar/', views.completar_preparacion, name='completar_preparacion'),
    path('preparaciones/<int:preparacion_id>/editar/', views.editar_preparacion, name='editar_preparacion'),
    path('preparaciones/<int:preparacion_id>/eliminar/', views.eliminar_preparacion, name='eliminar_preparacion'),
    path('preparaciones/<int:preparacion_id>/detalle/', views.agregar_detalle_preparacion, name='agregar_detalle_preparacion'),
    path('preparaciones/reporte/', views.reporte_preparaciones, name='reporte_preparaciones'),
]