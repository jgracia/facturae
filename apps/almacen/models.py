from django.db import models
from django.contrib.auth.models import User
from apps.administracion.models import Empresa
from apps.producto.models import Producto, UnidadMedida
from simple_history.models import HistoricalRecords
from simple_history import register
from model_utils.models import TimeStampedModel

import datetime

# Create your models here.


class Almacen(models.Model):
    almacen_id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    usuario_creador = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    codigo = models.CharField(unique=True, max_length=5)
    descripcion = models.CharField(max_length=30)
    activo = models.BooleanField(default=True)
    es_principal = models.BooleanField(default=False)
    empresa = models.ForeignKey(Empresa, null=False, blank=False, on_delete=models.CASCADE)

    def __str__(self):
        return self.descripcion


class TipoMovimiento(models.Model):
    tipo_movimiento_id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    usuario_creador = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    codigo = models.CharField(unique=True, max_length=10)
    descripcion = models.CharField(max_length=64)
    pide_referencia = models.BooleanField(default=False)
    es_entrada = models.BooleanField(default=False)
    es_salida = models.BooleanField(default=False)
    es_existencia = models.BooleanField(default=False)
    es_ajuste = models.BooleanField(default=False)
    estado = models.BooleanField(default=True)


class Kardex(models.Model):
    # EXISTENCIA = 0
    # ENTRADA = 1
    # SALIDA = 2
    # TYPE_CHOICES = (
    #    (EXISTENCIA, 'EXISTENCIA'),
    #    (ENTRADA, 'ENTRADA'),
    #    (SALIDA, 'SALIDA'),
    # )
    kardex_id = models.AutoField(
        auto_created=True, primary_key=True, serialize=False)
    # tipo = models.PositiveSmallIntegerField(choices=TYPE_CHOICES, null=False, blank=False)
    movimiento = models.ForeignKey(
        TipoMovimiento, null=True, blank=True, on_delete=models.SET_NULL)
    orden_id = models.IntegerField(default=0, help_text="factura_id, orden_id, etc..")
    numero_comprobante = models.CharField(max_length=17, null=True, blank=True)
    referencia = models.CharField(max_length=128, null=True, blank=True)
    producto = models.ForeignKey(Producto, null=True, blank=True, on_delete=models.SET_NULL)
    unidad = models.ForeignKey(UnidadMedida, null=True, blank=True, on_delete=models.SET_NULL)
    # submultiplo = xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    # fecha_operacion = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    # cantidad_ingreso = models.DecimalField(max_digits=25, decimal_places=5)
    # precio_ingreso = models.DecimalField(max_digits=25, decimal_places=5)
    # valor_ingreso = models.DecimalField(max_digits=25, decimal_places=5)
    # cantidad_salida = models.DecimalField(max_digits=25, decimal_places=5)
    # precio_salida = models.DecimalField(max_digits=25, decimal_places=5)
    # valor_salida = models.DecimalField(max_digits=25, decimal_places=5)

    cantidad = models.DecimalField(max_digits=25, decimal_places=5, default=0)
    costo = models.DecimalField(max_digits=25, decimal_places=5, default=0)
    total = models.DecimalField(max_digits=25, decimal_places=5, default=0)

    cantidad_total = models.DecimalField(max_digits=25, decimal_places=5, default=0)
    precio_total = models.DecimalField(max_digits=25, decimal_places=5, default=0)
    valor_total = models.DecimalField(max_digits=25, decimal_places=5, default=0)

    empresa = models.ForeignKey(Empresa, null=True, blank=True, on_delete=models.SET_NULL)
    almacen = models.ForeignKey(Almacen, null=True, blank=True, on_delete=models.SET_NULL)
    """metodo = models.CharField(max_length=5,
                            choices=(
                                    ('PEPS', 'PRIMERAS ENTRADAS, PRIMERAS SALIDAS'),
                                    ('UEPS', 'ÚLTIMAS ENTRADAS, PRIMERAS SALIDAS'),
                                    ('PROM', 'PROMEDIO PONDERADO'),
                            )
                            )"""
    usuario_creador = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)


class ProductoLote(models.Model):
    producto_lote_id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    usuario_creador = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    kardex = models.ForeignKey(Kardex, null=True, blank=True, on_delete=models.CASCADE)
    almacen = models.ForeignKey(Almacen, null=True, blank=True, on_delete=models.DO_NOTHING)
    producto = models.ForeignKey(Producto, null=False, blank=False, on_delete=models.CASCADE)
    lote_numero = models.CharField(max_length=10)
    fecha_caducidad = models.DateField(default=datetime.date.today)
    referencia = models.CharField(max_length=64, null=True, blank=True,
                                  help_text='Compra, Inventario Inicial, etc.')
    #cantidad = models.DecimalField(max_digits=25, decimal_places=5, default=0)
    # history = HistoricalRecords()

    class Meta:
        #db_table = 'app_version'
        constraints = [
            models.UniqueConstraint(fields=['producto', 'lote_numero',
                                            'fecha_caducidad'], name='unique_productolote')
        ]


# Agregar campos adicionales a modelos históricos
'''
class TarjetaKardexHistoricalModel(models.Model):
    """
    Modelo abstracto para modelos de historia que siguen el Kardex.
    """
    kardex = models.IntegerField(blank=True, null=True)

    class Meta:
        abstract = True
'''


