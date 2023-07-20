from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'notaentrega'
urlpatterns = [
    path('', login_required(views.ListadoNotasEntrega.as_view()),
         name='listado_notasentrega'),
    path('ajax_listado_notasentrega/', login_required(views.ajax_listado_notasentrega),
         name='ajax_listado_notasentrega'),

    path('crear_notaentrega/', login_required(views.CrearNotaEntrega.as_view()),
         name='crear_notaentrega'),
    path('eliminar_notaentrega/<int:pk>',
         login_required(views.EliminarNotaEntrega.as_view()), name='eliminar_notaentrega'),

    path('ajax/agregar_item/',
         login_required(views.ajaxAgregarItem), name='agregar_item'),
    path('ajax/agregar_item_sin_existencia/',
         login_required(views.ajaxAgregarItemSinExistencia), name='agregar_item_sin_existencia'),
    path('ajax/editar_item/', login_required(views.ajaxEditarItem), name='editar_item'),
    path('ajax/editar_item_sin_existencia/',
         login_required(views.ajaxEditarItemSinExistencia), name='editar_item_sin_existencia'),

    path('ajax/eliminar_item/',
         login_required(views.ajaxEliminarItem), name='eliminar_item'),

    # path('ajax/total_filas_carrito/',
    #     login_required(views.ajaxGetTotalFilasCarrito), name='total_filas_carrito'),
    #path('ajax/vaciar_carrito/', login_required(views.ajaxVaciarCarrito), name='vaciar_carrito'),

    path('ajax/guardar_notaentrega/',
         login_required(views.guardarNotaEntrega), name='guardar_notaentrega'),

    path('crear_cliente_modal/', login_required(views.CrearClienteModal.as_view()),
         name='crear_cliente_modal'),

    path('render/pdf/<int:pk>',
         login_required(views.GeneratePDF.as_view()), name='render_pdf'),
    # path('render/pdf/', login_required(GeneratePDF.as_view()), name='render_pdf'),

    path('plantilla/<int:pk>',
         login_required(views.PlantillaNotaEntrega.as_view()), name='plantilla'),

    # pagos
    path('sales_cash_payment/', login_required(views.ajax_cash_payment),
         name='sales_cash_payment'),
]
