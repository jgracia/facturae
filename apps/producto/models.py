from django.db import models
from django.contrib.auth.models import User
from apps.sri.models import SriTarifaIVA, SriTarifaICE, SriTarifaIRBPNR
from apps.unidadmedida.models import UnidadMedida
from apps.administracion.models import Empresa

# Create your models here.


class Categoria(models.Model):
    categoria_id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    empresa = models.ForeignKey(Empresa, null=False, blank=False, on_delete=models.CASCADE)
    usuario_creador = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=500)

    def __str__(self):
        return self.nombre


"""
class UnidadMedida(models.Model):
    unidad_id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    usuario_creador = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    nombre = models.CharField(max_length=32, unique=True)
    abreviatura = models.CharField(max_length=5, unique=True)

    def __str__(self):
        return self.nombre

    class Meta:  # nombre en plural
        verbose_name_plural = 'unidades'
"""

'''
class Precio(models.Model):
    precio = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    descuento = models.DecimalField(
        max_digits=15, decimal_places=5, default=0, help_text='Porcentaje')
    utilidad = models.DecimalField(
        max_digits=15, decimal_places=5, default=0, help_text='Porcentaje')
    precio_neto = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    es_principal = models.BooleanField(default=False, help_text='Precio principal')
'''


class Producto(models.Model):
    METODO_COSTO = (
        ('PEPS', 'PRIMERAS ENTRADAS, PRIMERAS SALIDAS'),
        ('UEPS', 'ÚLTIMAS ENTRADAS, PRIMERAS SALIDAS'),
        ('PROM', 'PROMEDIO PONDERADO'),
    )
    producto_id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    # proveedores = models.ManyToManyField(Proveedor)
    iva = models.ForeignKey(SriTarifaIVA, null=True, blank=True, on_delete=models.SET_NULL)
    ice = models.ForeignKey(SriTarifaICE, null=True, blank=True, on_delete=models.SET_NULL)
    irbpnr = models.ForeignKey(SriTarifaIRBPNR, null=True, blank=True, on_delete=models.SET_NULL)
    empresa = models.ForeignKey(Empresa, null=False, blank=False, on_delete=models.CASCADE)
    usuario_creador = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    codigo_principal = models.CharField(max_length=30, unique=True)
    codigo_auxiliar = models.CharField(max_length=25, null=True, blank=True)
    #es_servicio = models.BooleanField(default=False)
    es_deducible = models.BooleanField(default=False)
    marca = models.CharField(max_length=40, null=True, blank=True)
    modelo = models.CharField(max_length=40, null=True, blank=True)
    categoria = models.ForeignKey(Categoria, null=True, blank=True, on_delete=models.SET_NULL)
    # unidad_principal = models.ForeignKey(
    #    UnidadMedida, to_field='abreviatura', default='UN', null=False, blank=False, on_delete=models.CASCADE, related_name='unidad_principal')
    unidad_principal = models.ForeignKey(
        UnidadMedida, null=False, blank=False, on_delete=models.CASCADE, related_name='unidad_principal', default='1')
    unidad_secundaria = models.ForeignKey(
        UnidadMedida, null=True, blank=True, on_delete=models.SET_NULL, related_name='unidad_secundaria')
    unidad_equivalencia = models.IntegerField(default=1)
    # cantidad_unidad = models.IntegerField(default=0)
    nombre = models.CharField(max_length=128, unique=True)
    descripcion = models.TextField(null=True, blank=True, help_text='Observaciones')
    precio_costo = models.DecimalField(max_digits=15, decimal_places=5, default=0)

    '''
    utilidad = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    descuento = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    precio_venta = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    utilidad_minorista = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    descuento_minorista = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    precio_minorista = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    utilidad_mayorista = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    descuento_mayorista = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    precio_mayorista = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    '''

    precio_uno = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    descuento_uno = models.DecimalField(
        max_digits=15, decimal_places=5, default=0, help_text='Porcentaje')
    utilidad_uno = models.DecimalField(
        max_digits=15, decimal_places=5, default=0, help_text='Porcentaje')
    precio_neto_uno = models.DecimalField(max_digits=15, decimal_places=5, default=0)

    precio_dos = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    descuento_dos = models.DecimalField(
        max_digits=15, decimal_places=5, default=0, help_text='Porcentaje')
    utilidad_dos = models.DecimalField(
        max_digits=15, decimal_places=5, default=0, help_text='Porcentaje')
    precio_neto_dos = models.DecimalField(max_digits=15, decimal_places=5, default=0)

    precio_tres = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    descuento_tres = models.DecimalField(
        max_digits=15, decimal_places=5, default=0, help_text='Porcentaje')
    utilidad_tres = models.DecimalField(
        max_digits=15, decimal_places=5, default=0, help_text='Porcentaje')
    precio_neto_tres = models.DecimalField(max_digits=15, decimal_places=5, default=0)

    precio_cuatro = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    descuento_cuatro = models.DecimalField(
        max_digits=15, decimal_places=5, default=0, help_text='Porcentaje')
    utilidad_cuatro = models.DecimalField(
        max_digits=15, decimal_places=5, default=0, help_text='Porcentaje')
    precio_neto_cuatro = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    precio_principal = models.PositiveSmallIntegerField(
        choices=(
            (1, 'PRECIO 1'),
            (2, 'PRECIO 2'),
            (3, 'PRECIO 3'),
            (4, 'PRECIO 4')
        )
    )
    cantidad_minima = models.IntegerField(default=0)
    cantidad_maxima = models.IntegerField(default=0)
    cantidad_inicial = models.IntegerField(default=0)

    tiene_vencimiento = models.BooleanField(default=False)
    tiene_serie = models.BooleanField(default=False)

    # ubicacion = models.CharField(max_length=64, null=True, blank=True)
    # campo componente, relación uno a muchos (siguiente tabla)
    equivalente = models.ManyToManyField('self', blank=True)
    #vademecum = models.OneToOneField(Vademecum, null=True, blank=True, on_delete=models.CASCADE)
    foto = models.ImageField(upload_to="product-img/", null=True, blank=True,
                             default='product-img/no-img.jpg')
    metodo_costo = models.CharField(max_length=5, choices=METODO_COSTO,
                                    blank=True, null=True, default='PROM')

    # devuelve el atributo descripción del objeto
    def __str__(self):
        return '{}'.format(self.nombre)

    @property
    def image_url(self):
        if self.foto and hasattr(self.foto, 'url'):
            return self.foto.url

    @property
    def stock(self):
        from apps.almacen.models import Kardex, Almacen
        stock = 0
        almacenes = Almacen.objects.all()
        for almacen in almacenes:
            try:
                control_producto = Kardex.objects.filter(producto=self,
                                                         almacen=almacen).latest('created_at')
                stock = stock + control_producto.cantidad_total
            except Kardex.DoesNotExist:
                pass
        return stock

    class Meta:
        unique_together = (("codigo_principal", "nombre"),)


class Componente(models.Model):
    componente_id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.CharField(max_length=500)
    productos = models.ManyToManyField(Producto)

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ('nombre',)


"""
class SeguimientoLote(models.Model):
    seguimiento_lote_id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    usuario_creador = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    #compra = models.ForeignKey(OrdenCompra, null=True, blank=True, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, null=False, blank=False, on_delete=models.CASCADE)
    lote_numero = models.CharField(max_length=10, unique=True)
    descripcion = models.CharField(max_length=64)
    fecha_caducidad = models.DateField(default=datetime.date.today)
    cantidad = models.DecimalField(max_digits=25, decimal_places=5, default=0)
    history = HistoricalRecords()


class SeguimientoSerie(models.Model):
    seguimiento_serie_id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    usuario_creador = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    #compra = models.ForeignKey(OrdenCompra, null=True, blank=True, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, null=False, blank=False, on_delete=models.CASCADE)
    linea = models.IntegerField(default=1, help_text='Orden: 1, 2, 3, etc.')
    serie_numero = models.CharField(max_length=16, unique=True)
    history = HistoricalRecords()
"""
