from django import forms
from django.forms import ValidationError
from apps.usuario.models import Turno
from .models import PeriodoContable, PlanCuenta, AsientoContable, AsientoAutomatico

from django.db.models import F, Value
from django.db.models.functions import Concat
from django.db.models import CharField, Value as V

from bootstrap_modal_forms.forms import BSModalForm
import datetime

# from apps.contabilidad.models import Category, Selection
# from fancytree.widgets import FancyTreeWidget


class DateInput(forms.DateInput):
    input_type = 'date'


class PeriodoContableForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(PeriodoContableForm, self).__init__(*args, **kwargs)
        #self.fields['cuenta'].queryset = Cuenta.objects.filter(tipo='CUENTA')
        today = datetime.date.today()
        self.fields['fecha_inicio'].initial = format(today, '%Y-%m-%d')

    class Meta:
        model = PeriodoContable

        # fields = '__all__'
        fields = ['fecha_inicio', 'descripcion', ]

        widgets = {
            'fecha_inicio': DateInput(format='%Y-%m-%d'),
        }


"""class CrearTurnoForm(forms.ModelForm):

    class Meta:
        model = Turno

        fields = ['concepto_apertura', 'importe_apertura']

        labels = {
            'concepto_apertura': 'Concepto',
            'importe_apertura': 'Importe'
        }

        widgets = {
            'concepto_apertura': forms.TextInput(attrs={'id': 'concepto', 'maxlength': 128}),
            'importe_apertura': forms.NumberInput(attrs={'id': 'importe', 'min': 0}),
        }

    def __init__(self, *args, **kwargs):
        super(CrearTurnoForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })"""


class CrearTurnoForm(BSModalForm):

    class Meta:
        model = Turno

        fields = ['concepto_apertura', 'importe_apertura']

        labels = {
            'concepto_apertura': 'Concepto',
            'importe_apertura': 'Importe'
        }

        widgets = {
            'concepto_apertura': forms.TextInput(attrs={'id': 'concepto', 'maxlength': 128}),
            'importe_apertura': forms.NumberInput(attrs={'id': 'importe', 'min': 0}),
        }


class PlanCuentaForm(forms.ModelForm):

    class Meta:
        model = PlanCuenta

        # fields = '__all__'
        fields = ['codigo', 'nombre', 'clasificacion', 'tipo', 'parent']

        # widgets = {
        #    'codigo': forms.TextInput(attrs={'id': 'codigo', 'maxlength': 12}),
        # }

    """def clean(self):
        super(CuentaForm, self).clean()

        codigo = self.cleaned_data['codigo']
        tipo = self.cleaned_data['tipo']

        if len(codigo) == 1:
            # NIVEL 1
            print("codigo = %s" % codigo)
            print("tipo = %s" % tipo)
            if tipo != 'CLASE':
                # raise ValidationError('Código no válido')
                self.add_error('codigo', 'Código no válido')

        elif len(codigo) == 3:
            # NIVEL 2
            if tipo != 'GRUPO':
                # raise ValidationError('Código no válido')
                self.add_error('codigo', 'Código no válido')
        else:
            # raise ValidationError('Código no válido')
            self.add_error('codigo', 'Código no válido')

        return codigo"""


class AsientoForm(forms.ModelForm):

    class Meta:
        model = AsientoContable

        # fields = '__all__'
        fields = ['fecha', 'glosa', 'comprobante']

        widgets = {
            'fecha': forms.DateInput(attrs={
                'class': 'form-control datetimepicker-input',
                'data-target': '#datetimepicker1'
            }),

        }


"""
categories = Category.objects.order_by('tree_id', 'lft')


class SelectionForm(forms.ModelForm):
    class Meta:
        model = Selection
        fields = ('name', 'categories')
        widgets = {
            'categories': FancyTreeWidget(queryset=categories)
        }
"""


class AsientoAutomaticoForm(forms.ModelForm):

    class Meta:
        model = AsientoAutomatico

        # fields = '__all__'
        fields = ['cuenta', ]

        labels = {
            'cuenta': 'Cuenta Contable',
        }

    def __init__(self, *args, **kwargs):
        super(AsientoAutomaticoForm, self).__init__(*args, **kwargs)
        #self.fields['cuenta'].queryset = Cuenta.objects.filter(tipo='CUENTA')

        self.fields['cuenta'].choices = [
            (account.codigo, account.getFullName()) for account in Cuenta.objects.filter(tipo='CUENTA')]
