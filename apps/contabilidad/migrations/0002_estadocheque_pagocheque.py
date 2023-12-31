# Generated by Django 2.2.8 on 2019-12-26 05:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contabilidad', '0001_initial'),
        ('administracion', '0004_secuencia'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EstadoCheque',
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
            name='PagoCheque',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('cuenta_nro', models.CharField(blank=True, max_length=16, null=True)),
                ('cheque_nro', models.CharField(blank=True, max_length=16, null=True)),
                ('fecha_cheq', models.DateField()),
                ('monto', models.DecimalField(decimal_places=5, default=0, max_digits=15)),
                ('banco', models.ForeignKey(blank=True, null=True,
                                            on_delete=django.db.models.deletion.SET_NULL, to='administracion.EntidadFinanciera')),
                ('estado', models.ForeignKey(blank=True, null=True,
                                             on_delete=django.db.models.deletion.SET_NULL, to='contabilidad.EstadoCheque')),
                ('pago', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                           to='contabilidad.Pago')),
            ],
        ),
    ]
