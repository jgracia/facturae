from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'cesta'
urlpatterns = [
    path('vaciar_cesta/', login_required(views.vaciar_cesta_ajax), name='vaciar_cesta'),
    path('total_filas_cesta/', login_required(views.total_filas_cesta), name='total_filas_cesta'),
]
