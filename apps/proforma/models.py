from django.db import models
from django.contrib.auth.models import User

from apps.administracion.models import Empresa, Secuencia
from apps.sri.models import SriTipoComprobante
from apps.producto.models import Producto, UnidadMedida as UnidadMedidaProd
from apps.cliente.models import Cliente
from apps.servicio.models import Servicio, UnidadMedida as UnidadMedidaServ

# Create your models here.

"""
class CarritoProforma(models.Model):
    usuario = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
    tipo = models.IntegerField(default=1, help_text="1) Productos or 2) Servicios")
    producto = models.ForeignKey(Producto, null=False, blank=False, on_delete=models.CASCADE)
    servicio = models.ForeignKey(Servicio, null=True, blank=True, on_delete=models.SET_NULL)
    cantidad = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    unidad = models.ForeignKey(UnidadMedidaProd, null=True, blank=True, on_delete=models.SET_NULL)
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


class ProformaEstado(models.Model):
    proforma_estado_id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    usuario_creador = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=500)


class Proforma(models.Model):
    proforma_id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    empresa = models.ForeignKey(Empresa, null=False, blank=False, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, null=False, blank=False, on_delete=models.CASCADE)
    secuencia = models.ForeignKey(Secuencia, null=True, blank=True, on_delete=models.SET_NULL)
    sri_tipo_comprobante = models.ForeignKey(
        SriTipoComprobante, null=True, blank=True, on_delete=models.SET_NULL)
    usuario_creador = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    estado = models.ForeignKey(ProformaEstado, null=True, blank=True, on_delete=models.SET_NULL)
    fecha_emision = models.DateTimeField(null=True)
    numero_secuencia = models.IntegerField(default=0)
    fecha_validez = models.DateField(null=True)
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


class ProformaDetalle(models.Model):
    proforma_detalle_id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    proforma = models.ForeignKey(Proforma, null=False, blank=False, on_delete=models.CASCADE)
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
    unidad = models.ForeignKey(UnidadMedidaProd, null=True, blank=True, on_delete=models.SET_NULL)
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
class ProformaServicio(models.Model):
    proforma = models.ForeignKey(Proforma, null=False, blank=False, on_delete=models.CASCADE)
    servicio = models.ForeignKey(Servicio, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    cantidad = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    unidad = models.ForeignKey(UnidadMedidaServ, null=True, blank=True, on_delete=models.SET_NULL)
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
