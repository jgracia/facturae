from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test


def turno_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='pago:apertura_caja'):
    '''
    Decorador para vistas que comprueba que el usuario logeado haya abierto turno,
    redirige a la página de turno si es necesario.
    '''
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_student,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
