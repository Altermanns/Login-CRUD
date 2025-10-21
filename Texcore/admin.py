from django.contrib import admin
from .models import Materia


@admin.register(Materia)
class MateriaAdmin(admin.ModelAdmin):
	list_display = ('lote', 'tipo', 'cantidad', 'unidad_medida', 'fecha_ingreso')
	search_fields = ('lote', 'tipo')
	list_filter = ('unidad_medida',)
