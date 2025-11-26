from django import forms
from django.db.models import Q
from .models import Materia, PreparacionMateria, DetallePreparacion, ProcesoHilatura, DetalleHilatura


class MateriaForm(forms.ModelForm):
    """ModelForm for Materia with basic validation."""

    class Meta:
        model = Materia
        fields = ['tipo', 'cantidad', 'unidad_medida', 'lote', 'fecha_ingreso']
        widgets = {
            'fecha_ingreso': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'tipo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tipo de materia'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'unidad_medida': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Unidad de medida'}),
            'lote': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Lote/Referencia'}),
        }

    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad is None:
            return 0
        if cantidad < 0:
            raise forms.ValidationError('La cantidad no puede ser negativa.')
        return cantidad


class PreparacionMateriaForm(forms.ModelForm):
    """Formulario para crear/editar preparaciones de materias primas."""
    
    class Meta:
        model = PreparacionMateria
        fields = ['materia_prima', 'tipo_proceso', 'cantidad_procesada', 
                  'porcentaje_mezcla', 'observaciones', 'calidad_resultado']
        widgets = {
            'materia_prima': forms.Select(attrs={
                'class': 'form-control',
                'required': True,
                'style': 'border-radius: 8px;'
            }),
            'tipo_proceso': forms.Select(attrs={
                'class': 'form-control',
                'required': True,
                'style': 'border-radius: 8px;'
            }),
            'cantidad_procesada': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': '0.01',
                'placeholder': 'Cantidad en kg',
                'style': 'border-radius: 8px;'
            }),
            'porcentaje_mezcla': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 100,
                'step': '0.01',
                'placeholder': 'Porcentaje (%)',
                'style': 'border-radius: 8px;'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones del proceso de preparación...',
                'style': 'border-radius: 8px;'
            }),
            'calidad_resultado': forms.Select(attrs={
                'class': 'form-control',
                'style': 'border-radius: 8px;'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Solo mostrar materias disponibles para procesar
        # Materias que no tienen preparaciones o que tienen preparaciones completadas/rechazadas
        materias_disponibles = Materia.objects.filter(
            Q(preparacionmateria__isnull=True) |
            Q(preparacionmateria__estado__in=['completada', 'rechazada'])
        ).distinct()
        
        self.fields['materia_prima'].queryset = materias_disponibles
        
        # Hacer algunos campos opcionales
        self.fields['porcentaje_mezcla'].required = False
        self.fields['observaciones'].required = False
        self.fields['calidad_resultado'].required = False
    
    def clean_cantidad_procesada(self):
        cantidad = self.cleaned_data.get('cantidad_procesada')
        materia_prima = self.cleaned_data.get('materia_prima')
        
        if cantidad and materia_prima:
            if cantidad > materia_prima.cantidad:
                raise forms.ValidationError(
                    f'La cantidad a procesar no puede exceder la cantidad disponible ({materia_prima.cantidad} {materia_prima.unidad_medida})'
                )
        
        return cantidad
    
    def clean_porcentaje_mezcla(self):
        porcentaje = self.cleaned_data.get('porcentaje_mezcla')
        if porcentaje and (porcentaje < 0 or porcentaje > 100):
            raise forms.ValidationError('El porcentaje debe estar entre 0 y 100.')
        return porcentaje


class DetallePreparacionForm(forms.ModelForm):
    """Formulario para registrar detalles técnicos de la preparación."""
    
    class Meta:
        model = DetallePreparacion
        fields = ['temperatura', 'humedad', 'tiempo_proceso', 'equipo_utilizado',
                  'rendimiento', 'merma', 'notas_tecnicas']
        widgets = {
            'temperatura': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Temperatura (°C)'
            }),
            'humedad': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Humedad (%)'
            }),
            'tiempo_proceso': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': 'Tiempo (minutos)'
            }),
            'equipo_utilizado': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del equipo/máquina'
            }),
            'rendimiento': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 100,
                'step': '0.01',
                'placeholder': 'Rendimiento (%)'
            }),
            'merma': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 100,
                'step': '0.01',
                'placeholder': 'Merma (%)'
            }),
            'notas_tecnicas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Notas técnicas del proceso...'
            }),
        }
    
    def clean_humedad(self):
        humedad = self.cleaned_data.get('humedad')
        if humedad and (humedad < 0 or humedad > 100):
            raise forms.ValidationError('La humedad debe estar entre 0 y 100%.')
        return humedad
    
    def clean_rendimiento(self):
        rendimiento = self.cleaned_data.get('rendimiento')
        if rendimiento and (rendimiento < 0 or rendimiento > 100):
            raise forms.ValidationError('El rendimiento debe estar entre 0 y 100%.')
        return rendimiento
    
    def clean_merma(self):
        merma = self.cleaned_data.get('merma')
        if merma and (merma < 0 or merma > 100):
            raise forms.ValidationError('La merma debe estar entre 0 y 100%.')
        return merma


