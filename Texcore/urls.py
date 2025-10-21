from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('inicio/', views.inicio, name='inicio_slash'),
    path('login/', views.login, name='login'),
    path('libros/', views.dashboard, name='index'),
    path('logout/', views.logout, name='logout'),
    # Materias URLs expected by templates
    path('materias/', views.listar_materias, name='index_materia'),
    path('materias/crear/', views.crear_materia, name='crear_materia'),
    path('materias/editar/', views.editar_materia_no_id, name='editar_materia_no_id'),
    path('materias/editar/<int:materia_id>/', views.editar_materia, name='editar_materia'),
    path('materias/eliminar/<int:materia_id>/', views.eliminar_materia, name='eliminar_materia'),
]