class ControlProductoLote(TimeStampedModel):
    producto = models.ForeignKey(Producto, null=False, blank=False, on_delete=models.CASCADE)
    lote = models.ForeignKey(ProductoLote, on_delete=models.DO_NOTHING)
    almacen = models.ForeignKey(Almacen, on_delete=models.DO_NOTHING)
    cantidad = models.DecimalField(max_digits=25, decimal_places=5, default=0)
    history = HistoricalRecords()
    # Modelo con campos extras
    #history = HistoricalRecords(bases=[TarjetaKardexHistoricalModel, ])
    #__kardex = None

    class Meta:
        unique_together = (('almacen', 'producto', 'lote'),)

    # @property
    # def _kardex(self):
    #    return self.__kardex

    # @_kardex.setter
    # def _kardex(self, value):
    #    self.__kardex = value


# Nombre de tabla de historial personalizado
# register(ControlProductoLote, table_name='almacen_historico_lote')


class ProductoSerie(models.Model):
    producto_serie_id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    usuario_creador = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    kardex = models.ForeignKey(Kardex, null=True, blank=True, on_delete=models.CASCADE)
    almacen = models.ForeignKey(Almacen, on_delete=models.DO_NOTHING)
    producto = models.ForeignKey(Producto, null=False, blank=False, on_delete=models.CASCADE)
    literal = models.IntegerField(default=1, help_text='Item: 1, 2, 3, etc.')
    serie_numero = models.CharField(max_length=16, unique=True)
    cantidad = models.DecimalField(max_digits=25, decimal_places=5, default=0)
    # history = HistoricalRecords()


class ControlProductoSerie(TimeStampedModel):
    producto = models.ForeignKey(Producto, null=False, blank=False, on_delete=models.CASCADE)
    serie = models.ForeignKey(ProductoSerie, on_delete=models.DO_NOTHING)
    almacen = models.ForeignKey(Almacen, on_delete=models.DO_NOTHING)
    cantidad = models.DecimalField(max_digits=25, decimal_places=5, default=0)
    history = HistoricalRecords()

    class Meta:
        unique_together = (('almacen', 'producto', 'serie'),)


class ControlProducto(TimeStampedModel):
    producto = models.ForeignKey(Producto, on_delete=models.DO_NOTHING)
    # producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    almacen = models.ForeignKey(Almacen, on_delete=models.DO_NOTHING)
    stock = models.DecimalField(max_digits=25, decimal_places=8, default=0)
    precio = models.DecimalField(max_digits=25, decimal_places=8, default=0)
    history = HistoricalRecords()

    class Meta:
        unique_together = (('producto', 'almacen'),)


class ProductoResumen(models.Model):
    producto_id = models.BigIntegerField(primary_key=True)
    nombre = models.CharField(max_length=128, unique=True)
    codigo_principal = models.CharField(max_length=30, unique=True)
    # producto = models.ForeignKey(Producto, on_delete=models.DO_NOTHING)
    # proveedores = models.ManyToManyField(Proveedor)
    existencia = models.DecimalField(max_digits=15, decimal_places=5)
    unidad = models.CharField(max_length=5)
    precio_costo = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    # precio_uno = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    # descuento_uno = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    # utilidad_uno = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    precio_neto_uno = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    precio_neto_dos = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    precio_neto_tres = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    precio_neto_cuatro = models.DecimalField(max_digits=15, decimal_places=5, default=0)

    class Meta:
        managed = False
        db_table = 'almacen_productoresumen'


class InventarioExistencia(models.Model):
    producto_id = models.BigIntegerField(primary_key=True)
    nombre = models.CharField(max_length=128, unique=True)
    codigo_principal = models.CharField(max_length=30, unique=True)
    existencia = models.DecimalField(max_digits=15, decimal_places=5)
    unidad = models.CharField(max_length=5)
    cantidad_maxima = models.DecimalField(max_digits=15, decimal_places=5, default=0)

    class Meta:
        managed = False
        db_table = 'almacen_inventarioexistencia'


class ProductoSaldo(models.Model):
    id = models.BigIntegerField(primary_key=True)
    producto = models.ForeignKey(Producto, on_delete=models.DO_NOTHING)
    unidad = models.ForeignKey(UnidadMedida, on_delete=models.DO_NOTHING)
    existencia = models.DecimalField(max_digits=15, decimal_places=5)

    class Meta:
        managed = False
        db_table = 'almacen_productosaldo'


class ProductoConsolidado(models.Model):
    id = models.BigIntegerField(primary_key=True)
    producto = models.ForeignKey(Producto, on_delete=models.DO_NOTHING)
    unidad = models.ForeignKey(UnidadMedida, on_delete=models.DO_NOTHING)
    entradas = models.DecimalField(max_digits=15, decimal_places=5)
    salidas = models.DecimalField(max_digits=15, decimal_places=5)
    saldo = models.DecimalField(max_digits=15, decimal_places=5)

    class Meta:
        managed = False
        db_table = 'almacen_productoconsolidado'


class InventarioResumen(models.Model):
    id = models.BigIntegerField(primary_key=True)
    producto = models.ForeignKey(Producto, on_delete=models.DO_NOTHING)
    existencia = models.DecimalField(max_digits=15, decimal_places=5)
    # pieza = models.DecimalField(max_digits=15, decimal_places=5)

    class Meta:
        managed = False
        db_table = 'almacen_inventarioresumen'
