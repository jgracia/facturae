from django import forms
from .models import Servicio


class ServicioForm(forms.ModelForm):

    class Meta:
        model = Servicio
        #fields = '__all__'
        fields = [
            'nombre', 'descripcion', 'precio', 'descuento', 'iva', 'ice', 'unidad_medida', 'activo', 'es_deducible'
        ]

        TRUE_FALSE_CHOICES = (
            (True, 'SI'),
            (False, 'NO')
        )

        widgets = {
            'activo': forms.CheckboxInput(attrs={'id': 'es_activo'},),
            'es_deducible': forms.Select(choices=TRUE_FALSE_CHOICES, attrs={'class': 'form-control'},),
        }

    def __init__(self, *args, **kwargs):
        super(ServicioForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            if field != 'activo':
                self.fields[field].widget.attrs.update({
                    'class': 'form-control'
                })
