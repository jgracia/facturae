from django.contrib import admin

from .models import SriTipoComprobante, SriTipoIdentificacion, SriTipoImpuesto, \
    SriTipoDocumento, SriTarifaIVA, SriTarifaICE, SriTarifaIRBPNR, \
    SriTipoMoneda, SriFormaPago

# Register your models here.

admin.site.register(SriTipoComprobante)
admin.site.register(SriTipoIdentificacion)
admin.site.register(SriTipoImpuesto)
admin.site.register(SriTipoDocumento)
admin.site.register(SriTarifaIVA)
admin.site.register(SriTarifaICE)
admin.site.register(SriTarifaIRBPNR)
admin.site.register(SriTipoMoneda)
admin.site.register(SriFormaPago)
