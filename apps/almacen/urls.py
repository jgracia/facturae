from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'almacen'
urlpatterns = [
    path('listado_almacenes', login_required(views.ListadoAlmacenes.as_view()), name='listado_almacenes'),
    path('crear_almacen/', login_required(views.CrearAlmacen.as_view()), name='crear_almacen'),
    path('editar_almacen/<int:pk>', login_required(views.EditarAlmacen.as_view()), name='editar_almacen'),
    path('detalle_almacen/<int:pk>', login_required(views.DetalleAlmacen.as_view()), name='detalle_almacen'),
    path('eliminar_almacen/<int:pk>',
         login_required(views.EliminarAlmacen.as_view()), name='eliminar_almacen'),

    # ruta busqueda de producto para inventario/entrada/salida/ajuste
    path('obtener_propiedades_producto/', login_required(views.obtener_propiedades_producto),
         name='obtener_propiedades_producto'),

    # rutas inventario
    path('existencias/', login_required(views.ExistenciasIndexView.as_view()), name='existencias'),
    path('listado_entradas', login_required(views.ListadoEntradas.as_view()), name='listado_entradas'),
    path('ajax_listado_entradas/', login_required(views.ajax_listado_entradas), name='ajax_listado_entradas'),
    path('inventario_entrada/', login_required(views.EntradaInventario.as_view()), name='inventario_entrada'),
    path('entrada/add/<product_id>', login_required(views.cartin_add), name='cartin_add'),
    path('entrada/show/', login_required(views.cartin_show), name='cartin_show'),
    path('entrada/update/', login_required(views.cartin_update), name='cartin_update'),
    path('entrada/remove/', login_required(views.cartin_remove), name='cartin_remove'),
    path('entrada/save/', login_required(views.cartin_save), name='cartin_save'),

    # rutas salidas
    path('listado_salidas/', login_required(views.ListadoSalidas.as_view()), name='listado_salidas'),
    path('ajax_listado_salidas/', login_required(views.ajax_listado_salidas), name='ajax_listado_salidas'),
    path('inventario_salida/', login_required(views.SalidaInventario.as_view()), name='inventario_salida'),
    path('salida/add/<product_id>', login_required(views.cartout_add), name='cartout_add'),
    path('salida/show/', login_required(views.cartout_show), name='cartout_show'),
    path('salida/update/', login_required(views.cartout_update), name='cartout_update'),
    path('salida/remove/', login_required(views.cartout_remove), name='cartout_remove'),
    #path('salida/is_empty/', login_required(views.cartout_is_empty), name='cartout_is_empty'),
    path('salida/save/', login_required(views.cartout_save), name='cartout_save'),

    # rutas ajuste
    path('listado_ajustes', login_required(views.ListadoAjustes.as_view()), name='listado_ajustes'),
    path('ajax_listado_ajustes/', login_required(views.ajax_listado_ajustes), name='ajax_listado_ajustes'),
    path('inventario_ajuste/', login_required(views.AjusteInventarioView.as_view()), name='inventario_ajuste'),
    path('ajuste/add/<product_id>', login_required(views.cartfit_add), name='cartfit_add'),
    path('ajuste/show/', login_required(views.cart_show), name='ajuste_cart_show'),
    path('ajuste/remove-single/', login_required(views.cartfit_remove_single),
         name='cartfit_remove_single'),  # no se esta usando
    path('ajuste/remove/', login_required(views.cartfit_remove), name='cartfit_remove'),
    #path('eliminar_ajuste/<int:pk>', login_required(views.ajaxEliminarAjuste), name='eliminar_ajuste'),
    path('ajuste/update/', login_required(views.cartfit_update), name='cartfit_update'),
    #path('ajuste/is_empty/', login_required(views.cartfit_is_empty), name='cartfit_is_empty'),
    path('ajuste/is_exist/', login_required(views.stock_is_exist), name='stock_is_exist'),
    path('ajuste/save/', login_required(views.cartfit_save), name='cartfit_save'),
    path('ajax/ajuste_agregar_lote/', login_required(views.ajuste_agregar_lote), name='ajuste_agregar_lote'),

    path('kardex/', login_required(views.KardexIndexView.as_view()), name='kardex'),
    path('ajax/ajuste_buscar_producto/', login_required(views.ajaxBuscarProductoDB), name='buscar_producto'),
    path('ajax/product_lookup/', login_required(views.product_lookup), name='product_lookup'),
    path('consolidado_productos/', login_required(views.ConsolidadoProductosIndexView.as_view()),
         name='consolidado_productos'),
    path('ajax_consolidado_productos/', login_required(views.ajax_consolidado_productos),
         name='ajax_consolidado_productos'),

    path('consolidado_movimientos/', login_required(views.ConsolidadoMovimientosIndexView.as_view()),
         name='consolidado_movimientos'),
    path('ajax_consolidado_movimientos/', login_required(views.ajax_consolidado_movimientos),
         name='ajax_consolidado_movimientos'),
    path('api/', login_required(views.KardexAPI.as_view()), name='api'),

    path('jquerytypeahead/kardex_json/', login_required(views.kardex_json), name='kardex_json'),
    path('get_producto_control/', login_required(views.get_producto_control), name='get_producto_control'),
    # path('get_embalaje_principal/', login_required(views.get_embalaje_principal),
    #     name='get_embalaje_principal'),
]
