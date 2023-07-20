from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'servicio'
urlpatterns = [
    path('', login_required(views.ListadoServicios.as_view()), name='listado_servicios'),
    path('crear_servicio/', login_required(views.CrearServicio.as_view()), name='crear_servicio'),
    path('editar_servicio/<int:pk>', login_required(views.EditarServicio.as_view()), name='editar_servicio'),
    path('detalle_servicio/<int:pk>',
         login_required(views.DetalleServicio.as_view()), name='detalle_servicio'),
    path('eliminar_servicio/<int:pk>',
         login_required(views.EliminarServicio.as_view()), name='eliminar_servicio'),

    path('ajax/busqueda_servicios/', login_required(views.busqueda_servicios), name='busqueda_servicios'),

    # rutas unidades
    #path('listado_unidades/', login_required(views.ListadoUnidades.as_view()), name='listado_unidades'),
    #path('crear_unidad/', login_required(views.CrearUnidad.as_view()), name='crear_unidad'),
    # path('modificar_unidad/<int:pk>',
    #     login_required(views.ModificarUnidad.as_view()), name='modificar_unidad'),
    #path('detalle_unidad/<int:pk>', login_required(views.DetalleUnidad.as_view()), name='detalle_unidad'),
    #path('eliminar_unidad/<int:pk>', login_required(views.EliminarUnidad.as_view()), name='eliminar_unidad'),
]
