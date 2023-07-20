from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.administracion.models import Empresa

# Create your models here.


class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    biografia = models.TextField(max_length=500, null=True, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    papel = models.CharField(max_length=10,
                             choices=(
                                 ('VISITOR', 'Visitante'),
                                 ('EMPLOYEE', 'Empleado'),
                                 ('ACCOUNTANT', 'Contador'),
                                 ('SUPERVISOR', 'Supervisor'),
                             ), default='VISITOR'
                             )
    foto = models.ImageField('Foto de perfil',
                             upload_to='avatars/', blank=True, null=True, default='avatars/user.png')


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(usuario=instance)
    instance.perfil.save()


class Turno(models.Model):
    turno_id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    usuario_creador = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    importe_apertura = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    concepto_apertura = models.CharField(max_length=128, null=True, blank=True)
    closed_at = models.DateTimeField(auto_now=True)
    importe_cierre = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    concepto_cierre = models.CharField(max_length=128, null=True, blank=True)
    activo = models.BooleanField(default=True)
    # observaciones = models.CharField(max_length=256, null=True,
    #                                 blank=True, help_text='Observaciones')
    empresa = models.ForeignKey(Empresa, null=False, blank=False, on_delete=models.CASCADE)