class FiltroPreparacionForm(forms.Form):
    """Formulario para filtrar preparaciones."""
    
    estado = forms.ChoiceField(
        choices=[('', 'Todos los estados')] + PreparacionMateria.ESTADO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    estado = forms.ChoiceField(
        choices=[('', 'Todos los estados')] + PreparacionMateria.ESTADO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'style': 'border-radius: 8px;'})
    )
    
    tipo_proceso = forms.ChoiceField(
        choices=[('', 'Todos los procesos')] + PreparacionMateria.TIPO_PROCESO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'style': 'border-radius: 8px;'})
    )
    
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )


class ProcesoHilaturaForm(forms.ModelForm):
    """Formulario para crear/editar procesos de hilatura."""
    
    class Meta:
        model = ProcesoHilatura
        fields = ['preparacion_origen', 'etapa', 'cantidad_fibra_entrada', 
                  'titulo_hilo', 'observaciones']
        widgets = {
            'preparacion_origen': forms.Select(attrs={
                'class': 'form-control',
                'style': 'border-radius: 8px;'
            }),
            'etapa': forms.Select(attrs={
                'class': 'form-control',
                'required': True,
                'style': 'border-radius: 8px;'
            }),
            'cantidad_fibra_entrada': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': '0.01',
                'placeholder': 'Cantidad de fibra en kg',
                'style': 'border-radius: 8px;',
                'required': True
            }),
            'titulo_hilo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Ne 30/1, Nm 50/2, Tex 20',
                'style': 'border-radius: 8px;'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones del proceso de hilatura...',
                'style': 'border-radius: 8px;'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Solo mostrar preparaciones completadas
        self.fields['preparacion_origen'].queryset = PreparacionMateria.objects.filter(
            estado='completada'
        ).order_by('-fecha_completado')
        
        # Hacer algunos campos opcionales
        self.fields['preparacion_origen'].required = False
        self.fields['titulo_hilo'].required = False
        self.fields['observaciones'].required = False
    
    def clean_cantidad_fibra_entrada(self):
        cantidad = self.cleaned_data.get('cantidad_fibra_entrada')
        
        if cantidad and cantidad <= 0:
            raise forms.ValidationError('La cantidad debe ser mayor a 0.')
        
        return cantidad


class CompletarHilaturaForm(forms.Form):
    """Formulario para completar un proceso de hilatura."""
    
    cantidad_hilo_salida = forms.DecimalField(
        label='Cantidad de hilo producido (kg)',
        min_value=0,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': 'Cantidad en kg',
            'style': 'border-radius: 8px;'
        })
    )
    
    torsion = forms.DecimalField(
        label='Torsión (TPM)',
        required=False,
        min_value=0,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': 'Torsiones por metro',
            'style': 'border-radius: 8px;'
        })
    )
    
    resistencia = forms.DecimalField(
        label='Resistencia (cN/tex)',
        required=False,
        min_value=0,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': 'Resistencia del hilo',
            'style': 'border-radius: 8px;'
        })
    )
    
    calidad_resultado = forms.ChoiceField(
        label='Calidad del resultado',
        choices=[
            ('excelente', 'Excelente'),
            ('buena', 'Buena'),
            ('regular', 'Regular'),
            ('deficiente', 'Deficiente'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'style': 'border-radius: 8px;'
        })
    )


