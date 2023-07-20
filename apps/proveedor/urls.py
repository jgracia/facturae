from django.urls import path
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from . import views

app_name = 'proveedor'
urlpatterns = [
    path('', login_required(views.ProveedoresIndexView.as_view()), name='listado_proveedores'),
    path('crear_proveedor/', login_required(views.CrearProveedor.as_view()), name='crear_proveedor'),
    path('editar_proveedor/<int:pk>',
         login_required(views.EditarProveedor.as_view()), name='editar_proveedor'),
    path('detalle_proveedor/<int:pk>',
         login_required(views.DetalleProveedor.as_view()), name='detalle_proveedor'),
    path('eliminar_proveedor/<int:pk>',
         login_required(views.EliminarProveedor.as_view()), name='eliminar_proveedor'),

    # DESACTIVADO PROVEEDOR DESDE PRODUCTOS
    # path('ajax/agregar_proveedor/', login_required(views.ajaxCrearProveedorModal),
    #     name='ajax_crear_proveedor_modal'),
]
