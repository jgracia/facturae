# Generated by Django 2.2.8 on 2019-12-25 23:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('usuario', '0001_initial'),
        ('administracion', '0004_secuencia'),
    ]

    operations = [
        migrations.CreateModel(
            name='Turno',
            fields=[
                ('turno_id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('importe_apertura', models.DecimalField(decimal_places=5, default=0, max_digits=15)),
                ('concepto_apertura', models.CharField(blank=True, max_length=128, null=True)),
                ('closed_at', models.DateTimeField(auto_now=True)),
                ('importe_cierre', models.DecimalField(decimal_places=5, default=0, max_digits=15)),
                ('concepto_cierre', models.CharField(blank=True, max_length=128, null=True)),
                ('activo', models.BooleanField(default=True)),
                ('empresa', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, to='administracion.Empresa')),
                ('usuario_creador', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]