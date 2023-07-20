from django.urls import path
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from .views import ListadoVentas, ajax_listado_ventas, CrearVenta, \
    busquedaClientes, ajaxAgregarItem, ajaxAgregarItemSinExistencia, \
    localizarAgregarElemento, ajaxEliminarItem, ajaxEditarItem, \
    ajaxEditarItemSinExistencia, CrearClienteModal, ajaxIntercambioResumen, \
    guardarFactura, mostrarFactura, GeneratePDF, CuentasCobrarIndexView, \
    ajaxPaymentView, RetencionesIndexView, ajaxAnularComprobante, \
    imprimirTicketLocalNetwork, imprimirTicketInterfazWeb, \
    imprimirFactura, seleccionar_lote, \
    buscar_lote_seleccionado, get_lot_list_by_product, \
    html_to_pdf_directly_ticket, generar_archivo_binario, tpv, paymentListView, \
    ajax_cash_payment

app_name = 'venta'
urlpatterns = [
    path('', login_required(ListadoVentas.as_view()), name='listado_ventas'),
    path('ajax_listado_ventas/', login_required(ajax_listado_ventas), name='ajax_listado_ventas'),
    path('crear_venta/', login_required(CrearVenta.as_view()), name='crear_venta'),
    #path('ajax/product_lookup/', login_required(product_lookup), name='product_lookup'),
    path('ajax/busquedaClientes/', login_required(busquedaClientes), name='busquedaClientes'),

    path('ajax/agregar_item/', login_required(ajaxAgregarItem), name='agregar_item'),
    path('ajax/agregar_item_sin_existencia/',
         login_required(ajaxAgregarItemSinExistencia), name='agregar_item_sin_existencia'),
    path('ajax/localizar_agregar_elemento_venta/', login_required(localizarAgregarElemento),
         name='localizar_agregar_elemento'),

    path('ajax/editar_item/', login_required(ajaxEditarItem), name='editar_item'),
    path('ajax/editar_item_sin_existencia/',
         login_required(ajaxEditarItemSinExistencia), name='editar_item_sin_existencia'),
    path('ajax/seleccionar_lote/', login_required(seleccionar_lote), name='seleccionar_lote'),
    path('ajax/buscar_lote_seleccionado/',
         login_required(buscar_lote_seleccionado), name='buscar_lote_seleccionado'),
    path('ajax/get_lot_list/', login_required(get_lot_list_by_product), name='get_lot_list'),

    path('ajax/eliminar_item/', login_required(ajaxEliminarItem), name='eliminar_item'),
    #path('ajax/vaciar_carrito/', login_required(ajaxVaciarCarrito), name='vaciar_carrito'),
    #path('ajax/total_filas_carrito/', login_required(ajaxGetTotalFilasCarrito), name='total_filas_carrito'),
    path('ajax/intercambio_resumen/', login_required(ajaxIntercambioResumen), name='intercambio_resumen'),
    path('ajax/guardar_factura/', login_required(guardarFactura), name='guardar_factura'),
    path('ajax/imprimirFactura/', login_required(imprimirFactura), name='imprimirFactura'),
    path('ajax/mostrarFactura/', login_required(mostrarFactura), name='mostrarFactura'),
    #path('render/pdf/', login_required(GeneratePDF.as_view())),
    path('render/pdf/<int:pk>', login_required(GeneratePDF.as_view()), name='render_pdf'),
    path('anular_comprobante/<int:pk>', login_required(ajaxAnularComprobante), name='anular_comprobante'),
    #path('firmarFactura/', login_required(firmarFactura), name='firmarFactura'),
    #path('enviarRecepcionSRI/', login_required(enviarRecepcionSRI), name='enviarRecepcionSRI'),
    #path('solicitarAutorizacionSRI/', login_required(solicitarAutorizacionSRI), name='solicitarAutorizacionSRI'),

    path('crear_cliente_modal/', login_required(CrearClienteModal.as_view()), name='crear_cliente_modal'),
    path('cuentas_cobrar/', login_required(CuentasCobrarIndexView.as_view()), name='cuentas_cobrar'),
    path('credito/abonar/', login_required(ajaxPaymentView), name='credito_abonar'),

    path('retenciones/', login_required(RetencionesIndexView.as_view()), name='retencion_venta'),

    path('ajax/generar_archivo_binario/',
         login_required(generar_archivo_binario), name='generar_archivo_binario'),
    path('ajax/imprimir_ticket/', login_required(imprimirTicketLocalNetwork), name='imprimir_ticket'),
    path('print/ticket/', login_required(imprimirTicketInterfazWeb),
         name='imprimir_ticket_interfaz_web'),

    # path('print/browserify/', login_required(imprimir_browserify),
    #     name='imprimir_browserify'),

    path('render/ticket/<inflow_id>', login_required(html_to_pdf_directly_ticket), name='ticketpdf'),
    path('ajax/imprimir_factura/', login_required(imprimirFactura), name='imprimir_factura'),

    #path('ajax/imprimir_proforma/', login_required(imprimirProforma), name='imprimir_proforma'),
    path('tpv/', login_required(tpv), name='tpv'),

    path('payment-detail/', login_required(paymentListView), name='payment'),

    path('sales_cash_payment/', login_required(ajax_cash_payment), name='sales_cash_payment'),

]
