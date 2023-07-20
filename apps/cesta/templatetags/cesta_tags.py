from django import template

from apps.cesta.models import Cesta
from apps.cesta.settings import CESTA_TEMPLATE_TAG_NAME

register = template.Library()


def get_cesta(context, clave_apli=None, empresa_id=None):

    # user_basket = Cesta.objects.filter(
    #    usuario=request.user, clave_apli='apli_compra', clave_pers='Proveedor-1')[0]

    request = context['request']
    user_basket, status = Cesta.objects.get_or_create(
        usuario=request.user, clave_apli=clave_apli, empresa_id=empresa_id)
    return user_basket


register.simple_tag(takes_context=True, name=CESTA_TEMPLATE_TAG_NAME)(get_cesta)
