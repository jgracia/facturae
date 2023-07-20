# Generated by Django 2.2.8 on 2019-12-25 22:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sri', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SriTipoIdentificacion',
            fields=[
                ('sri_tipo_identificacion_id', models.AutoField(
                    auto_created=True, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('update_at', models.DateTimeField(auto_now=True)),
                ('activo', models.BooleanField(default=True)),
                ('nombre', models.CharField(max_length=50, unique=True)),
                ('codigo', models.CharField(max_length=3, unique=True)),
                ('usuario_creador', models.ForeignKey(blank=True, null=True,
                                                      on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]