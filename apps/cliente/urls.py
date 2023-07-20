from django.urls import path
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from . import views

app_name = 'cliente'
urlpatterns = [
    path('', login_required(views.ClientesIndexView.as_view()), name='listado_clientes'),
    path('crear_cliente/', login_required(views.CrearCliente.as_view()), name='crear_cliente'),
    path('editar_cliente/<int:pk>', login_required(views.EditarCliente.as_view()), name='editar_cliente'),
    path('detalle_cliente/<int:pk>', login_required(views.DetalleCliente.as_view()), name='detalle_cliente'),
    path('eliminar_cliente/<int:pk>',
         login_required(views.EliminarCliente.as_view()), name='eliminar_cliente'),
]
