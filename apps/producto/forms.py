from django import forms
from .models import Categoria, Producto

from bootstrap_modal_forms.forms import BSModalForm


class CategoriaForm(forms.ModelForm):

    class Meta:
        model = Categoria
        fields = [
            'nombre', 'descripcion', 'activo'
        ]

        widgets = {
            'activo': forms.CheckboxInput(attrs={'id': 'es_activo'},),
        }

    def __init__(self, *args, **kwargs):
        super(CategoriaForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            if field != 'activo':
                self.fields[field].widget.attrs.update({
                    'class': 'form-control'
                })


# formulario modal para productos
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ('nombre', 'descripcion', )


class CategoryModalForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion', 'activo']
        labels = {
            'descripcion': 'Descripción',
            'activo': 'Estado activo?'
        }

        TRUE_FALSE_CHOICES = (
            (True, 'SI'),
            (False, 'NO')
        )
        widgets = {
            'activo': forms.Select(choices=TRUE_FALSE_CHOICES, attrs={'class': 'form-control'},),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })

    def clean(self):
        try:
            sc = Categoria.objects.get(
                nombre=self.cleaned_data["nombre"].upper()
            )

            if not self.instance.pk:
                print("El registro ya existe")
                raise forms.ValidationError("El registro ya existe")
            elif self.instance.pk != sc.pk:
                print("Cambio no permitido")
                raise forms.ValidationError("Cambio no permitido")
        except Categoria.DoesNotExist:
            pass
        return self.cleaned_data


