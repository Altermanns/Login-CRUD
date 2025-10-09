from django import forms
from .models import Materia


class CreateMateriaForm(forms.Form):
    tipo = forms.CharField(label='Tipo', max_length=100, required=False)
    cantidad = forms.IntegerField(label='Cantidad', min_value=0, required=False)
    unidad_medida = forms.CharField(label='Unidad de medida', max_length=50, required=False)
    lote = forms.CharField(label='Lote', max_length=100, required=False)
    fecha_ingreso = forms.DateField(label='Fecha de ingreso', required=False, widget=forms.DateInput(attrs={'type': 'date'}))


class MateriaForm(forms.ModelForm):
    class Meta:
        model = Materia
        fields = ['tipo', 'cantidad', 'unidad_medida', 'lote', 'fecha_ingreso']
        widgets = {
            'fecha_ingreso': forms.DateInput(attrs={'type': 'date'})
        }
