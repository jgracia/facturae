from django import template
from apps.contabilidad.models import PlanCuenta, AsientoDebeDetalle, \
    AsientoHaberDetalle
from django.db.models import CharField, Value
import json

register = template.Library()


@register.simple_tag
def define(val=None):
    return val


@register.simple_tag
def my_custom_tag():
    things = PlanCuenta.objects.all()
    return {'things': things}


@register.simple_tag
def filtro_data(qs, **kwargs):
    # print(kwargs)

    # print(qs.filter(cuenta_id=kwargs['cuenta_id']))
    # return qs.filter(cuenta_id=kwargs['cuenta_id'])
    return qs.filter(**kwargs)


@register.simple_tag
def get_cuentas_filtradas(company_id, cuenta_id):
    #print("company_id = %s" % (company_id))
    #print("cuenta_id = %s" % (cuenta_id))

    qs1 = AsientoDebeDetalle.objects.select_related(
        'asiento').filter(asiento__empresa_id=company_id).annotate(mycolumn=Value('D', output_field=CharField()))  # .order_by('cuenta_id', 'asiento_id')
    qs2 = AsientoHaberDetalle.objects.select_related(
        'asiento').filter(asiento__empresa_id=company_id).annotate(mycolumn=Value('H', output_field=CharField()))  # .order_by('cuenta_id', 'asiento_id')
    qs3 = qs1.union(qs2).order_by('cuenta_id', 'asiento_id')

    return qs3
