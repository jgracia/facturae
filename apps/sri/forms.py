from django import forms
from .models import SriTipoComprobante, SriTipoIdentificacion, \
    SriTarifaIVA, SriTarifaICE, SriTarifaIRBPNR, \
    SriTipoDocumento, SriTipoMoneda, SriTipoImpuesto

from bootstrap_modal_forms.forms import BSModalForm


class TipoComprobanteForm(BSModalForm):
    class Meta:
        model = SriTipoComprobante
        #exclude = ['timestamp']
        fields = ['codigo', 'descripcion', 'alias']


# ajax crud
class TipoComprobanteModalForm(forms.ModelForm):
    class Meta:
        model = SriTipoComprobante
        fields = ('codigo', 'descripcion', 'alias',)


# FORMULARIO MODAL CON VALIDACIÓN EN FONTEND
class TipoComprobanteNewForm(forms.ModelForm):

    class Meta:
        model = SriTipoComprobante
        fields = ('codigo', 'descripcion', 'alias',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })

    def clean(self):
        cleaned_data = super(TipoComprobanteNewForm, self).clean()
        # additional cleaning here
        return cleaned_data


class TipoIdentificacionForm(BSModalForm):
    class Meta:
        model = SriTipoIdentificacion
        fields = ['codigo', 'nombre']


class TipoDocumentoForm(BSModalForm):
    class Meta:
        model = SriTipoDocumento
        fields = ['codigo', 'descripcion', 'alias']


class TipoMonedaForm(BSModalForm):
    class Meta:
        model = SriTipoMoneda
        fields = ['codigo', 'descripcion']


class TarifaIvaForm(BSModalForm):
    class Meta:
        model = SriTarifaIVA
        fields = ['codigo', 'descripcion', 'porcentaje', 'porcentaje_retencion']


class TarifaIceForm(BSModalForm):
    class Meta:
        model = SriTarifaICE
        fields = ['codigo', 'descripcion', 'porcentaje', 'porcentaje_retencion']


class TarifaIrbpnrForm(BSModalForm):
    class Meta:
        model = SriTarifaIRBPNR
        fields = ['codigo', 'descripcion', 'porcentaje', 'porcentaje_retencion']


class TipoImpuestoForm(BSModalForm):
    class Meta:
        model = SriTipoImpuesto
        fields = ['codigo', 'tipo_impuesto', 'descripcion', 'porcentaje', 'porcentaje_retencion']
