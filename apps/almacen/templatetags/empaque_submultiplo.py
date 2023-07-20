from django import template
from apps.producto.models import Producto

register = template.Library()


@register.filter()
def pieza_submultiplo(producto_id, stock):
    producto_obj = Producto.objects.get(pk=producto_id)
    equiv_undprim = producto_obj.unidad_equivalencia

    #import math
    #frac, whole = math.modf(stock)

    frac = stock - int(stock)
    whole = int(stock)
    pieza = round(frac * equiv_undprim)

    #print("ENTERO=%s" % whole)
    #print("FRACCION=%s" % frac)
    #print("PIEZAS=%s" % pieza)

    if whole > 0:
        if frac > 0:
            cadena = "%s %s + %s %s" % (whole, producto_obj.unidad_principal.abreviatura,
                                        pieza, producto_obj.unidad_secundaria.abreviatura)
        else:
            cadena = "%s %s" % (whole, producto_obj.unidad_principal.abreviatura)
    else:
        if frac > 0:
            cadena = "%s %s" % (pieza, producto_obj.unidad_secundaria.abreviatura)
        else:
            cadena = ''
    return cadena
