from django.db import models
from django.contrib.auth.models import User
from apps.sri.models import SriTarifaIVA, SriTarifaICE
from apps.unidadmedida.models import UnidadMedida
from apps.administracion.models import Empresa

# Create your models here.

"""
class UnidadMedida(models.Model):
    medida_id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    usuario_creador = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    nombre = models.CharField(max_length=32, unique=True)
    abreviatura = models.CharField(max_length=5, unique=True)

    def __str__(self):
        return self.nombre
"""


class Servicio(models.Model):
    servicio_id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    empresa = models.ForeignKey(Empresa, null=False, blank=False, on_delete=models.CASCADE)
    usuario_creador = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    es_deducible = models.BooleanField(default=False)
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=500)
    precio = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    descuento = models.DecimalField(max_digits=15, decimal_places=5,
                                    default=0, help_text='Porcentaje descuento')
    iva = models.ForeignKey(SriTarifaIVA, null=True, blank=True, on_delete=models.SET_NULL)
    ice = models.ForeignKey(SriTarifaICE, null=True, blank=True, on_delete=models.SET_NULL)
    unidad_medida = models.ForeignKey(
        UnidadMedida, null=True, blank=True, on_delete=models.SET_NULL)