class DetalleHilaturaForm(forms.ModelForm):
    """Formulario para registrar detalles técnicos de la hilatura."""
    
    class Meta:
        model = DetalleHilatura
        fields = ['velocidad_maquina', 'temperatura', 'humedad', 'maquina_hiladora',
                  'numero_husos', 'velocidad_cardado', 'limpieza_fibras',
                  'longitud_fibra_eliminada', 'porcentaje_impurezas_removidas',
                  'grado_torsion', 'uniformidad', 'tiempo_proceso',
                  'defectos_encontrados', 'notas_tecnicas']
        widgets = {
            'velocidad_maquina': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Velocidad (m/min)',
                'style': 'border-radius: 8px;'
            }),
            'temperatura': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Temperatura (°C)',
                'style': 'border-radius: 8px;'
            }),
            'humedad': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Humedad (%)',
                'style': 'border-radius: 8px;'
            }),
            'maquina_hiladora': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la máquina hiladora',
                'style': 'border-radius: 8px;'
            }),
            'numero_husos': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': 'Número de husos',
                'style': 'border-radius: 8px;'
            }),
            'velocidad_cardado': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Velocidad de cardado (m/min)',
                'style': 'border-radius: 8px;'
            }),
            'limpieza_fibras': forms.Select(attrs={
                'class': 'form-control',
                'style': 'border-radius: 8px;'
            }),
            'longitud_fibra_eliminada': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Longitud de fibra corta eliminada (mm)',
                'style': 'border-radius: 8px;'
            }),
            'porcentaje_impurezas_removidas': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Porcentaje de impurezas removidas (%)',
                'style': 'border-radius: 8px;'
            }),
            'grado_torsion': forms.Select(attrs={
                'class': 'form-control',
                'style': 'border-radius: 8px;'
            }),
            'uniformidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Uniformidad del hilo (%)',
                'style': 'border-radius: 8px;'
            }),
            'tiempo_proceso': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': 'Tiempo (minutos)',
                'style': 'border-radius: 8px;'
            }),
            'defectos_encontrados': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Defectos encontrados durante el proceso...',
                'style': 'border-radius: 8px;'
            }),
            'notas_tecnicas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Notas técnicas del proceso...',
                'style': 'border-radius: 8px;'
            }),
        }
    
    def clean_humedad(self):
        humedad = self.cleaned_data.get('humedad')
        if humedad and (humedad < 0 or humedad > 100):
            raise forms.ValidationError('La humedad debe estar entre 0 y 100%.')
        return humedad
    
    def clean_uniformidad(self):
        uniformidad = self.cleaned_data.get('uniformidad')
        if uniformidad and (uniformidad < 0 or uniformidad > 100):
            raise forms.ValidationError('La uniformidad debe estar entre 0 y 100%.')
        return uniformidad
    
    def clean_porcentaje_impurezas_removidas(self):
        porcentaje = self.cleaned_data.get('porcentaje_impurezas_removidas')
        if porcentaje and (porcentaje < 0 or porcentaje > 100):
            raise forms.ValidationError('El porcentaje debe estar entre 0 y 100%.')
        return porcentaje


class FiltroHilaturaForm(forms.Form):
    """Formulario para filtrar procesos de hilatura."""
    
    estado = forms.ChoiceField(
        choices=[('', 'Todos los estados')] + ProcesoHilatura.ESTADO_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'style': 'border-radius: 8px;'
        })
    )
    
    etapa = forms.ChoiceField(
        choices=[('', 'Todas las etapas')] + ProcesoHilatura.ETAPA_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'style': 'border-radius: 8px;'
        })
    )
    
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'style': 'border-radius: 8px;'
        })
    )
    
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'style': 'border-radius: 8px;'
        })
    )
