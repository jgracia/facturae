from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

from apps.administracion.models import Empresa
from apps.producto.models import Producto
from apps.servicio.models import Servicio
from apps.unidadmedida.models import UnidadMedida

# Create your models here.

"""
class Cesta(models.Model):
    usuario = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
    creado_en = models.DateTimeField(default=datetime.now)
    clave_apli = models.CharField(
        max_length=16, help_text="apli_venta, apli_compra, apli_proforma, etc.")
    clave_pers = models.CharField(max_length=16, help_text="RUC del Cliente o Proveedor")


class Item(models.Model):
    PRODUCTO = 'PROD'
    SERVICIO = 'SERV'
    TIPO_ELECCIONES = [
        (PRODUCTO, 'Producto'),
        (SERVICIO, 'Servicio'),
    ]
    tipo = models.CharField(
        max_length=4,
        choices=TIPO_ELECCIONES,
        default=PRODUCTO,
    )
    producto = models.ForeignKey(Producto, null=True, blank=True, on_delete=models.SET_NULL)
    servicio = models.ForeignKey(Servicio, null=True, blank=True, on_delete=models.SET_NULL)
    cantidad = models.IntegerField(default=1)
    unidad_medida_prod = models.ForeignKey(UnidadMedida, null=True, blank=True,
                                           on_delete=models.SET_NULL, related_name='unidad_producto')
    unidad_medida_serv = models.ForeignKey(
        UnidadMedida, null=True, blank=True, on_delete=models.SET_NULL, related_name='unidad_servicio')
    precio = models.FloatField(blank=True)
    porcentaje_descuento = models.DecimalField(
        max_digits=15, decimal_places=5, default=0, help_text="Porcentaje de descuento")
    valor_descuento = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    valor_subtotal_sin_impuesto = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    valor_subtotal_12 = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    valor_subtotal_0 = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    valor_subtotal_no_objeto_iva = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    valor_subtotal_exento = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    valor_base_imponible_ibrpnr = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    valor_subtotal_ibrpnr = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    valor_ice = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    valor_iva = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    valor_total = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    cesta = models.ForeignKey(Cesta, null=False, blank=False, on_delete=models.CASCADE)

    def total_linea(self):
        return self.cantidad * self.precio


class Lote(models.Model):
    item = models.ForeignKey(Item, null=False,
                             blank=False, on_delete=models.CASCADE)
    lote_numero = models.CharField(max_length=10, unique=True)
    fecha_caducidad = models.DateField(default=datetime.now)
    cantidad = models.DecimalField(max_digits=25, decimal_places=5, default=0)


class Serie(models.Model):
    item = models.ForeignKey(Item, null=False,
                             blank=False, on_delete=models.CASCADE)
    serie_numero = models.CharField(max_length=16, unique=True)
    cantidad = models.DecimalField(max_digits=25, decimal_places=5, default=1)
"""


class Item(models.Model):
    PRODUCTO = 'PROD'
    SERVICIO = 'SERV'
    TIPO_ELECCIONES = [
        (PRODUCTO, 'Producto'),
        (SERVICIO, 'Servicio'),
    ]
    tipo = models.CharField(
        max_length=4,
        choices=TIPO_ELECCIONES,
        default=PRODUCTO,
    )
    producto = models.ForeignKey(Producto, null=True, blank=True, on_delete=models.SET_NULL)
    servicio = models.ForeignKey(Servicio, null=True, blank=True, on_delete=models.SET_NULL)
    #opciones = models.ForeignKey(Opcion, null=True, blank=True, on_delete=models.CASCADE)
    #cantidad = models.IntegerField(default=1)
    cantidad = models.DecimalField(max_digits=15, decimal_places=5, default=1)
    # unidad_medida_prod = models.ForeignKey(UnidadMedida, null=True, blank=True,
    #                                       on_delete=models.SET_NULL, related_name='unidad_producto')
    # unidad_medida_serv = models.ForeignKey(
    #    UnidadMedida, null=True, blank=True, on_delete=models.SET_NULL, related_name='unidad_servicio')
    unidad_medida = models.ForeignKey(UnidadMedida, null=True, blank=True,
                                      on_delete=models.SET_NULL)
    precio = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    porcentaje_descuento = models.DecimalField(
        max_digits=15, decimal_places=5, default=0, help_text="Porcentaje de descuento")
    valor_descuento = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    valor_subtotal_sin_impuesto = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    valor_subtotal_12 = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    valor_subtotal_0 = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    valor_subtotal_no_objeto_iva = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    valor_subtotal_exento = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    valor_base_imponible_ibrpnr = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    valor_subtotal_ibrpnr = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    valor_ice = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    valor_iva = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    valor_total = models.DecimalField(max_digits=15, decimal_places=5, default=0)


class Lote(models.Model):
    item = models.ForeignKey(Item, null=False,
                             blank=False, on_delete=models.CASCADE)
    lote_numero = models.CharField(max_length=10)
    fecha_caducidad = models.DateField(default=datetime.now)
    cantidad = models.DecimalField(max_digits=25, decimal_places=5, default=0)


class Serie(models.Model):
    item = models.ForeignKey(Item, null=False,
                             blank=False, on_delete=models.CASCADE)
    serie_numero = models.CharField(max_length=16)
    cantidad = models.DecimalField(max_digits=25, decimal_places=5, default=1)


class Opcion(models.Model):
    item = models.ForeignKey(Item, null=False,
                             blank=False, on_delete=models.CASCADE, related_name="opciones")
    nombre = models.CharField(max_length=32)
    valor = models.CharField(max_length=64)


class Cesta(models.Model):
    usuario = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
    creado_en = models.DateTimeField(default=datetime.now)
    clave_apli = models.CharField(
        max_length=16, help_text="CART-VENTA, CART-COMPRA, CART-PROFORMA, etc.")
    #clave_pers = models.CharField(max_length=16, help_text="RUC del Cliente o Proveedor")
    empresa = models.ForeignKey(Empresa, null=False, blank=False, on_delete=models.CASCADE)
    items = models.ManyToManyField(Item)

    def obtener_total_filas(self):
        return self.items.count()

    def obtener_sub_total(self):
        return 0 + sum([item.valor_subtotal_sin_impuesto for item in self.items.all()])

    def obtener_total_descuento(self):
        return 0 + sum([item.valor_descuento for item in self.items.all()])

    def obtener_base_imponible(self):
        return 0 + sum([item.valor_subtotal_12 for item in self.items.all()])

    def obtener_total_tarifa_cero(self):
        return 0 + sum([item.valor_subtotal_0 for item in self.items.all()])

    def obtener_total_iva(self):
        return 0 + sum([item.valor_iva for item in self.items.all()])

    def obtener_gran_total(self):
        return 0 + sum([item.valor_total for item in self.items.all()])

    def obtener_items(self):
        return self.items.all()

    def vaciar_cesta(self):
        self.items.all().delete()
