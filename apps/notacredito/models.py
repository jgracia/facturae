from django.db import models
from django.contrib.auth.models import User

from apps.administracion.models import Empresa, Secuencia
from apps.sri.models import SriTipoComprobante, SriTipoMoneda
from apps.cliente.models import Cliente
from apps.producto.models import Producto


# Create your models here.
class NotaCreditoEstado(models.Model):
    notacredito_estado_id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    usuario_creador = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=500)


class NotaCredito(models.Model):
    nota_credito_id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    empresa = models.ForeignKey(Empresa, null=False, blank=False, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, null=False, blank=False, on_delete=models.CASCADE)
    secuencia = models.ForeignKey(Secuencia, null=True, blank=True, on_delete=models.SET_NULL)
    sri_tipo_comprobante = models.ForeignKey(
        SriTipoComprobante, null=True, blank=True, on_delete=models.SET_NULL)
    sri_tipo_comprobante_modificado = models.CharField(max_length=10, null=True, blank=True)
    sri_tipo_moneda = models.ForeignKey(
        SriTipoMoneda, null=True, blank=True, on_delete=models.SET_NULL)
    usuario_creador = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    #activo = models.BooleanField(default=True)
    estado = models.ForeignKey(NotaCreditoEstado, null=True, blank=True, on_delete=models.SET_NULL)
    fecha_emision = models.DateTimeField(null=True)
    numero_secuencia = models.IntegerField(default=0)
    clave_acceso = models.CharField(max_length=49, unique=True)
    numero_autorizacion = models.CharField(max_length=100, null=True, blank=True)
    fecha_autorizacion = models.DateTimeField(null=True, blank=True)
    fecha_emision_documento_modificado = models.DateTimeField(null=True, blank=True)
    numero_documento_modificado = models.CharField(max_length=49)
    motivo_modificacion = models.TextField(null=True, blank=True)
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
    fecha_generado = models.DateTimeField(auto_now=True)
    archivo_generado = models.TextField(null=True, blank=True)
    archivo_autorizado = models.TextField(null=True, blank=True)
    fecha_error = models.DateTimeField(null=True, blank=True)
    archivo_error = models.TextField(null=True, blank=True)


class NotaCreditoDetalle(models.Model):
    nota_credito_detalle_id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    nota_credito = models.ForeignKey(NotaCredito, null=False, blank=False, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, null=False, blank=False, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    cantidad = models.DecimalField(max_digits=15, decimal_places=5, default=0)
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