class CategoryBSModalForm(BSModalForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion', 'activo']
        labels = {
            'descripcion': 'Descripción',
            'activo': 'Estado activo?'
        }

        TRUE_FALSE_CHOICES = (
            (True, 'SI'),
            (False, 'NO')
        )
        widgets = {
            'activo': forms.Select(choices=TRUE_FALSE_CHOICES, attrs={'class': 'form-control'},),
        }


class ProductoForm(forms.ModelForm):

    class Meta:
        model = Producto
        # fields = '__all__'
        # exclude = ['usuario_creador']
        fields = ['codigo_principal', 'codigo_auxiliar', 'marca', 'modelo', 'categoria',
                  'nombre', 'descripcion', 'precio_costo',
                  'unidad_principal', 'unidad_secundaria', 'unidad_equivalencia',
                  'iva', 'ice', 'irbpnr', 'es_deducible',
                  'precio_uno', 'descuento_uno', 'utilidad_uno', 'precio_neto_uno',
                  'precio_dos', 'descuento_dos', 'utilidad_dos', 'precio_neto_dos',
                  'precio_tres', 'descuento_tres', 'utilidad_tres', 'precio_neto_tres',
                  'precio_cuatro', 'descuento_cuatro', 'utilidad_cuatro', 'precio_neto_cuatro',
                  'precio_principal',
                  'cantidad_minima', 'cantidad_maxima', 'cantidad_inicial',
                  'tiene_vencimiento', 'tiene_serie', 'activo', ]

        labels = {
            'activo': 'Producto estado activo?',
            'es_deducible': 'Producto deducible IR?',
            'tiene_vencimiento': 'Producto con expiración?',
            'tiene_serie': 'Producto tiene serie?'
        }
        # widgets = {
        #    'proveedores': forms.CheckboxSelectMultiple()
        # }
        TRUE_FALSE_CHOICES = (
            (True, 'SI'),
            (False, 'NO')
        )
        widgets = {
            'categoria': forms.Select(attrs={'id': 'categoria'}),
            'unidad_principal': forms.Select(attrs={'id': 'unidad_principal', 'required': True}),
            'unidad_secundaria': forms.Select(attrs={'id': 'unidad_secundaria'}),
            # 'proveedores': forms.SelectMultiple(attrs={'id': 'proveedores'}),

            'precio_costo': forms.NumberInput(attrs={'id': 'precio_costo', 'min': 0}),
            'precio_uno': forms.NumberInput(attrs={'id': 'precio_uno', 'min': 0}),
            'descuento_uno': forms.NumberInput(attrs={'id': 'descuento_uno', 'min': 0}),
            'utilidad_uno': forms.NumberInput(attrs={'id': 'utilidad_uno', 'min': 0}),
            'precio_neto_uno': forms.NumberInput(attrs={'id': 'precio_neto_uno', 'min': 0, 'readonly': 'readonly', 'style': 'text-align:right;font-weight: bold;color:coral', 'placeholder': '0.00', 'title': 'Precio + Imptos. - Desc.'}),

            'precio_dos': forms.NumberInput(attrs={'id': 'precio_dos', 'min': 0}),
            'descuento_dos': forms.NumberInput(attrs={'id': 'descuento_dos', 'min': 0}),
            'utilidad_dos': forms.NumberInput(attrs={'id': 'utilidad_dos', 'min': 0}),
            'precio_neto_dos': forms.NumberInput(attrs={'id': 'precio_neto_dos', 'min': 0, 'readonly': 'readonly', 'style': 'text-align:right;font-weight: bold;color:coral', 'placeholder': '0.00', 'title': 'Precio + Imptos. - Desc.'}),

            'precio_tres': forms.NumberInput(attrs={'id': 'precio_tres', 'min': 0}),
            'descuento_tres': forms.NumberInput(attrs={'id': 'descuento_tres', 'min': 0}),
            'utilidad_tres': forms.NumberInput(attrs={'id': 'utilidad_tres', 'min': 0}),
            'precio_neto_tres': forms.NumberInput(attrs={'id': 'precio_neto_tres', 'min': 0, 'readonly': 'readonly', 'style': 'text-align:right;font-weight: bold;color:coral', 'placeholder': '0.00', 'title': 'Precio + Imptos. - Desc.'}),

            'precio_cuatro': forms.NumberInput(attrs={'id': 'precio_cuatro', 'min': 0}),
            'descuento_cuatro': forms.NumberInput(attrs={'id': 'descuento_cuatro', 'min': 0}),
            'utilidad_cuatro': forms.NumberInput(attrs={'id': 'utilidad_cuatro', 'min': 0}),
            'precio_neto_cuatro': forms.NumberInput(attrs={'id': 'precio_neto_cuatro', 'min': 0, 'readonly': 'readonly', 'style': 'text-align:right;font-weight: bold;color:coral', 'placeholder': '0.00', 'title': 'Precio + Imptos. - Desc.'}),

            # 'precio_costo': forms.NumberInput(attrs={'id': 'precio_costo', 'style': 'text-align:right;'}),
            # 'utilidad': forms.NumberInput(attrs={'id': 'utilidad', 'style': 'text-align:right;'}),
            # 'descuento': forms.NumberInput(attrs={'id': 'descuento', 'style': 'text-align:right;'}),
            # 'precio_venta': forms.NumberInput(attrs={'id': 'precio_venta', 'style': 'text-align:right;'}),
            'unidad_equivalencia': forms.NumberInput(attrs={'min': 1}),
            'cantidad_minima': forms.NumberInput(attrs={'min': 1}),
            'cantidad_maxima': forms.NumberInput(attrs={'min': 1}),
            'cantidad_inicial': forms.NumberInput(attrs={'min': 0}),
            'precio_principal': forms.Select(attrs={'id': 'precio_principal', 'required': True}),
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'nombre': forms.TextInput(attrs={'maxlength': 128}),
            'es_deducible': forms.Select(choices=TRUE_FALSE_CHOICES, attrs={'class': 'form-control'},),
        }

    def __init__(self, *args, **kwargs):
        super(ProductoForm, self).__init__(*args, **kwargs)

        # Ordering Choices in ModelForm
        self.fields['categoria'].queryset = Categoria.objects.order_by('nombre')

        for field in iter(self.fields):
            if (field != 'activo') and (field != 'tiene_vencimiento') \
                    and (field != 'tiene_serie'):
                self.fields[field].widget.attrs.update({
                    'class': 'form-control'
                })
