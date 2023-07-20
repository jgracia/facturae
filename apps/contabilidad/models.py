from django.db import models
from django.contrib.auth.models import User

from apps.administracion.models import EntidadFinanciera, TarjetaBancaria
from apps.sri.models import SriFormaPago, SriTipoMoneda
from apps.usuario.models import Turno
from apps.cliente.models import Cliente
from apps.proveedor.models import Proveedor
from apps.administracion.models import Empresa

from mptt.models import MPTTModel, TreeForeignKey

#from django.core.urlresolvers import reverse
from django.urls import reverse
from django_extensions.db.fields import AutoSlugField
import mptt

#from urlparse import urljoin
from urllib.parse import urljoin

# Create your models here.


class FormaPago(models.Model):
    usuario_creador = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    sri_codigo = models.CharField(max_length=10)
    descripcion = models.CharField(max_length=50, unique=True)
    codigo = models.CharField(max_length=2, unique=True)

    def __str__(self):
        return self.descripcion


class EstadoPago(models.Model):
    usuario_creador = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    situacion = models.CharField(max_length=16, unique=True)


class Pago(models.Model):
    turno = models.ForeignKey(
        Turno, null=True, blank=True, on_delete=models.SET_NULL)
    usuario = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    app_forma_pago = models.ForeignKey(
        FormaPago, null=True, blank=True, on_delete=models.SET_NULL)
    sri_forma_pago = models.ForeignKey(
        SriFormaPago, null=True, blank=True, on_delete=models.SET_NULL)
    sri_tipo_moneda = models.ForeignKey(
        SriTipoMoneda, null=True, blank=True, on_delete=models.SET_NULL)
    tipo_flujo = models.CharField(max_length=1,
                                  choices=(
                                      ('D', 'Debe'),
                                      ('H', 'Haber')
                                  )
                                  )
    referencia = models.CharField(max_length=32, null=True, blank=True)
    estado = models.ForeignKey(
        EstadoPago, null=True, blank=True, on_delete=models.SET_NULL)
    orden_id = models.IntegerField(
        default=0, help_text="factura_id, orden_id, etc..")
    numero_comprobante = models.CharField(max_length=17, null=True, blank=True)
    cliente = models.ForeignKey(
        Cliente, null=True, blank=True, on_delete=models.SET_NULL)
    proveedor = models.ForeignKey(
        Proveedor, null=True, blank=True, on_delete=models.SET_NULL)
    #compra = models.ForeignKey(Orden, null=True, blank=True, on_delete=models.SET_NULL)
    #venta = models.ForeignKey(Factura, null=True, blank=True, on_delete=models.SET_NULL)
    #proforma = models.ForeignKey(Proforma, null=True, blank=True, on_delete=models.SET_NULL)
    importe = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    importe_recibido = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    valor_retenido = models.DecimalField(
        max_digits=15, decimal_places=5, default=0)
    empresa = models.ForeignKey(
        Empresa, null=False, blank=False, on_delete=models.CASCADE)


class EstadoCheque(models.Model):
    usuario_creador = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    situacion = models.CharField(max_length=16, unique=True)


class PagoCheque(models.Model):
    pago = models.ForeignKey(Pago, null=False,
                             blank=False, on_delete=models.CASCADE)
    banco = models.ForeignKey(
        EntidadFinanciera, null=True, blank=True, on_delete=models.SET_NULL)
    cuenta_nro = models.CharField(max_length=16, null=True, blank=True)
    cheque_nro = models.CharField(max_length=16, null=True, blank=True)
    #titular = models.CharField(max_length=64, null=True, blank=True)
    fecha_cheq = models.DateField()
    estado = models.ForeignKey(
        EstadoCheque, null=True, blank=True, on_delete=models.SET_NULL)
    monto = models.DecimalField(max_digits=15, decimal_places=5, default=0)


