from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Materia, Profile, PreparacionMateria, DetallePreparacion, ProcesoHilatura, DetalleHilatura


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Perfil'


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)


@admin.register(Materia)
class MateriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo', 'cantidad', 'unidad_medida', 'lote', 'fecha_ingreso', 'usuario_registro')
    list_filter = ('tipo', 'fecha_ingreso', 'usuario_registro')
    search_fields = ('tipo', 'lote', 'usuario_registro__username')
    ordering = ('-id',)
    readonly_fields = ('usuario_registro',)

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.usuario_registro = request.user
        super().save_model(request, obj, form, change)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(PreparacionMateria)
class PreparacionMateriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'materia_prima', 'tipo_proceso', 'estado', 'cantidad_procesada', 
                   'usuario_preparador', 'fecha_inicio')
    list_filter = ('estado', 'tipo_proceso', 'calidad_resultado', 'fecha_inicio')
    search_fields = ('materia_prima__tipo', 'materia_prima__lote', 'usuario_preparador__username')
    ordering = ('-fecha_inicio',)
    readonly_fields = ('fecha_inicio', 'fecha_completado')


@admin.register(DetallePreparacion)
class DetallePreparacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'preparacion', 'equipo_utilizado', 'temperatura', 'humedad', 
                   'rendimiento', 'fecha_registro')
    list_filter = ('fecha_registro',)
    search_fields = ('preparacion__id', 'equipo_utilizado')
    ordering = ('-fecha_registro',)


@admin.register(ProcesoHilatura)
class ProcesoHilaturaAdmin(admin.ModelAdmin):
    list_display = ('id', 'etapa', 'estado', 'cantidad_fibra_entrada', 'cantidad_hilo_salida',
                   'rendimiento_proceso', 'usuario_operador', 'fecha_inicio')
    list_filter = ('estado', 'etapa', 'calidad_resultado', 'fecha_inicio')
    search_fields = ('titulo_hilo', 'usuario_operador__username', 'preparacion_origen__id')
    ordering = ('-fecha_inicio',)
    readonly_fields = ('fecha_inicio', 'fecha_completado', 'rendimiento_proceso', 'merma')
    
    fieldsets = (
        ('Información General', {
            'fields': ('preparacion_origen', 'etapa', 'estado', 'usuario_operador')
        }),
        ('Cantidades', {
            'fields': ('cantidad_fibra_entrada', 'cantidad_hilo_salida', 'rendimiento_proceso', 'merma')
        }),
        ('Características del Hilo', {
            'fields': ('titulo_hilo', 'torsion', 'resistencia')
        }),
        ('Calidad', {
            'fields': ('calidad_resultado', 'observaciones')
        }),
        ('Fechas', {
            'fields': ('fecha_inicio', 'fecha_completado')
        }),
    )


@admin.register(DetalleHilatura)
class DetalleHilaturaAdmin(admin.ModelAdmin):
    list_display = ('id', 'hilatura', 'maquina_hiladora', 'velocidad_maquina', 
                   'temperatura', 'humedad', 'tiempo_proceso', 'fecha_registro')
    list_filter = ('fecha_registro', 'limpieza_fibras', 'grado_torsion')
    search_fields = ('hilatura__id', 'maquina_hiladora')
    ordering = ('-fecha_registro',)
    
    fieldsets = (
        ('Proceso de Hilatura', {
            'fields': ('hilatura',)
        }),
        ('Parámetros Generales', {
            'fields': ('velocidad_maquina', 'temperatura', 'humedad', 'maquina_hiladora', 
                      'numero_husos', 'tiempo_proceso')
        }),
        ('Cardado', {
            'fields': ('velocidad_cardado', 'limpieza_fibras'),
            'classes': ('collapse',)
        }),
        ('Peinado', {
            'fields': ('longitud_fibra_eliminada', 'porcentaje_impurezas_removidas'),
            'classes': ('collapse',)
        }),
        ('Hilado', {
            'fields': ('grado_torsion', 'uniformidad'),
            'classes': ('collapse',)
        }),
        ('Control de Calidad', {
            'fields': ('defectos_encontrados', 'notas_tecnicas')
        }),
    )
