from django import forms
from django.db.models import Q
from .models import Materia, PreparacionMateria, DetallePreparacion


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
                'required': True
            }),
            'tipo_proceso': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'cantidad_procesada': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': '0.01',
                'placeholder': 'Cantidad en kg'
            }),
            'porcentaje_mezcla': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 100,
                'step': '0.01',
                'placeholder': 'Porcentaje (%)'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones del proceso de preparación...'
            }),
            'calidad_resultado': forms.Select(attrs={
                'class': 'form-control'
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
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    tipo_proceso = forms.ChoiceField(
        choices=[('', 'Todos los procesos')] + PreparacionMateria.TIPO_PROCESO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
