# Generated by Django 2.2.8 on 2020-01-16 20:32

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sri', '0009_sriformapago'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Empresa',
            fields=[
                ('empresa_id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('update_at', models.DateTimeField(auto_now=True)),
                ('activo', models.BooleanField(default=True)),
                ('factel', models.BooleanField(default=False)),
                ('razon_social', models.CharField(max_length=300)),
                ('nombre_comercial', models.CharField(max_length=300, null=True)),
                ('ruc', models.CharField(max_length=15)),
                ('direccion_matriz', models.CharField(max_length=500)),
                ('telefono', models.CharField(blank=True, max_length=25, null=True)),
                ('pagina_web', models.CharField(blank=True, max_length=300, null=True)),
                ('codigo_contribuyente_especial', models.CharField(blank=True, max_length=10, null=True)),
                ('obligado_llevar_contabilidad', models.BooleanField(default=False)),
                ('nombre_logo', models.CharField(blank=True, max_length=100, null=True)),
                ('tipo_ambiente', models.PositiveSmallIntegerField(
                    blank=True, choices=[(1, 'PRUEBAS'), (2, 'PRODUCCIÓN')], null=True)),
                ('nombre_token', models.CharField(blank=True, max_length=100, null=True)),
                ('pin_token', models.CharField(blank=True, max_length=255, null=True)),
                ('smtp_servidor', models.CharField(blank=True, max_length=255, null=True)),
                ('smtp_puerto', models.IntegerField(blank=True, default=0, null=True)),
                ('smtp_usuario', models.CharField(blank=True, max_length=255, null=True)),
                ('smtp_clave', models.CharField(blank=True, max_length=255, null=True)),
                ('smtp_seguridad', models.BooleanField(blank=True, null=True)),
                ('email', models.CharField(blank=True, max_length=255, null=True)),
                ('usuario_creador', models.ForeignKey(blank=True, null=True,
                                                      on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('razon_social', 'ruc')},
            },
        ),
    ]