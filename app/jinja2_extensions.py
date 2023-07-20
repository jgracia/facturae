from django import template
from apps.contabilidad.model import PlanCuenta

register = template.Library()


@register.simple_tag()
def my_custom_tag():
    things = PlanCuenta.objects.all()
    return {'things': things}
