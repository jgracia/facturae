from django.db import models
from django.contrib.auth.models import User
from apps.administracion.models import Empresa

# Create your models here.


class UnidadMedida(models.Model):
    TIPOS = (
        ('TIEMPO', 'UNIDADES DE TIEMPO'),
        ('LONGITUD', 'UNIDADES DE LONGITUD'),
        ('MASA', 'UNIDADES DE MASA'),
        ('VOLUMEN', 'UNIDADES DE VOLUMEN'),
        ('OTRAS', 'OTRAS UNIDADES'),
    )
    unidad_medida_id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    empresa = models.ForeignKey(Empresa, null=False, blank=False, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=8, choices=TIPOS, default='OTRAS',)
    usuario_creador = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    nombre = models.CharField(max_length=32, unique=True)
    abreviatura = models.CharField(max_length=5, unique=True)

    def __str__(self):
        return self.nombre

    class Meta:  # nombre en plural
        verbose_name_plural = 'unidades de medida'
