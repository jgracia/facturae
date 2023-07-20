from django import forms
from .models import UnidadMedida

# formulario modal para productos


class ModalUnitForm(forms.ModelForm):
    class Meta:
        model = UnidadMedida
        fields = ('abreviatura', 'nombre', )


class UnidadMedidaForm(forms.ModelForm):

    class Meta:
        model = UnidadMedida
        fields = [
            'nombre', 'abreviatura', 'activo'
        ]

        widgets = {
            'activo': forms.CheckboxInput(attrs={'id': 'es_activo'},),
        }

    def __init__(self, *args, **kwargs):
        super(UnidadMedidaForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            if field != 'activo':
                self.fields[field].widget.attrs.update({
                    'class': 'form-control'
                })
