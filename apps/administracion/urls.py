from django.urls import path
from django.contrib.auth.decorators import login_required
from apps.usuario.decorators import supervisor_required
from django.http import HttpResponse

from .views import ListadoBancos, CrearBanco, ModificarBanco,\
    DetalleBanco, EliminarBanco, \
    ListadoTarjetas, CrearTarjeta, ModificarTarjeta, DetalleTarjeta, EliminarTarjeta, \
    ListadoEmpresas, CrearEmpresa, ModificarEmpresa, DetalleEmpresa, EliminarEmpresa, \
    ListadoSecuencias, CrearSecuencia, EditarSecuencia, DetalleSecuencia, EliminarSecuencia

from apps.usuario.views import ListadoUsuarios

app_name = 'administracion'
urlpatterns = [
    path('bancos/', login_required(ListadoBancos.as_view()), name='listado_bancos'),
    path('crear_banco/', login_required(CrearBanco.as_view()), name='crear_banco'),
    path('modificar_banco/<int:pk>', login_required(ModificarBanco.as_view()), name='modificar_banco'),
    path('detalle_banco/<int:pk>', login_required(DetalleBanco.as_view()), name='detalle_banco'),
    path('eliminar_banco/<int:pk>', login_required(EliminarBanco.as_view()), name='eliminar_banco'),

    path('tarjetas/', login_required(ListadoTarjetas.as_view()), name='listado_tarjetas'),
    path('crear_tarjeta/', login_required(CrearTarjeta.as_view()), name='crear_tarjeta'),
    path('modificar_tarjeta/<int:pk>', login_required(ModificarTarjeta.as_view()), name='modificar_tarjeta'),
    path('detalle_tarjeta/<int:pk>', login_required(DetalleTarjeta.as_view()), name='detalle_tarjeta'),
    path('eliminar_tarjeta/<int:pk>', login_required(EliminarTarjeta.as_view()), name='eliminar_tarjeta'),

    path('listado_empresas', ListadoEmpresas.as_view(), name='listado_empresas'),
    path('crear_empresa/', supervisor_required(CrearEmpresa.as_view()), name='crear_empresa'),
    path('modificar_empresa/<int:pk>', login_required(ModificarEmpresa.as_view()), name='modificar_empresa'),
    path('detalle_empresa/<int:pk>', login_required(DetalleEmpresa.as_view()), name='detalle_empresa'),
    path('eliminar_empresa/<int:pk>', login_required(EliminarEmpresa.as_view()), name='eliminar_empresa'),

    path('listado_secuencias', login_required(ListadoSecuencias.as_view()), name='listado_secuencias'),
    path('crear_secuencia/', login_required(CrearSecuencia.as_view()), name='crear_secuencia'),
    path('editar_secuencia/<int:pk>', login_required(EditarSecuencia.as_view()), name='editar_secuencia'),
    path('detalle_secuencia/<int:pk>', login_required(DetalleSecuencia.as_view()), name='detalle_secuencia'),
    path('eliminar_secuencia/<int:pk>',
         login_required(EliminarSecuencia.as_view()), name='eliminar_secuencia'),

    path('usuarios/', login_required(ListadoUsuarios.as_view()), name='listado_usuarios'),
]
