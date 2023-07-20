from django.contrib import admin

# Register your models here.

from apps.compra.models import OrdenCompraEstado, OrdenCompra, \
    OrdenCompraDetalle

admin.site.register(OrdenCompraEstado)
admin.site.register(OrdenCompra)
admin.site.register(OrdenCompraDetalle)
