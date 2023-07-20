from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'sri'
urlpatterns = [
    path('listado_tipos_comprobantes', login_required(
        views.ListadoTiposComprobantes.as_view()), name='listado_tipos_comprobantes'),
    path('crear_comprobante/', login_required(views.CrearTipoComprobante.as_view()),
         name='crear_tipo_comprobante'),
    path('modificar_comprobante/<int:pk>', login_required(views.ModificarTipoComprobante.as_view()),
         name='modificar_tipo_comprobante'),
    path('eliminar_comprobante/<int:pk>', login_required(views.EliminarTipoComprobante.as_view()),
         name='eliminar_tipo_comprobante'),
    path('detalle_comprobante/<int:pk>', login_required(views.DetalleTipoComprobante.as_view()),
         name='detalle_tipo_comprobante'),

    path('listar_identificaciones/', login_required(views.ListadoTiposIdentificaciones.as_view()),
         name='listado_tipos_identificaciones'),
    path('crear_identificacion/', login_required(views.CrearTipoIdentificacion.as_view()),
         name='crear_tipo_identificacion'),
    path('modificar_identificacion/<int:pk>',
         login_required(views.ModificarTipoIdentificacion.as_view()), name='modificar_tipo_identificacion'),
    path('detalle_identificacion/<int:pk>',
         login_required(views.DetalleTipoIdentificacion.as_view()), name='detalle_tipo_identificacion'),
    path('eliminar_identificacion/<int:pk>',
         login_required(views.EliminarTipoIdentificacion.as_view()), name='eliminar_tipo_identificacion'),

    path('listar_iva/', login_required(views.ListadoTarifaIva.as_view()),
         name='listado_tarifa_iva'),
    path('crear_iva/', login_required(views.CrearTarifaIva.as_view()), name='crear_tarifa_iva'),
    path('modificar_iva/<int:pk>', login_required(views.ModificarTarifaIva.as_view()),
         name='modificar_tarifa_iva'),
    path('detalle_iva/<int:pk>', login_required(views.DetalleTarifaIva.as_view()),
         name='detalle_tarifa_iva'),
    path('eliminar_iva/<int:pk>', login_required(views.EliminarTarifaIva.as_view()),
         name='eliminar_tarifa_iva'),

    path('listar_ice/', login_required(views.ListadoTarifaIce.as_view()),
         name='listado_tarifa_ice'),
    path('crear_ice/', login_required(views.CrearTarifaIce.as_view()), name='crear_tarifa_ice'),
    path('modificar_ice/<int:pk>', login_required(views.ModificarTarifaIce.as_view()),
         name='modificar_tarifa_ice'),
    path('detalle_ice/<int:pk>', login_required(views.DetalleTarifaIce.as_view()),
         name='detalle_tarifa_ice'),
    path('eliminar_ice/<int:pk>', login_required(views.EliminarTarifaIce.as_view()),
         name='eliminar_tarifa_ice'),

    path('listar_irbpnr/', login_required(views.ListadoTarifaIrbpnr.as_view()),
         name='listado_tarifa_irbpnr'),
    path('crear_irbpnr/', login_required(views.CrearTarifaIrbpnr.as_view()), name='crear_tarifa_irbpnr'),
    path('modificar_irbpnr/<int:pk>', login_required(views.ModificarTarifaIrbpnr.as_view()),
         name='modificar_tarifa_irbpnr'),
    path('detalle_irbpnr/<int:pk>', login_required(views.DetalleTarifaIrbpnr.as_view()),
         name='detalle_tarifa_irbpnr'),
    path('eliminar_irbpnr/<int:pk>', login_required(views.EliminarTarifaIrbpnr.as_view()),
         name='eliminar_tarifa_irbpnr'),

    path('listar_documentos/', login_required(views.ListadoTiposDocumentos.as_view()),
         name='listado_tipos_documentos'),
    path('crear_documento/', login_required(views.CrearTipoDocumento.as_view()), name='crear_tipo_documento'),
    path('modificar_documento/<int:pk>', login_required(views.ModificarTipoDocumento.as_view()),
         name='modificar_tipo_documento'),
    path('detalle_documento/<int:pk>', login_required(views.DetalleTipoDocumento.as_view()),
         name='detalle_tipo_documento'),
    path('eliminar_documento/<int:pk>', login_required(views.EliminarTipoDocumento.as_view()),
         name='eliminar_tipo_documento'),

    path('listar_monedas/', login_required(views.ListadoTiposMoneda.as_view()), name='listado_tipos_monedas'),
    path('crear_moneda/', login_required(views.CrearTipoMoneda.as_view()), name='crear_tipo_moneda'),
    path('modificar_moneda/<int:pk>', login_required(views.ModificarTipoMoneda.as_view()),
         name='modificar_tipo_moneda'),
    path('detalle_moneda/<int:pk>', login_required(views.DetalleTipoMoneda.as_view()),
         name='detalle_tipo_moneda'),
    path('eliminar_moneda/<int:pk>', login_required(views.EliminarTipoMoneda.as_view()),
         name='eliminar_tipo_moneda'),

    path('listado_tipos_impuestos', login_required(
        views.ListadoTiposImpuestos.as_view()), name='listado_tipos_impuestos'),
    path('crear_tipo_impuesto/', login_required(views.CrearTipoImpuesto.as_view()),
         name='crear_tipo_impuesto'),
    path('modificar_tipo_impuesto/<int:pk>', login_required(views.ModificarTipoImpuesto.as_view()),
         name='modificar_tipo_impuesto'),
    path('detalle_tipo_impuesto/<int:pk>', login_required(views.DetalleTipoImpuesto.as_view()),
         name='detalle_tipo_impuesto'),
    path('eliminar_tipo_impuesto/<int:pk>', login_required(views.EliminarTipoImpuesto.as_view()),
         name='eliminar_tipo_impuesto'),
]
