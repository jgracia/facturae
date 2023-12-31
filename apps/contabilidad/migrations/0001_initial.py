# Generated by Django 2.2.8 on 2020-01-17 01:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cliente', '0004_clienteresumen'),
        ('administracion', '0004_secuencia'),
        ('usuario', '0002_turno'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('proveedor', '0004_proveedorresumen'),
        ('sri', '0009_sriformapago'),
    ]

    operations = [
        migrations.CreateModel(
            name='EstadoPago',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('update_at', models.DateTimeField(auto_now=True)),
                ('activo', models.BooleanField(default=True)),
                ('situacion', models.CharField(max_length=16, unique=True)),
                ('usuario_creador', models.ForeignKey(blank=True, null=True,
                                                      on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='FormaPago',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('update_at', models.DateTimeField(auto_now=True)),
                ('activo', models.BooleanField(default=True)),
                ('sri_codigo', models.CharField(max_length=10)),
                ('descripcion', models.CharField(max_length=50, unique=True)),
                ('codigo', models.CharField(max_length=2, unique=True)),
                ('usuario_creador', models.ForeignKey(blank=True, null=True,
                                                      on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Pago',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('update_at', models.DateTimeField(auto_now=True)),
                ('tipo_flujo', models.CharField(choices=[
                 ('D', 'Debe'), ('H', 'Haber')], max_length=1)),
                ('referencia', models.CharField(blank=True, max_length=32, null=True)),
                ('orden_id', models.IntegerField(default=0, help_text='factura_id, orden_id, etc..')),
                ('numero_comprobante', models.CharField(blank=True, max_length=17, null=True)),
                ('importe', models.DecimalField(decimal_places=5, default=0, max_digits=15)),
                ('importe_recibido', models.DecimalField(decimal_places=5, default=0, max_digits=15)),
                ('valor_retenido', models.DecimalField(decimal_places=5, default=0, max_digits=15)),
                ('app_forma_pago', models.ForeignKey(blank=True, null=True,
                                                     on_delete=django.db.models.deletion.SET_NULL, to='contabilidad.FormaPago')),
                ('cliente', models.ForeignKey(blank=True, null=True,
                                              on_delete=django.db.models.deletion.SET_NULL, to='cliente.Cliente')),
                ('empresa', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, to='administracion.Empresa')),
                ('estado', models.ForeignKey(blank=True, null=True,
                                             on_delete=django.db.models.deletion.SET_NULL, to='contabilidad.EstadoPago')),
                ('proveedor', models.ForeignKey(blank=True, null=True,
                                                on_delete=django.db.models.deletion.SET_NULL, to='proveedor.Proveedor')),
                ('sri_forma_pago', models.ForeignKey(blank=True, null=True,
                                                     on_delete=django.db.models.deletion.SET_NULL, to='sri.SriFormaPago')),
                ('sri_tipo_moneda', models.ForeignKey(blank=True, null=True,
                                                      on_delete=django.db.models.deletion.SET_NULL, to='sri.SriTipoMoneda')),
                ('turno', models.ForeignKey(blank=True, null=True,
                                            on_delete=django.db.models.deletion.SET_NULL, to='usuario.Turno')),
                ('usuario', models.ForeignKey(blank=True, null=True,
                                              on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
