# Generated by Django 2.2.8 on 2019-12-26 06:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contabilidad', '0006_periodocontable'),
        ('administracion', '0004_secuencia'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AsientoContable',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_asiento', models.PositiveIntegerField(db_index=True, default=0)),
                ('fecha', models.DateField()),
                ('glosa', models.CharField(max_length=100, null=True)),
                ('comprobante', models.CharField(max_length=24, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='AsientoParcialDetalle',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('movimiento', models.CharField(max_length=1)),
                ('monto', models.FloatField()),
                ('asiento', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, to='contabilidad.AsientoContable')),
                ('cuenta', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, to='contabilidad.PlanCuenta')),
            ],
        ),
        migrations.CreateModel(
            name='AsientoDebeDetalle',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('monto', models.FloatField()),
                ('asiento', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, to='contabilidad.AsientoContable')),
                ('cuenta', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, to='contabilidad.PlanCuenta')),
            ],
        ),
        migrations.CreateModel(
            name='AsientoHaberDetalle',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('monto', models.FloatField()),
                ('asiento', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, to='contabilidad.AsientoContable')),
                ('cuenta', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, to='contabilidad.PlanCuenta')),
            ],
        ),
        migrations.AddField(
            model_name='asientocontable',
            name='debe',
            field=models.ManyToManyField(
                related_name='CuentasDebe', through='contabilidad.AsientoDebeDetalle', to='contabilidad.PlanCuenta'),
        ),
        migrations.AddField(
            model_name='asientocontable',
            name='empresa',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    to='administracion.Empresa'),
        ),
        migrations.AddField(
            model_name='asientocontable',
            name='haber',
            field=models.ManyToManyField(
                related_name='CuentasHaber', through='contabilidad.AsientoHaberDetalle', to='contabilidad.PlanCuenta'),
        ),
        migrations.AddField(
            model_name='asientocontable',
            name='periodo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    to='contabilidad.PeriodoContable'),
        ),
        migrations.AddField(
            model_name='asientocontable',
            name='usuario_creador',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]