class PagoTransferencia(models.Model):
    pago = models.ForeignKey(Pago, null=False,
                             blank=False, on_delete=models.CASCADE)
    banco_origen = models.ForeignKey(
        EntidadFinanciera, null=True, blank=True, on_delete=models.SET_NULL, related_name='banco_origen')
    cta_origen = models.CharField(max_length=16, null=True, blank=True)
    #titular = models.CharField(max_length=64, null=True, blank=True)
    banco_destino = models.ForeignKey(
        EntidadFinanciera, null=True, blank=True, on_delete=models.SET_NULL, related_name='banco_destino')
    cta_destino = models.CharField(max_length=16, null=True, blank=True)
    fecha_transf = models.DateField()
    monto = models.DecimalField(max_digits=15, decimal_places=5, default=0)


class PagoTarjeta(models.Model):
    pago = models.ForeignKey(Pago, null=False,
                             blank=False, on_delete=models.CASCADE)
    #banco = models.ForeignKey(EntidadFinanciera, null=True, blank=True, on_delete=models.SET_NULL)
    tarjeta = models.ForeignKey(
        TarjetaBancaria, null=True, blank=True, on_delete=models.SET_NULL)
    tipo_tarjeta = models.CharField(max_length=2,
                                    choices=(
                                        ('TD', 'Tarjeta Débito'),
                                        ('TC', 'Tarjeta Crédito')
                                    )
                                    )
    #titular = models.CharField(max_length=64, null=True, blank=True)
    tarjeta_nro = models.CharField(max_length=16, null=True, blank=True)
    #expira = models.CharField(max_length=7, null=True, blank=True)
    # modalidad = models.CharField(max_length=10,
    #                             choices=(
    #                                 ('Corriente', 'Pago Corriente'),
    #                                 ('Diferido', 'Pago Diferido')
    #                             )
    #                             )
    #plazo = models.IntegerField(default=0)
    vaucher = models.CharField(max_length=16, null=True, blank=True)
    monto = models.DecimalField(max_digits=15, decimal_places=5, default=0)


class EstadoCredito(models.Model):
    usuario_creador = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    situacion = models.CharField(max_length=16, unique=True)


class PagoCredito(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    pago = models.ForeignKey(Pago, null=False,
                             blank=False, on_delete=models.CASCADE)
    valor_credito = models.DecimalField(
        max_digits=15, decimal_places=5, default=0)
    plazo = models.IntegerField(default=0)
    unidad_tiempo = models.CharField(max_length=1,
                                     choices=(
                                         ('D', 'DÍAS'),
                                         ('M', 'MESES'),
                                         ('A', 'AÑOS')
                                     )
                                     )
    num_cuotas = models.IntegerField(default=0)
    tasa_interes = models.DecimalField(
        max_digits=15, decimal_places=5, default=0)
    cuota_nro = models.IntegerField(default=0)
    vence = models.DateField()
    estado = models.ForeignKey(
        EstadoCredito, null=True, blank=True, on_delete=models.SET_NULL)
    valor_cuota = models.DecimalField(
        max_digits=15, decimal_places=5, default=0)
    valor_retenido = models.DecimalField(
        max_digits=15, decimal_places=5, default=0)
    abono = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    saldo = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    empresa = models.ForeignKey(
        Empresa, null=False, blank=False, on_delete=models.CASCADE)


class PlanCuenta(MPTTModel):
    # NO ID AUTOMÁTICO
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    #codigo = models.CharField(max_length=10, unique=True)
    #codigo = models.CharField(max_length=12, unique=True, primary_key=True)
    #nombre = models.CharField(max_length=128, unique=True)
    codigo = models.CharField(max_length=12)
    nombre = models.CharField(max_length=128)
    clasificacion = models.CharField(max_length=24,
                                     choices=(
                                         ('ACTIVO', 'ACTIVO'),
                                         ('PASIVO', 'PASIVO'),
                                         ('PATRIMONIO', 'PATRIMONIO'),
                                         ('INGRESOS', 'INGRESOS'),
                                         ('GASTOS', 'GASTOS'),
                                         ('COSTOS', 'COSTOS'),
                                         ('DE ORDEN', 'DE ORDEN')
                                     )
                                     )
    tipo = models.CharField(max_length=10,
                            choices=(
                                ('CLASE', 'CLASE'),
                                ('GRUPO', 'GRUPO'),
                                ('CUENTA', 'CUENTA'),
                                ('SUBCUENTA', 'SUBCUENTA'),
                                ('AUXILIAR', 'AUXILIAR'),
                            )
                            )
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True,
                            blank=True, related_name='children')
    usuario_creador = models.ForeignKey(
        User, null=False, blank=False, on_delete=models.CASCADE)
    empresa = models.ForeignKey(
        Empresa, null=False, blank=False, on_delete=models.CASCADE)

    # UNIQUE TOGHETER, porque no puede repetirse la cuenta en el plan
    # class Meta:
    #    unique_together = (("codigo", "nombre", "empresa"),)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['codigo', 'nombre', 'empresa'], name='cuenta_unica')
        ]

    def __str__(self):
        return self.nombre

    def getFullName(self):
        return self.codigo + ", " + self.nombre

    class MPTTMeta:
        order_insertion_by = ['codigo']


