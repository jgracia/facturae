from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from apps.sri.models import SriTipoComprobante

# Create your models here.


class Empresa(models.Model):
    TYPE_CHOICES = (
        (1, 'PRUEBAS'),
        (2, 'PRODUCCIÓN'),
    )
    # METODO_COSTO = (
    #('PEPS', 'PRIMERAS ENTRADAS, PRIMERAS SALIDAS', {'disabled': True}),
    #('UEPS', 'ÚLTIMAS ENTRADAS, PRIMERAS SALIDAS'),
    #    ('PROM', 'PROMEDIO PONDERADO'),
    # )
    empresa_id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    usuario_creador = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    factel = models.BooleanField(default=False)
    #razon_social = models.CharField(max_length=300, unique=True)
    razon_social = models.CharField(max_length=300)
    nombre_comercial = models.CharField(null=True, max_length=300)
    #ruc = models.CharField(max_length=15, unique=True)
    ruc = models.CharField(max_length=15)
    direccion_matriz = models.CharField(max_length=500)
    telefono = models.CharField(max_length=25, null=True, blank=True)
    pagina_web = models.CharField(max_length=300, null=True, blank=True)
    codigo_contribuyente_especial = models.CharField(max_length=10, null=True, blank=True)
    obligado_llevar_contabilidad = models.BooleanField(default=False)
    nombre_logo = models.CharField(max_length=100, null=True, blank=True)
    tipo_ambiente = models.PositiveSmallIntegerField(choices=TYPE_CHOICES, null=True, blank=True)
    nombre_token = models.CharField(max_length=100, null=True, blank=True)
    pin_token = models.CharField(max_length=255, null=True, blank=True)
    smtp_servidor = models.CharField(max_length=255, null=True, blank=True)
    smtp_puerto = models.IntegerField(default=0, null=True, blank=True)
    smtp_usuario = models.CharField(max_length=255, null=True, blank=True)
    smtp_clave = models.CharField(max_length=255, null=True, blank=True)
    smtp_seguridad = models.BooleanField(null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    # metodo_costo = models.CharField(max_length=5, choices=METODO_COSTO,
    #                                blank=True, null=True, default='PEPS')
    #impresora_nombre = models.CharField(max_length=64, null=True, blank=True)
    #factura_total_filas = models.IntegerField(default=0, help_text="Filas por factura")
    #factura_total_copias = models.IntegerField(default=0)
    #factura_margen_superior = models.IntegerField(default=0)
    #factura_margen_inferior = models.IntegerField(default=0)

    def __str__(self):
        return self.razon_social + ' - ' + self.ruc

    def get_numero_filas(self):
        return self.factura_numero_filas

    class Meta:
        unique_together = (("razon_social", "ruc"),)


class EntidadFinanciera(models.Model):
    entidad_id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    usuario_creador = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre


class TarjetaBancaria(models.Model):
    tarjeta_id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    usuario_creador = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre


class Secuencia(models.Model):
    TYPE_PRINTERS = (
        (1, 'Impresoras de tickets (POS) Matricial'),
        (2, 'Impresoras de tickets (POS) Térmica'),
        (3, 'Impresora de Matriz de Puntos'),
        (4, 'Impresora de chorro de tinta'),
        (5, 'Impresora Láser'),
    )
    TYPE_PROTOCOLS = (
        (1, 'Ethernet'),
        (2, 'Wi-Fi'),
        (3, 'USB'),
    )
    secuencia_id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    empresa = models.ForeignKey(Empresa, null=False, blank=False, on_delete=models.CASCADE)
    sri_tipo_comprobante = models.ForeignKey(
        SriTipoComprobante, null=True, blank=True, on_delete=models.SET_NULL)
    usuario_creador = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    punto_establecimiento = models.CharField(max_length=3)
    punto_emision = models.CharField(max_length=3)
    ultima_secuencia = models.IntegerField(default=0)
    direccion_establecimiento = models.TextField(null=True, blank=True)

    comprobante_total_filas = models.IntegerField(default=0, help_text="Filas por comprobante")
    comprobante_fisico_ancho = models.IntegerField(default=0)
    comprobante_fisico_alto = models.IntegerField(default=0)
    comprobante_fisico_margen_superior = models.IntegerField(default=0)
    comprobante_fisico_margen_inferior = models.IntegerField(default=0)
    comprobante_fisico_total_copias = models.IntegerField(
        default=1, validators=[MinValueValidator(1)])

    comprobante_fisico_tipo_impresora = models.PositiveSmallIntegerField(
        choices=TYPE_PRINTERS, null=True, blank=True)
    comprobante_fisico_tipo_protocolo = models.PositiveSmallIntegerField(
        choices=TYPE_PROTOCOLS, null=True, blank=True)
    comprobante_fisico_nombre_impresora = models.CharField(
        max_length=64, null=True, blank=True, help_text="IP, nombre impresora")

    def __str__(self):
        return self.empresa.razon_social
