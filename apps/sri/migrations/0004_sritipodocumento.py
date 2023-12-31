# Generated by Django 2.2.8 on 2019-12-25 22:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sri', '0003_sritipoimpuesto'),
    ]

    operations = [
        migrations.CreateModel(
            name='SriTipoDocumento',
            fields=[
                ('sri_tipo_documento_id', models.AutoField(
                    auto_created=True, primary_key=True, serialize=False)),
                ('tipo_impuesto', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('update_at', models.DateTimeField(auto_now=True)),
                ('activo', models.BooleanField(default=True)),
                ('codigo', models.CharField(max_length=3, unique=True)),
                ('descripcion', models.CharField(max_length=50, unique=True)),
                ('alias', models.CharField(max_length=5, unique=True)),
                ('usuario_creador', models.ForeignKey(blank=True, null=True,
                                                      on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
