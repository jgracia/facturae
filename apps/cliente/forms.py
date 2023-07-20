from django import forms
from .models import Cliente


class ClienteForm(forms.ModelForm):

    class Meta:
        model = Cliente
        fields = ['identificacion_tipo', 'identificacion', 'nombre',
                  'direccion', 'telefono', 'celular', 'email',
                  'obligado_contabilidad', 'activo']
        labels = {
            'identificacion_tipo': 'Tipo de Identificación',
            'activo': 'Activo?',
            'nombre': 'Apellidos y Nombres',
            'identificacion': 'Identificación',
            'obligado_contabilidad': 'Obligado a llevar contabilidad?',
            'direccion': 'Dirección',
            'telefono': 'Teléfono',
            # 'extension': 'Extensión',
            'celular': 'Teléfono Celular',
            'email': 'Correo electrónico'
        }

        widgets = {
            'identificacion_tipo': forms.Select(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'id': 'es_activo'},),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'identificacion': forms.TextInput(attrs={'class': 'form-control'}),
            'obligado_contabilidad': forms.CheckboxInput(attrs={'id': 'oblig_contab'},),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            # 'extension': forms.TextInput(attrs={'class':'form-control'}),
            'celular': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'nombre@example.com'})
        }
