from django import forms
from .models import Materia


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
