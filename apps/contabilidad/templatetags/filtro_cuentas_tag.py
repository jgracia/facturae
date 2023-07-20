from django import template

register = template.Library()


@register.simple_tag()
def get_item_list(qs, **kwargs):
    print(kwargs)
    # return qs.filter(**kwargs)

    print(qs.objects.filter(cuenta_id=kwargs['cuenta_id']))
    return qs.objects.filter(cuenta_id=kwargs['cuenta_id'])


@register.filter()
def sumar(value, arg):
    if value == '':
        value = 0
    if arg == '':
        arg = 0
    return round(value, 2) + round(arg, 2)


@register.filter()
def restar(value, arg):
    if value == 0:
        value = 0
    if arg == 0:
        arg = 0
    return round(value, 2) - round(arg, 2)


@register.filter
def running_total0(compras_list):
    return sum(compra.valor_subtotal_0 for compra in compras_list)


@register.filter
def running_total12(compras_list):
    return sum(compra.valor_subtotal_12 for compra in compras_list)


@register.filter
def running_total_noiva(compras_list):
    return sum(compra.valor_subtotal_no_objeto_iva for compra in compras_list)


@register.filter
def running_total_iva(compras_list):
    return sum(compra.valor_iva for compra in compras_list)


@register.filter
def running_total_retef_base_imponible(retef_renta_list):
    return sum(retef['sum_base_imponible'] for retef in retef_renta_list)


@register.filter
def running_total_retef_valor_retenido(retef_list):
    return sum(retef['sum_valor_retenido'] for retef in retef_list)


@register.filter
def running_retef_renta_valor_retenido(retef_list):
    print("RECIBIDO...")
    print(retef_list)

    return sum(retef['sum_valor_retenido'] for retef in retef_list)
