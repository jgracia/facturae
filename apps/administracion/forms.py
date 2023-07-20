from django import forms
from .models import EntidadFinanciera, TarjetaBancaria, \
    Empresa, Secuencia

from bootstrap_modal_forms.forms import BSModalForm


class BancoForm(BSModalForm):

    class Meta:
        model = EntidadFinanciera
        fields = ['nombre']


class TarjetaForm(BSModalForm):

    class Meta:
        model = TarjetaBancaria
        fields = ['nombre']


class EmpresaForm(forms.ModelForm):

    class Meta:
        model = Empresa
        #fields = '__all__'
        exclude = ['usuario_creador']

        """fields = ['razon_social', 'nombre_comercial', 'ruc', 'direccion_matriz', \
        'telefono', 'pagina_web', 'activo']"""

        labels = {
            'codigo_contribuyente_especial': 'Código Contribuyente Especial',
            'activo': 'Suscriptor activo?',
            'factel': 'Facturación electrónica?',
            'obligado_llevar_contabilidad': 'Obligado Llevar Contabilidad?',
            #'nombre_logo': FileInput(attrs={'html_attribute': value}),
            'factura_total_filas': 'Total filas',
            'factura_total_copias': 'Total copias',
            'factura_margen_superior': 'Margen superior',
            'factura_margen_inferior': 'Margen inferior',
        }

        widgets = {
            'codigo_contribuyente_especial': forms.TextInput(attrs={'placeholder': 'Código contribuyente Especial'}),
            #'pin_token': forms.PasswordInput(),
            #'smtp_clave': forms.PasswordInput(),
            'factel': forms.CheckboxInput(attrs={'id': 'factel'}),
            #'obligado_llevar_contabilidad': forms.CheckboxInput(attrs={'id': 'obligado_llevar_contabilidad'}),
        }

    def __init__(self, *args, **kwargs):
        super(EmpresaForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            if (field != 'activo') and (field != 'factel') and (field != 'obligado_llevar_contabilidad'):
                self.fields[field].widget.attrs.update({
                    'class': 'form-control'
                })


class SecuenciaForm(forms.ModelForm):

    class Meta:
        model = Secuencia
        fields = ['empresa', 'sri_tipo_comprobante', 'usuario_creador', 'punto_establecimiento', \
            'punto_emision', 'ultima_secuencia', 'direccion_establecimiento', 'activo', \
            'comprobante_total_filas', 'comprobante_fisico_ancho', 'comprobante_fisico_alto', \
            'comprobante_fisico_margen_superior', 'comprobante_fisico_margen_inferior', \
            'comprobante_fisico_total_copias', 'comprobante_fisico_tipo_impresora', \
            'comprobante_fisico_tipo_protocolo', 'comprobante_fisico_nombre_impresora']

        labels = {
            'activo': 'Secuencia activa?',
            'comprobante_total_filas': 'Filas por comprobante',
            'comprobante_fisico_ancho': 'Ancho (mm)',
            'comprobante_fisico_alto': 'Alto (mm)',
            'comprobante_fisico_margen_superior': 'Marg. Superior (mm)',
            'comprobante_fisico_margen_inferior': 'Marg. Inferior (mm)',
            'comprobante_fisico_total_copias': 'Copias',
            'comprobante_fisico_tipo_impresora': 'Tipo Impresora',
            'comprobante_fisico_tipo_protocolo': 'Tipo Protocolo',
            'comprobante_fisico_nombre_impresora': 'Nombre Impresora',
        }

        widgets = {
            'direccion_establecimiento': forms.Textarea(attrs={'rows': 3}),
            'comprobante_total_filas': forms.NumberInput(attrs={'id': 'comprobante_total_filas', 'min': 0}),
            'ultima_secuencia': forms.NumberInput(attrs={'id': 'ultima_secuencia', 'min': 0}),
            'comprobante_fisico_ancho': forms.NumberInput(attrs={'id': 'comprobante_fisico_ancho', 'min': 0}),
            'comprobante_fisico_alto': forms.NumberInput(attrs={'id': 'comprobante_fisico_alto', 'min': 0}),
            'comprobante_fisico_margen_superior': forms.NumberInput(attrs={'id': 'comprobante_fisico_margen_superior', 'min': 0}),
            'comprobante_fisico_margen_inferior': forms.NumberInput(attrs={'id': 'comprobante_fisico_margen_inferior', 'min': 0}),
        }

    def __init__(self, *args, **kwargs):
        super(SecuenciaForm, self).__init__(*args, **kwargs)
        self.fields['comprobante_fisico_total_copias'].widget.attrs['min'] = 1
        for field in iter(self.fields):
            if (field != 'activo'):
                self.fields[field].widget.attrs.update({
                    'class': 'form-control'
                })
