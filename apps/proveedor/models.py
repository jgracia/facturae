from django.db import models
from django.contrib.auth.models import User
from apps.sri.models import SriTipoIdentificacion
from apps.administracion.models import Empresa

# Create your models here.


class Proveedor(models.Model):
    proveedor_id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    identificacion_tipo = models.ForeignKey(
        SriTipoIdentificacion, null=True, blank=True, on_delete=models.SET_NULL)
    usuario_creador = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    nombre = models.CharField(max_length=255)
    identificacion = models.CharField(max_length=25, unique=True)
    obligado_contabilidad = models.BooleanField(default=False)
    #codigo_contribuyente_especial = models.CharField(max_length=10, blank=True)
    #es_rise = models.BooleanField(default=False)
    #es_cliente = models.BooleanField()
    #es_sujeto_retenido = models.BooleanField(default=False)
    #es_transportista = models.BooleanField(default=False)
    #es_destinatario = models.BooleanField(default=False)
    #placa = models.CharField(max_length=10, blank=True)
    direccion = models.CharField(max_length=255, null=True, blank=True)
    telefono = models.CharField(max_length=25, null=True, blank=True)
    extension = models.CharField(max_length=10, null=True, blank=True)
    celular = models.CharField(max_length=25, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    empresa = models.ForeignKey(Empresa, null=False, blank=False, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre


class ProveedorResumen(models.Model):
    proveedor_id = models.BigIntegerField(primary_key=True)
    #proveedor = models.ForeignKey(Proveedor, on_delete=models.DO_NOTHING)
    #id = models.IntegerField(default=0)
    nombre = models.CharField(max_length=255)
    identificacion = models.CharField(max_length=25, unique=True)
    direccion = models.CharField(max_length=255, blank=True)
    activo = models.BooleanField(default=True)
    saldo = models.DecimalField(max_digits=15, decimal_places=5, default=0)

    class Meta:
        managed = False
        db_table = 'proveedor_proveedorresumen'
