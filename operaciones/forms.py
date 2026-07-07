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

from django import forms
from .models import Incidencia

class IncidenciaMovilForm(forms.ModelForm):
    # Campo virtual para que el motorista marque rápido desde el celular si requiere reenvío
    causa_reenvio = forms.ChoiceField(
        choices=[
            ('ninguna', '--- Otro Motivo / Alerta General ---'),
            ('cliente_ausente', 'Cliente no estaba en su casa (Requiere Reenvío)'),
        ],
        initial='ninguna',
        widget=forms.Select(attrs={'class': 'form-select form-select-lg bg-dark text-white border-secondary'}),
        label="Acción Rápida (Móvil)"
    )

    class Meta:
        model = Incidencia
        fields = ['movimiento', 'motorista', 'tipo', 'descripcion']
        widgets = {
            'movimiento': forms.Select(attrs={'class': 'form-select form-select-lg bg-dark text-white border-secondary'}),
            'motorista': forms.Select(attrs={'class': 'form-select form-select-lg bg-dark text-white border-secondary'}),
            'tipo': forms.Select(attrs={'class': 'form-select form-select-lg bg-dark text-white border-secondary'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control bg-dark text-white border-secondary', 'rows': 3, 'placeholder': 'Ej: El cliente no contestó el teléfono ni el timbre...'}),
        }