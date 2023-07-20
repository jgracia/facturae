from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test


def employee_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='login'):
    '''
    Decorador para vistas que comprueba que el usuario que ha iniciado sesión es un empleado.
    redirige a la página de inicio de sesión si es necesario.
    '''
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.perfil.papel == 'EMPLOYEE',
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def supervisor_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='login'):
    '''
    Decorador para vistas que comprueba que el usuario que ha iniciado sesión es un supervisor.
    redirige a la página de inicio de sesión si es necesario.
    '''
    actual_decorator = user_passes_test(
        #lambda u: u.is_active and u.perfil.papel == 'SUPERVISOR',
        lambda u: u.is_active and u.is_staff,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
