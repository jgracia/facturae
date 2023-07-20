from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'contabilidad'
urlpatterns = [
    path('mensaje_vista/', login_required(views.message_view), name='mensaje_vista'),

    path('listado_turnos/', login_required(views.ListadoTurnos.as_view()), name='listado_turnos'),
    path('crear_turno/', login_required(views.CrearTurno.as_view()), name='crear_turno'),
    path('modificar_turno/<int:pk>', login_required(views.ModificarTurno.as_view()), name='modificar_turno'),
    path('detalle_turno/<int:pk>', login_required(views.DetalleTurno.as_view()), name='detalle_turno'),
    path('eliminar_turno/<int:pk>', login_required(views.EliminarTurno.as_view()), name='eliminar_turno'),
    #path('cerrar_turno/<int:pk>', login_required(views.CerrarTurnoModal.as_view()), name='cerrar_turno'),
    path('cerrar_turno/<int:turno_id>', login_required(views.arqueo_caja_list), name='cerrar_turno'),
    path('terminar_cierre_caja/', login_required(views.terminar_cierre_caja), name='terminar_cierre_caja'),
    path('ajax/imprimir_recibo/', login_required(views.ajaxImprimirRecibo), name='imprimir_recibo'),

    # rutas períodos
    path('listado_periodos/', login_required(views.ListadoPeriodos.as_view()), name='listado_periodos'),
    path('crear_periodo/', login_required(views.CrearPeriodo.as_view()), name='crear_periodo'),
    path('editar_periodo/<pk>', login_required(views.EditarPeriodo.as_view()), name='editar_periodo'),
    path('detalle_periodo/<pk>', login_required(views.DetallePeriodo.as_view()), name='detalle_periodo'),
    path('eliminar_periodo/<pk>', login_required(views.EliminarPeriodo.as_view()), name='eliminar_periodo'),

    # rutas plan de cuentas
    path('listado_cuentas/', login_required(views.ListadoCuentas.as_view()), name='listado_cuentas'),
    #path('listado_cuentas/', login_required(views.show_genres), name='listado_cuentas'),
    #path('ajax_listado_cuentas/', login_required(views.ajax_listado_cuentas), name='ajax_listado_cuentas'),

    path('cargar_plan_cuenta/', login_required(views.cargar_plan_cuenta_excel), name='cargar_plan_cuenta'),
    path('crear_cuenta/', login_required(views.CrearCuenta.as_view()), name='crear_cuenta'),
    path('editar_cuenta/<pk>', login_required(views.EditarCuenta.as_view()), name='editar_cuenta'),
    path('detalle_cuenta/<pk>', login_required(views.DetalleCuenta.as_view()), name='detalle_cuenta'),
    path('eliminar_cuenta/<pk>', login_required(views.EliminarCuenta.as_view()), name='eliminar_cuenta'),
    path('ajax_load_padre/', login_required(views.load_padre), name='ajax_load_padre'),

    # rutas libro diario
    path('libro_diario/', login_required(views.LibroDiarioView.as_view()), name='libro_diario'),
    path('ajax_listado_asientos/', login_required(views.ajax_listado_asientos), name='ajax_listado_asientos'),
    path('crear_asiento/', login_required(views.CrearAsiento.as_view()), name='crear_asiento'),
    path('ajax_busqueda_cuentas_typeahead/', login_required(views.ajax_busqueda_cuentas_typeahead),
         name='ajax_busqueda_cuentas_typeahead'),
    path('ajax_guardar_asiento/', login_required(views.ajax_guardar_asiento), name='ajax_guardar_asiento'),
    path('editar_asiento/<int:pk>', login_required(views.EditarAsiento.as_view()), name='editar_asiento'),
    path('eliminar_asiento/<int:pk>',
         login_required(views.EliminarAsiento.as_view()), name='eliminar_asiento'),
    path('asiento_agregar_cuenta/', login_required(views.asiento_agregar_cuenta),
         name='asiento_agregar_cuenta'),

    path('render/pdf/libro_mayor_auxiliar',
         login_required(views.GenerateLibroMayorAuxiliarPDF.as_view()), name='libro_mayor_auxiliar'),
    path('render/pdf/libro_mayor_principal',
         login_required(views.GenerateLibroMayorPrincipalPDF.as_view()), name='libro_mayor_principal'),
    path('render/pdf/balance_comprobacion',
         login_required(views.GenerateBalanceComprobacionPDF.as_view()), name='balance_comprobacion'),
    path('render/pdf/estado_resultados/<int:pk>',
         login_required(views.GenerateEstadoResultadosPDF.as_view()), name='estado_resultados'),
    path('render/pdf/balance_general/<int:pk>',
         login_required(views.GenerateBalanceGeneralPDF.as_view()), name='balance_general'),

    # rutas asientos automáticos
    path('listado_asientos_automaticos/', login_required(views.ListadoAsientosAutomaticos.as_view()),
         name='listado_asientos_automaticos'),
    path('cargar_asiento_auto/', login_required(views.cargar_asiento_auto_excel), name='cargar_asiento_auto'),
    path('ajax_asiento_automatico/', login_required(views.ajax_asiento_automatico),
         name='ajax_asiento_automatico'),
    path('editar_asiento_automatico/<pk>',
         login_required(views.EditarAsientoAutomatico.as_view()), name='editar_asiento_automatico'),

    #path('crear_turno/', login_required(views.crear_turno_view), name='crear_turno'),
    #path('detalle_turno/<int:pk>', login_required(views.DetalleTurno.as_view()), name='detalle_turno'),

    #path('cerrar_turno/<int:pk>', login_required(views.cerrar_turno_view), name='cerrar_turno'),

    # path('flujo_caja_efectivo/', login_required(views.FlujoCajaEfectivo.as_view()),
    #     name='flujo_caja_efectivo'),
    #path('apertura_caja/', login_required(views.apertura_caja_view), name='apertura_caja'),


    #path('view/<int:pk>', login_required(views.DetalleTurno.as_view()), name='view'),

    path('cheques_recibidos/', login_required(views.ListadoChequesRecibidos.as_view()),
         name='cheques_recibidos'),
    path('cheques_entregados/', login_required(views.ListadoChequesEntregados.as_view()),
         name='cheques_entregados'),

    # path('plan_cuenta/', login_required(views.PlanCuenta.as_view()),
    #     name='plan_cuenta'),
    #path('show_genres/', login_required(views.show_genres), name='show_genres'),

    path('cuentas_pagar/', login_required(views.CuentasPagarIndexView.as_view()), name='cuentas_pagar'),
    path('credito/abonar_cta_pagar/', login_required(views.ajaxAbonoCtaPagar), name='abonar_cta_pagar'),

    path('cuentas_cobrar/', login_required(views.CuentasCobrarIndexView.as_view()), name='cuentas_cobrar'),
    path('credito/abonar_cta_cobrar/', login_required(views.ajaxAbonoCtaCobrar), name='abonar_cta_cobrar'),


    path('ajax_tree_cuentas/', login_required(views.ajax_tree_cuentas), name='ajax_tree_cuentas'),
    path('buscar_cuentadb/', login_required(views.ajaxBuscarCuentaDB), name='buscar_cuentadb'),

    path('ajax_actualizar_asiento/', login_required(views.ajax_actualizar_asiento),
         name='ajax_actualizar_asiento'),
    path('resumen_sri/', login_required(views.ResumenSRI.as_view()),
         name='resumen_sri'),
    path('render/ats/pdf/<periodo_fiscal>', login_required(views.ResumenAtsPdf.as_view()),
         name='render_ats'),
    path('resumen_sri_xls', login_required(views.resumen_sri_xls),
         name='resumen_sri_xls'),
]
