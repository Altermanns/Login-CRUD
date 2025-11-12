from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Materia, Profile


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
