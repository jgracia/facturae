from django.contrib import admin

# Register your models here.

from .models import FacturaEstado, Factura, FacturaDetalle, \
    FacturaRetencion

admin.site.register(FacturaEstado)
admin.site.register(Factura)
admin.site.register(FacturaDetalle)
admin.site.register(FacturaRetencion)
