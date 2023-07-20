from django import forms
from .models import Almacen


class AlmacenForm(forms.ModelForm):

    class Meta:
        model = Almacen
        fields = [
            'codigo', 'descripcion', 'es_principal', 'activo'
        ]
        TRUE_FALSE_CHOICES = (
            (True, 'SI'),
            (False, 'NO')
        )
        STATE_CHOICES = (
            (True, 'SI'),
            (False, 'NO'),
        )
        widgets = {
            'es_principal': forms.Select(choices=TRUE_FALSE_CHOICES, attrs={'class': 'form-control'},),
            # 'activo': forms.RadioSelect(choices=STATE_CHOICES,)
            'activo': forms.CheckboxInput(attrs={'id': 'es_activo'},),
        }

    def __init__(self, *args, **kwargs):
        super(AlmacenForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            if field != 'activo' and field != 'es_principal':
                self.fields[field].widget.attrs.update({
                    'class': 'form-control'
                })
