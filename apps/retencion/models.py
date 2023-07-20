from django.db import models
from django.contrib.auth.models import User

from apps.administracion.models import Empresa, Secuencia
from apps.sri.models import SriTipoComprobante, SriTipoMoneda, SriTipoImpuesto
from apps.proveedor.models import Proveedor
from apps.compra.models import OrdenCompra

# Create your models here.


class RetencionEstado(models.Model):
    retencion_estado_id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    usuario_creador = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=500)


class ComprobanteRetencion(models.Model):
    comprobante_retencion_id = models.AutoField(
        auto_created=True, primary_key=True, serialize=False)
    empresa = models.ForeignKey(Empresa, null=False, blank=False, on_delete=models.CASCADE)
    proveedor = models.ForeignKey(Proveedor, null=False, blank=False, on_delete=models.CASCADE)
    compra = models.ForeignKey(OrdenCompra, null=False, blank=False, on_delete=models.CASCADE)
    secuencia = models.ForeignKey(Secuencia, null=True, blank=True, on_delete=models.SET_NULL)
    sri_tipo_comprobante = models.ForeignKey(
        SriTipoComprobante, null=True, blank=True, on_delete=models.SET_NULL)
    sri_tipo_moneda = models.ForeignKey(
        SriTipoMoneda, null=True, blank=True, on_delete=models.SET_NULL)
    usuario_creador = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    estado = models.ForeignKey(RetencionEstado, null=True, blank=True, on_delete=models.SET_NULL)
    #activo = models.BooleanField(default=True)
    fecha_emision = models.DateTimeField(null=True)
    numero_secuencia = models.IntegerField(default=0)
    clave_acceso = models.CharField(max_length=49, unique=True)
    numero_autorizacion = models.CharField(max_length=100, null=True, blank=True)
    fecha_autorizacion = models.DateTimeField(null=True, blank=True)
    periodo = models.SmallIntegerField(null=True)
    anio = models.SmallIntegerField(null=True)
    valor_total = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    fecha_generado = models.DateTimeField(auto_now=True)
    archivo_generado = models.TextField(null=True, blank=True)
    archivo_autorizado = models.TextField(null=True, blank=True)
    fecha_error = models.DateTimeField(null=True, blank=True)
    archivo_error = models.TextField(null=True, blank=True)

    def get_numero_secuencia_formateado(self):
        return str(self.numero_secuencia).zfill(9)


class ComprobanteRetencionDetalle(models.Model):
    comprobante_retencion_detalle_id = models.AutoField(
        auto_created=True, primary_key=True, serialize=False)
    #comprobante_retencion = models.ForeignKey(ComprobanteRetencion, null=False, blank=False, on_delete=models.CASCADE)
    retencion = models.ForeignKey(ComprobanteRetencion, null=False,
                                  blank=False, on_delete=models.CASCADE)
    sri_tipo_comprobante_modificado = models.ForeignKey(
        SriTipoComprobante, null=False, blank=False, on_delete=models.CASCADE)
    sri_tipo_impuesto = models.ForeignKey(
        SriTipoImpuesto, null=False, blank=False, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    fecha_emision_documento_modificado = models.DateField(null=True, blank=True)
    numero_documento_modificado = models.CharField(max_length=49)
    #tipo_impuesto = models.IntegerField(default=0, help_text='1=RENTA, 2=IVA')
    tipo_impuesto = models.PositiveSmallIntegerField(
        choices=(
            (1, 'RENTA'),
            (2, 'IVA'),
        )
    )
    valor_base_imponible = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    valor_total = models.DecimalField(max_digits=15, decimal_places=5, default=0)
