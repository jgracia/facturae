from django import template

import math
from apps.contabilidad.models import Pago, PagoCredito
from django.db.models import Sum
from django.db.models.functions import Coalesce
import datetime

register = template.Library()


def promedio(dividendo, divisor):
    if divisor > 0:
        return dividendo / divisor
    else:
        return 0


register.filter('promedio', promedio)


def ventas_hoy(user_pk):

    today = datetime.date.today()

    total_ventas = Pago.objects.filter(
        usuario_id=user_pk,
        created_at__date=today,
        referencia='Venta').aggregate(
        total=Coalesce(Sum('importe'), 0))['total']

    return total_ventas


register.filter('ventas_hoy', ventas_hoy)


@register.simple_tag
def all_notifications(current_company_id):

    today = datetime.date.today()
    notifications_obj = PagoCredito.objects.filter(
        saldo__gt=0,
        estado__lt=3,
        vence__lte=today, empresa_id=current_company_id).order_by('vence', '-estado')[:5]  # filtrar primeros 10 registros
    return notifications_obj
