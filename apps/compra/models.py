from django.db import models
from django.contrib.auth.models import User

from apps.sri.models import SriTipoComprobante
from apps.unidadmedida.models import UnidadMedida
from apps.producto.models import Producto
from apps.proveedor.models import Proveedor
from apps.servicio.models import Servicio
from apps.administracion.models import Empresa
from apps.sri.models import SriTipoImpuesto
import datetime

# Create your models here.

"""
class CarritoCompra(models.Model):
    PRODUCTO = 'PROD'
    SERVICIO = 'SERV'
    TIPO_CHOICES = [
        (PRODUCTO, 'Producto'),
        (SERVICIO, 'Servicio'),
    ]
    usuario = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
    #producto = models.ForeignKey(Producto, null=False, blank=False, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, null=True, blank=True, on_delete=models.SET_NULL)
    #tipo = models.IntegerField(default=1, help_text="1) Productos or 2) Servicios")
    tipo = models.CharField(
        max_length=4,
        choices=TIPO_CHOICES,
        default=PRODUCTO,
    )
    #token = models.IntegerField(default=0, help_text="Producto_Id o Servicio_Id")
    servicio = models.ForeignKey(Servicio, null=True, blank=True, on_delete=models.SET_NULL)
    cantidad = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    unidad_medida_prod = models.ForeignKey(UnidadMedida, null=True, blank=True,
                                           on_delete=models.SET_NULL, related_name='unidad_producto')
    # unidad_secundaria = models.ForeignKey(
    #    Unidad, null=True, blank=True, on_delete=models.SET_NULL, related_name='unidad_secundaria')
    unidad_medida_serv = models.ForeignKey(
        UnidadMedida, null=True, blank=True, on_delete=models.SET_NULL, related_name='unidad_servicio')
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


class CarritoCompraLote(models.Model):
    carrito = models.ForeignKey(CarritoCompra, null=False, blank=False, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, null=False, blank=False, on_delete=models.CASCADE)
    lote_numero = models.CharField(max_length=10, unique=True)
    #descripcion = models.CharField(max_length=64)
    fecha_caducidad = models.DateField(default=datetime.date.today)
    cantidad = models.DecimalField(max_digits=25, decimal_places=5, default=0)


class CarritoCompraSerie(models.Model):
    carrito = models.ForeignKey(CarritoCompra, null=False, blank=False, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, null=False, blank=False, on_delete=models.CASCADE)
    linea = models.IntegerField(default=1, help_text='Orden: 1, 2, 3, etc.')
    serie_numero = models.CharField(max_length=16, unique=True)
"""


class OrdenCompraEstado(models.Model):
    orden_estado_id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    usuario_creador = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=500)


class OrdenCompra(models.Model):
    orden_id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    empresa = models.ForeignKey(Empresa, null=False, blank=False, on_delete=models.CASCADE)
    proveedor = models.ForeignKey(Proveedor, null=True, blank=True, on_delete=models.SET_NULL)
    sri_tipo_comprobante = models.ForeignKey(
        SriTipoComprobante, null=True, blank=True, on_delete=models.SET_NULL)
    usuario_creador = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    estado = models.ForeignKey(OrdenCompraEstado, null=True, blank=True, on_delete=models.SET_NULL)
    fecha_emision = models.DateTimeField(null=True)
    numero_comprobante = models.CharField(max_length=17, null=True, blank=True)
    clave_acceso = models.CharField(max_length=49, null=True, blank=True)
    guia_remision = models.CharField(max_length=20, null=True, blank=True)
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
    valor_propina = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    valor_total = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    fecha_recibido = models.DateTimeField(auto_now=True)
    archivo_autorizado = models.TextField(null=True, blank=True)

    class Meta:  # nombre en plural
        verbose_name_plural = 'ordenes'


class OrdenCompraDetalle(models.Model):
    orden_detalle_id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    compra = models.ForeignKey(OrdenCompra, null=False, blank=False, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=1,
                            choices=(
                                ('P', 'PRODUCTO'),
                                ('S', 'SERVICIO')
                            )
                            )
    #producto = models.ForeignKey(Producto, null=True, blank=True, on_delete=models.SET_NULL)
    producto = models.ForeignKey(Producto, null=True, blank=True, on_delete=models.SET_NULL)
    servicio = models.ForeignKey(Servicio, null=True, blank=True, on_delete=models.SET_NULL)
    #lote = models.ForeignKey(SeguimientoLote, null=True, blank=True, on_delete=models.SET_NULL)
    #serie = models.ForeignKey(SeguimientoSerie, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    cantidad = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    unidad = models.ForeignKey(UnidadMedida, null=True, blank=True, on_delete=models.SET_NULL)
    precio_costo = models.DecimalField(max_digits=15, decimal_places=5, default=0)
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
class OrdenCompraDetalleServicio(models.Model):
    compra = models.ForeignKey(OrdenCompra, null=False, blank=False, on_delete=models.CASCADE)
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


class OrdenCompraRetencion(models.Model):
    orden_retencion_id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    orden = models.ForeignKey(OrdenCompra, null=False, blank=False, on_delete=models.CASCADE)
    sri_tipo_impuesto = models.ForeignKey(
        SriTipoImpuesto, null=True, blank=True, on_delete=models.SET_NULL)
    valor_total = models.DecimalField(max_digits=15, decimal_places=5, default=0)

    class Meta:  # nombre en plural
        verbose_name_plural = 'Orden Retenciones'
