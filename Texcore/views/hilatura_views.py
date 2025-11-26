"""
Hilatura views - spinning process management.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from decimal import Decimal
from ..models import ProcesoHilatura, DetalleHilatura
from ..decorators import (
    admin_required,
    operario_required,
    admin_or_operario_required
)
from ..services import hilatura_service


@admin_or_operario_required
def listar_hilaturas(request):
    """Lista todos los procesos de hilatura con filtros."""
    hilaturas = hilatura_service.get_all_hilaturas()
    
    # Apply filters
    estado = request.GET.get('estado')
    etapa = request.GET.get('etapa')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    
    if estado or etapa or fecha_desde or fecha_hasta:
        hilaturas = hilatura_service.filtrar_hilaturas(
            estado=estado,
            etapa=etapa,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta
        )
    
    # Estadísticas
    estadisticas = hilatura_service.obtener_estadisticas_hilatura()
    
    context = {
        'hilaturas': hilaturas,
        'estadisticas': estadisticas,
        'filtro_estado': estado,
        'filtro_etapa': etapa,
        'filtro_fecha_desde': fecha_desde,
        'filtro_fecha_hasta': fecha_hasta,
    }
    return render(request, 'hilatura/lista.html', context)


@operario_required
def crear_hilatura(request):
    """Crear un nuevo proceso de hilatura."""
    if request.method == 'POST':
        try:
            etapa = request.POST.get('etapa')
            preparacion_id = request.POST.get('preparacion_origen')
            cantidad_fibra_entrada = Decimal(request.POST.get('cantidad_fibra_entrada', '0'))
            titulo_hilo = request.POST.get('titulo_hilo', '')
            observaciones = request.POST.get('observaciones', '')
            
            # Get preparacion if provided
            preparacion_origen = None
            if preparacion_id:
                from ..models import PreparacionMateria
                preparacion_origen = PreparacionMateria.objects.get(pk=preparacion_id)
            
            # Create using service
            hilatura, error_msg = hilatura_service.crear_proceso_hilatura(
                etapa=etapa,
                preparacion_origen=preparacion_origen,
                cantidad_fibra_entrada=cantidad_fibra_entrada,
                usuario_operador=request.user,
                titulo_hilo=titulo_hilo,
                observaciones=observaciones
            )
            
            if hilatura:
                messages.success(request, error_msg)
                return redirect('detalle_hilatura', hilatura_id=hilatura.id)
            else:
                messages.error(request, error_msg)
                
        except Exception as e:
            messages.error(request, f"Error al crear proceso: {str(e)}")
    
    # Get available preparaciones
    preparaciones = hilatura_service.get_preparaciones_disponibles()
    
    context = {
        'preparaciones': preparaciones,
    }
    return render(request, 'hilatura/crear.html', context)


@admin_or_operario_required
def detalle_hilatura(request, hilatura_id):
    """Ver detalle de un proceso de hilatura."""
    hilatura = get_object_or_404(ProcesoHilatura, pk=hilatura_id)
    detalles = hilatura.detalles.all()
    
    context = {
        'hilatura': hilatura,
        'detalles': detalles,
    }
    return render(request, 'hilatura/detalle.html', context)


@operario_required
def iniciar_hilatura(request, hilatura_id):
    """Iniciar un proceso de hilatura."""
    if request.method == 'POST':
        success, message = hilatura_service.iniciar_proceso_hilatura(hilatura_id)
        
        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)
    
    return redirect('detalle_hilatura', hilatura_id=hilatura_id)


@operario_required
def completar_hilatura(request, hilatura_id):
    """Completar un proceso de hilatura."""
    if request.method == 'POST':
        try:
            cantidad_hilo_salida = Decimal(request.POST.get('cantidad_hilo_salida', '0'))
            calidad_resultado = request.POST.get('calidad_resultado')
            torsion_str = request.POST.get('torsion')
            resistencia_str = request.POST.get('resistencia')
            
            torsion = Decimal(torsion_str) if torsion_str else None
            resistencia = Decimal(resistencia_str) if resistencia_str else None
            
            success, message = hilatura_service.completar_proceso_hilatura(
                hilatura_id=hilatura_id,
                cantidad_hilo_salida=cantidad_hilo_salida,
                calidad_resultado=calidad_resultado,
                torsion=torsion,
                resistencia=resistencia
            )
            
            if success:
                messages.success(request, message)
            else:
                messages.error(request, message)
                
        except Exception as e:
            messages.error(request, f"Error al completar proceso: {str(e)}")
    
    return redirect('detalle_hilatura', hilatura_id=hilatura_id)


@operario_required
def editar_hilatura(request, hilatura_id):
    """Editar un proceso de hilatura."""
    hilatura = get_object_or_404(ProcesoHilatura, pk=hilatura_id)
    
    if request.method == 'POST':
        try:
            datos_actualizados = {
                'etapa': request.POST.get('etapa'),
                'cantidad_fibra_entrada': Decimal(request.POST.get('cantidad_fibra_entrada', '0')),
                'titulo_hilo': request.POST.get('titulo_hilo', ''),
                'observaciones': request.POST.get('observaciones', ''),
            }
            
            # Update preparacion if changed
            preparacion_id = request.POST.get('preparacion_origen')
            if preparacion_id:
                from ..models import PreparacionMateria
                datos_actualizados['preparacion_origen'] = PreparacionMateria.objects.get(pk=preparacion_id)
            
            success, message = hilatura_service.actualizar_proceso_hilatura(
                hilatura_id=hilatura_id,
                datos_actualizados=datos_actualizados
            )
            
            if success:
                messages.success(request, message)
                return redirect('detalle_hilatura', hilatura_id=hilatura_id)
            else:
                messages.error(request, message)
                
        except Exception as e:
            messages.error(request, f"Error al editar proceso: {str(e)}")
    
    # Get available preparaciones
    preparaciones = hilatura_service.get_preparaciones_disponibles()
    
    context = {
        'hilatura': hilatura,
        'preparaciones': preparaciones,
    }
    return render(request, 'hilatura/editar.html', context)


@admin_required
def eliminar_hilatura(request, hilatura_id):
    """Eliminar un proceso de hilatura."""
    if request.method == 'POST':
        success, message = hilatura_service.eliminar_proceso_hilatura(hilatura_id)
        
        if success:
            messages.success(request, message)
            return redirect('listar_hilaturas')
        else:
            messages.error(request, message)
            return redirect('detalle_hilatura', hilatura_id=hilatura_id)
    
    return redirect('detalle_hilatura', hilatura_id=hilatura_id)


@operario_required
def agregar_detalle_hilatura(request, hilatura_id):
    """Agregar detalle a un proceso de hilatura."""
    hilatura = get_object_or_404(ProcesoHilatura, pk=hilatura_id)
    
    if request.method == 'POST':
        try:
            detalle_data = {
                'velocidad_maquina': _get_decimal_or_none(request.POST.get('velocidad_maquina')),
                'temperatura': _get_decimal_or_none(request.POST.get('temperatura')),
                'humedad': _get_decimal_or_none(request.POST.get('humedad')),
                'maquina_hiladora': request.POST.get('maquina_hiladora', ''),
                'numero_husos': _get_int_or_none(request.POST.get('numero_husos')),
                'velocidad_cardado': _get_decimal_or_none(request.POST.get('velocidad_cardado')),
                'limpieza_fibras': request.POST.get('limpieza_fibras'),
                'longitud_fibra_eliminada': _get_decimal_or_none(request.POST.get('longitud_fibra_eliminada')),
                'porcentaje_impurezas_removidas': _get_decimal_or_none(request.POST.get('porcentaje_impurezas_removidas')),
                'grado_torsion': request.POST.get('grado_torsion'),
                'uniformidad': _get_decimal_or_none(request.POST.get('uniformidad')),
                'tiempo_proceso': _get_int_or_none(request.POST.get('tiempo_proceso')),
                'defectos_encontrados': request.POST.get('defectos_encontrados', ''),
                'notas_tecnicas': request.POST.get('notas_tecnicas', ''),
            }
            
            # Remove None values
            detalle_data = {k: v for k, v in detalle_data.items() if v is not None and v != ''}
            
            detalle, error_msg = hilatura_service.agregar_detalle_hilatura(
                hilatura_id=hilatura_id,
                detalle_data=detalle_data
            )
            
            if detalle:
                messages.success(request, error_msg)
                return redirect('detalle_hilatura', hilatura_id=hilatura_id)
            else:
                messages.error(request, error_msg)
                
        except Exception as e:
            messages.error(request, f"Error al agregar detalle: {str(e)}")
    
    context = {
        'hilatura': hilatura,
    }
    return render(request, 'hilatura/agregar_detalle.html', context)


@admin_or_operario_required
def reporte_hilaturas(request):
    """Generar reporte de procesos de hilatura."""
    hilaturas = hilatura_service.get_all_hilaturas()
    
    # Apply filters
    estado = request.GET.get('estado')
    etapa = request.GET.get('etapa')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    
    if estado or etapa or fecha_desde or fecha_hasta:
        hilaturas = hilatura_service.filtrar_hilaturas(
            estado=estado,
            etapa=etapa,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta
        )
    
    # Estadísticas
    estadisticas = hilatura_service.obtener_estadisticas_hilatura()
    
    context = {
        'hilaturas': hilaturas,
        'estadisticas': estadisticas,
        'filtro_estado': estado,
        'filtro_etapa': etapa,
    }
    return render(request, 'hilatura/reporte.html', context)


# Helper functions
def _get_decimal_or_none(value):
    """Convert string to Decimal or return None."""
    if value and value.strip():
        try:
            return Decimal(value)
        except:
            return None
    return None


def _get_int_or_none(value):
    """Convert string to int or return None."""
    if value and value.strip():
        try:
            return int(value)
        except:
            return None
    return None
