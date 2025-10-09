from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('inicio/', views.inicio, name='inicio_slash'),
    path('login/', views.login, name='login'),
    path('libros/', views.index, name='index'),
    # Materias URLs expected by templates
    path('materias/', views.index_materia, name='index_materia'),
    path('materias/crear/', views.crear_materia, name='crear_materia'),
    path('materias/editar/<int:materia_id>/', views.editar_materia, name='editar_materia'),
    path('materias/eliminar/<int:materia_id>/', views.eliminar_materia, name='eliminar_materia'),
]