class PeriodoContable(models.Model):
    usuario_creador = models.ForeignKey(
        User, null=False, blank=False, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    descripcion = models.CharField(max_length=128)
    fecha_inicio = models.DateField()
    fecha_cierre = models.DateField(null=True)
    activo = models.BooleanField(default=True)
    empresa = models.ForeignKey(
        Empresa, null=False, blank=False, on_delete=models.CASCADE)

    # UNIQUE TOGHETER, porque no puede repetirse la descripción en la empresa
    class Meta:
        unique_together = (("descripcion", "empresa"),)


class AsientoContable(models.Model):
    numero_asiento = models.PositiveIntegerField(default=0, db_index=True)
    fecha = models.DateField()
    # parcial = models.ManyToManyField(Cuenta, through='AsientoParcialDetalle',
    #                                 related_name='CuentasParcial')
    debe = models.ManyToManyField(PlanCuenta, through='AsientoDebeDetalle',
                                  related_name='CuentasDebe')
    haber = models.ManyToManyField(
        PlanCuenta, through='AsientoHaberDetalle', related_name='CuentasHaber')
    glosa = models.CharField(max_length=100, null=True)
    comprobante = models.CharField(max_length=24, null=True)
    usuario_creador = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL)
    empresa = models.ForeignKey(
        Empresa, null=False, blank=False, on_delete=models.CASCADE)
    periodo = models.ForeignKey(
        PeriodoContable, null=False, blank=False, on_delete=models.CASCADE)

    def __str__(self):
        try:
            result = str(self.fecha) + ' - #:' + \
                str(self.id) + ' - ' + self.glosa
        except self.glosa:
            result = str(self.fecha) + ' - #:' + str(self.id)
        return result


class AsientoParcialDetalle(models.Model):
    asiento = models.ForeignKey(
        AsientoContable, null=False, blank=False, on_delete=models.CASCADE)
    cuenta = models.ForeignKey(
        PlanCuenta, null=False, blank=False, on_delete=models.CASCADE)
    movimiento = models.CharField(max_length=1)
    monto = models.FloatField()
    # UNIQUE TOGHETER, porque no puede repetirse la cuenta en el asiento
    # class Meta:
    #     unique_together = (("asiento", "cuenta"),)

    def __str__(self):
        return str(self.asiento) + ' - ' + str(self.id)


class AsientoDebeDetalle(models.Model):
    asiento = models.ForeignKey(
        AsientoContable, null=False, blank=False, on_delete=models.CASCADE)
    cuenta = models.ForeignKey(
        PlanCuenta, null=False, blank=False, on_delete=models.CASCADE)
    monto = models.FloatField()
    # UNIQUE TOGHETER, porque no puede repetirse la cuenta en el asiento
    # class Meta:
    #     unique_together = (("asiento", "cuenta"),)

    def __str__(self):
        return str(self.asiento) + ' - ' + str(self.id)


class AsientoHaberDetalle(models.Model):
    asiento = models.ForeignKey(
        AsientoContable, null=False, blank=False, on_delete=models.CASCADE)
    cuenta = models.ForeignKey(
        PlanCuenta, null=False, blank=False, on_delete=models.CASCADE)
    monto = models.FloatField()
    # UNIQUE TOGHETER, porque no puede repetirse la cuenta en el asiento
    # class Meta:
    #     unique_together = (("asiento", "cuenta"),)

    def __str__(self):
        return str(self.asiento) + ' - ' + str(self.id)


