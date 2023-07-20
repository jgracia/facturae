from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'unidadmedida'
urlpatterns = [
    # rutas unidades
    path('unidades/', login_required(views.ListadoUnidades.as_view()), name='listado_unidades'),
    path('crear_unidad/', login_required(views.CrearUnidad.as_view()), name='crear_unidad'),
    path('modificar_unidad/<int:pk>',
         login_required(views.ModificarUnidad.as_view()), name='modificar_unidad'),
    path('detalle_unidad/<int:pk>', login_required(views.DetalleUnidad.as_view()), name='detalle_unidad'),
    path('eliminar_unidad/<int:pk>', login_required(views.EliminarUnidad.as_view()), name='eliminar_unidad'),

    # formularios modales
    path('unit/create/', login_required(views.unit_create), name='unit_create'),
]
