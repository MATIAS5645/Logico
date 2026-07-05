from django import forms
from .models import Incidencia

class IncidenciaForm(forms.ModelForm):
    class Meta:
        model = Incidencia
        # Los campos que el usuario debe llenar
        fields = ['movimiento', 'motorista', 'tipo', 'descripcion']
        
        # Agregamos clases de Bootstrap para que se vea bien
        widgets = {
            'movimiento': forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'}),
            'motorista': forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'}),
            'tipo': forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control bg-dark text-white border-secondary', 'rows': 3, 'placeholder': 'Detalle lo sucedido...'}),
        }