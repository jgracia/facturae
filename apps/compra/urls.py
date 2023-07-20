from django.urls import path
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from . import views

app_name = 'compra'
urlpatterns = [
    path('', login_required(views.ListadoCompras.as_view()), name='listado_compras'),
    path('ajax_listado_compras/', login_required(views.ajax_listado_compras), name='ajax_listado_compras'),
    path('ingresar_compra/', login_required(views.CrearCompra.as_view()), name='ingresar_compra'),
    #path('modificar_compra/<int:pk>', login_required(views.ModificarCompra.as_view()), name='modificar_compra'),
    path('modificar_compra/<orden_id>', login_required(views.ModificarCompra), name='modificar_compra'),
    path('eliminar_compra/<int:pk>', login_required(views.EliminarCompra.as_view()), name='eliminar_compra'),
    path('ajax/busqueda_productos/', login_required(views.busquedaProductos), name='busqueda_productos'),

    # acciones tabla productos
    path('ajax/agregar_item/', login_required(views.ajaxAgregarItem), name='agregar_item'),
    path('ajax/localizar_agregar_elemento_compra/',
         login_required(views.localizarAgregarElemento), name='localizar_agregar_elemento'),
    path('ajax/editar_item/', login_required(views.ajaxEditarItem), name='editar_item'),
    path('ajax/eliminar_item/', login_required(views.ajaxEliminarItem), name='eliminar_item'),

    path('ajax/compra_agregar_lote/', login_required(views.agregar_lote), name='agregar_lote'),

    #path('ajax/vaciar_carrito/', login_required(views.ajaxVaciarCarrito), name='vaciar_carrito'),
    # path('ajax/total_filas_carrito/',
    #     login_required(views.ajaxGetTotalFilasCarrito), name='total_filas_carrito'),
    #path('total_filas_cesta/', login_required(views.total_filas_cesta), name='total_filas_cesta'),
    path('ajax/intercambio_resumen/',
         login_required(views.ajaxIntercambioResumen), name='intercambio_resumen'),
    path('ajax/guardar_orden/', login_required(views.guardarOrden), name='guardar_orden'),

    path('crear_proveedor_modal/', login_required(views.CrearProveedorModal.as_view()),
         name='crear_proveedor_modal'),
    path('ajax_buscar_comprobante/', login_required(views.BuscarComprobanteModal.as_view()),
         name='ajax_buscar_comprobante'),
    path('cuentas_pagar/', login_required(views.CuentasPagarIndexView.as_view()), name='cuentas_pagar'),
    #path('credito/abonar/', login_required(views.ajaxPaymentView), name='credito_abonar'),
    path('abonar_credito/<int:id_pagocredito>',
         login_required(views.abonar_credito_modal), name='abonar_credito'),
    path('abono/efectivo/<int:id_pagocredito>',
         login_required(views.abono_efectivo), name='abono_efectivo'),

    path('export/xls/', login_required(views.export_credits_xls), name='export_credits_xls'),
    path('render/pdf/<int:pk>', login_required(views.GeneratePDF.as_view()), name='render_pdf'),

    # ruta comprobante xml
    path('upload_driver/', login_required(views.upload_driver), name='upload_driver'),
    path('get_comprobante_xml/', login_required(views.get_comprobante_xml), name='get_comprobante_xml'),

    # formularios de pagos
    # path('pago_efectivo/', login_required(views.PagoEfectivoModal.as_view()),
    #     name='pago_efectivo'),
    # path('cash_payment/<int:param1>/<slug:param2>/<str:param3>',
    #     login_required(views.cash_payment),
    #     name='cash_payment'),
    # path('cash_payment/', login_required(views.cash_payment), name='cash_payment'),
    path('purchase-payment/', login_required(views.ajax_purchase_payment),
         name='purchase_payment'),



]
