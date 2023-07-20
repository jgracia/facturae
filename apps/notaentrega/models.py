from django.db import models
from django.contrib.auth.models import User

from apps.administracion.models import Empresa, Secuencia
from apps.sri.models import SriTipoComprobante
from apps.unidadmedida.models import UnidadMedida
from apps.producto.models import Producto
from apps.cliente.models import Cliente
from apps.servicio.models import Servicio

# Create your models here.

""""
class CarritoNotaEntrega(models.Model):
    usuario = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
    tipo = models.IntegerField(default=1, help_text="1) Productos or 2) Servicios")
    producto = models.ForeignKey(Producto, null=False, blank=False, on_delete=models.CASCADE)
    servicio = models.ForeignKey(Servicio, null=True, blank=True, on_delete=models.SET_NULL)
    cantidad = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    unidad = models.ForeignKey(UnidadMedida, null=True, blank=True, on_delete=models.SET_NULL)

    precio_costo = models.DecimalField(max_digits=15, decimal_places=5, default=0)
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

    def line_total(self):
        return self.cantidad * self.precio
"""


class NotaEntregaEstado(models.Model):
    usuario_creador = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    situacion = models.CharField(max_length=16, unique=True)


class NotaEntrega(models.Model):
    nota_entrega_id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    empresa = models.ForeignKey(Empresa, null=False, blank=False, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, null=False, blank=False, on_delete=models.CASCADE)
    secuencia = models.ForeignKey(Secuencia, null=True, blank=True, on_delete=models.SET_NULL)
    sri_tipo_comprobante = models.ForeignKey(
        SriTipoComprobante, null=True, blank=True, on_delete=models.SET_NULL)
    usuario_creador = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    estado = models.ForeignKey(NotaEntregaEstado, null=True, blank=True, on_delete=models.SET_NULL)
    fecha_emision = models.DateTimeField(null=True)
    numero_secuencia = models.IntegerField(default=0)
    #fecha_validez = models.DateField(null=True)
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

    def get_numero_secuencia_formateado(self):
        return str(self.numero_secuencia).zfill(9)


class NotaEntregaDetalle(models.Model):
    nota_entrega_detalle_id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    nota_entrega = models.ForeignKey(NotaEntrega, null=False, blank=False, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=1,
                            choices=(
                                ('P', 'PRODUCTO'),
                                ('S', 'SERVICIO')
                            )
                            )
    producto = models.ForeignKey(Producto, null=True, blank=True, on_delete=models.SET_NULL)
    servicio = models.ForeignKey(Servicio, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    cantidad = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    unidad = models.ForeignKey(UnidadMedida, null=True, blank=True, on_delete=models.SET_NULL)
    precio_venta = models.DecimalField(max_digits=15, decimal_places=5, default=0)
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


"""
class NotaEntregaServicio(models.Model):
    nota_entrega = models.ForeignKey(NotaEntrega, null=False, blank=False, on_delete=models.CASCADE)
    servicio = models.ForeignKey(Servicio, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    cantidad = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    unidad = models.ForeignKey(UnidadMedida, null=True, blank=True, on_delete=models.SET_NULL)
    precio = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    porcentaje_descuento = models.DecimalField(
        max_digits=15, decimal_places=5, default=0, help_text="Porcentaje de descuento")
    valor_descuento = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    valor_subtotal_sin_impuesto = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    valor_subtotal_12 = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    valor_subtotal_0 = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    valor_subtotal_no_objeto_iva = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    valor_subtotal_exento = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    valor_ice = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    valor_iva = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    valor_total = models.DecimalField(max_digits=15, decimal_places=5, default=0)
"""
