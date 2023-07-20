from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class SriTipoComprobante(models.Model):
    sri_tipo_comprobante_id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    usuario_creador = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    codigo = models.CharField(max_length=10, unique=True)
    descripcion = models.CharField(max_length=50, unique=True)
    alias = models.CharField(max_length=5, unique=True)

    '''class Meta:
        constraints = [
            models.UniqueConstraint(fields=['codigo', 'descripcion',
                                            'alias'], name='tipo_comprobante_unico')
        ]'''

    def __str__(self):
        return self.descripcion

    def save(self):
        self.codigo = self.codigo.upper()
        self.descripcion = self.descripcion.upper()
        self.alias = self.alias.upper()
        super(SriTipoComprobante, self).save()


class SriTipoIdentificacion(models.Model):
    sri_tipo_identificacion_id = models.AutoField(
        auto_created=True, primary_key=True, serialize=False)
    usuario_creador = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    nombre = models.CharField(max_length=50, unique=True)
    codigo = models.CharField(max_length=3, unique=True)

    def __str__(self):
        return self.nombre


class SriTipoImpuesto(models.Model):
    sri_tipo_impuesto_id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    usuario_creador = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    tipo_impuesto = models.PositiveSmallIntegerField(
        choices=(
            (1, 'IVA'),
            (2, 'RENTA'),
        )
    )
    codigo = models.CharField(max_length=5, null=True, blank=True)
    descripcion = models.CharField(max_length=256, blank=True)
    porcentaje = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    porcentaje_retencion = models.DecimalField(max_digits=15, decimal_places=5, default=0)

    def __str__(self):
        return self.descripcion


class SriTipoDocumento(models.Model):
    sri_tipo_documento_id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    tipo_impuesto = models.IntegerField(default=0)
    usuario_creador = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    codigo = models.CharField(max_length=3, unique=True)
    descripcion = models.CharField(max_length=50, unique=True)
    alias = models.CharField(max_length=5, unique=True)

    def __str__(self):
        return self.descripcion


class SriTarifaIVA(models.Model):
    sri_tarifa_iva_id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    usuario_creador = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    #codigo_impuesto = models.IntegerField(default=0)
    #tipo_impuesto = models.IntegerField(default=0)
    codigo = models.CharField(max_length=10, unique=True)
    descripcion = models.CharField(max_length=50, blank=True)
    porcentaje = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    porcentaje_retencion = models.DecimalField(max_digits=15, decimal_places=5, default=0)

    def __str__(self):
        return self.descripcion


class SriTarifaICE(models.Model):
    sri_tarifa_ice_id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    usuario_creador = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    #codigo_impuesto = models.IntegerField(default=0)
    #tipo_impuesto = models.IntegerField(default=0)
    codigo = models.CharField(max_length=10, unique=True)
    descripcion = models.CharField(max_length=300, blank=True)
    porcentaje = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    porcentaje_retencion = models.DecimalField(max_digits=15, decimal_places=5, default=0)

    def __str__(self):
        return self.descripcion


class SriTarifaIRBPNR(models.Model):
    sri_tipo_impuesto_id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    usuario_creador = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    #codigo_impuesto = models.IntegerField(default=0)
    #tipo_impuesto = models.IntegerField(default=0)
    codigo = models.CharField(max_length=10, unique=True)
    descripcion = models.CharField(max_length=50, blank=True)
    porcentaje = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    porcentaje_retencion = models.DecimalField(max_digits=15, decimal_places=5, default=0)

    def __str__(self):
        return self.descripcion


class SriTipoMoneda(models.Model):
    sri_tipo_moneda_id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    usuario_creador = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    codigo = models.CharField(max_length=10, unique=True)
    descripcion = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.descripcion


class SriFormaPago(models.Model):
    sri_forma_pago_id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    usuario_creador = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    codigo = models.CharField(max_length=10, unique=True)
    descripcion = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.descripcion
