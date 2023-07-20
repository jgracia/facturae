from django.contrib import admin

from .models import EntidadFinanciera, TarjetaBancaria, Empresa, \
    Secuencia

# Register your models here.

admin.site.register(EntidadFinanciera)
admin.site.register(TarjetaBancaria)
admin.site.register(Empresa)
admin.site.register(Secuencia)