"""class CuentaEnlace(models.Model):
    cuenta = models.ForeignKey(Cuenta, null=True, blank=True, on_delete=models.SET_NULL)
    descripcion = models.CharField(max_length=128, unique=True)
    debito = models.BooleanField(default=False)
    credito = models.BooleanField(default=False)"""


class AsientoAutomatico(models.Model):
    # codigo = models.CharField(max_length=10, primary_key=True)
    codigo_enlace = models.CharField(max_length=32)
    grupo_asiento = models.CharField(max_length=64, null=False, blank=False)
    descripcion = models.CharField(max_length=128, null=False, blank=False)
    cuenta = models.ForeignKey(
        PlanCuenta, null=True, blank=True, on_delete=models.SET_NULL)
    #glosa = models.CharField(max_length=100, null=True)
    debito = models.BooleanField(default=False)
    credito = models.BooleanField(default=False)
    usuario_creador = models.ForeignKey(
        User, null=False, blank=False, on_delete=models.CASCADE)
    empresa = models.ForeignKey(
        Empresa, null=False, blank=False, on_delete=models.CASCADE)

    # UNIQUE TOGHETER, porque no puede repetirse la cuenta en el plan
    # class Meta:
    #    unique_together = (("codigo", "nombre", "empresa"),)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['codigo_enlace', 'empresa'], name='asiento_unico')
        ]


'''class PlanCuenta(models.Model):
    plan_cuenta_id = models.AutoField(
        auto_created=True, primary_key=True, serialize=False)
    usuario_creador = models.ForeignKey(
        User, null=False, blank=False, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    codigo = models.CharField(max_length=7, unique=True)
    descripcion = models.CharField(max_length=128, unique=True)
    clasificacion = models.CharField(max_length=10,
                                     choices=(
                                         ('ACTIVO', 'ACTIVO'),
                                         ('PASIVO', 'PASIVO'),
                                         ('CAPITAL', 'CAPITAL'),
                                         ('VENTAS', 'VENTAS'),
                                         ('GASTOS', 'GASTOS')
                                     )
                                     )
    tipo = models.CharField(max_length=10,
                            choices=(
                                    ('DETALLE', 'Cuenta de Detalle'),
                                    ('GRUPO', 'Cuenta de Grupo'),
                            )
                            )'''


'''class LibroDiario(models.Model):
    libro_diario_id = models.AutoField(
        auto_created=True, primary_key=True, serialize=False)
    asiento = models.IntegerField(default=0)
    turno = models.ForeignKey(
        Turno, null=True, blank=True, on_delete=models.SET_NULL)
    usuario_creador = models.ForeignKey(
        User, null=False, blank=False, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    cuenta = models.ForeignKey(
        PlanCuenta, null=False, blank=False, on_delete=models.CASCADE)
    movimiento = models.CharField(max_length=1,
                                  choices=(
                                      ('D', 'Debe'),
                                      ('H', 'Haber')
                                  )
                                  )
    importe = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    referencia = models.CharField(max_length=32, null=True, blank=True)'''


class CuentasLibroMayor(models.Model):
    id = models.BigIntegerField(primary_key=True)
    cuenta = models.ForeignKey(PlanCuenta, on_delete=models.DO_NOTHING)
    empresa = models.ForeignKey(Empresa, on_delete=models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'contabilidad_cuentaslibromayor'


class CuentasLibroDiario(models.Model):
    id = models.BigIntegerField(primary_key=True)
    tipo_movimiento = models.CharField(max_length=1)
    asiento = models.ForeignKey(AsientoContable, on_delete=models.DO_NOTHING)
    debe = models.ForeignKey(AsientoDebeDetalle, on_delete=models.DO_NOTHING)
    haber = models.ForeignKey(AsientoHaberDetalle, on_delete=models.DO_NOTHING)
    empresa = models.ForeignKey(Empresa, on_delete=models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'contabilidad_cuentaslibrodiario'


class BalanceComprobacion(models.Model):
    id = models.BigIntegerField(primary_key=True)
    cuenta = models.ForeignKey(PlanCuenta, on_delete=models.DO_NOTHING)
    saldo_deudor = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    saldo_acreedor = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    empresa = models.ForeignKey(Empresa, on_delete=models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'contabilidad_balancecomprobacion'
