from django.urls import path
from django.contrib.auth.decorators import login_required

"""from .views import ListadoProformas, CrearProforma, ajaxAgregarItem, \
    ajaxAgregarItemSinExistencia, ajaxGetTotalFilasCarrito, ajaxEditarItem, \
    ajaxEditarItemSinExistencia, ajaxEliminarItem, ajaxVaciarCarrito, \
    guardarFactura, CrearClienteModal, EliminarProforma, GeneratePDF, \
    PlantillaProforma"""

from . import views

app_name = 'proforma'
urlpatterns = [
    path('', login_required(views.ListadoProformas.as_view()), name='listado_proformas'),
    path('ajax_listado_proformas/', login_required(views.ajax_listado_proformas),
         name='ajax_listado_proformas'),
    path('crear_proforma/', login_required(views.CrearProforma.as_view()), name='crear_proforma'),
    path('eliminar_proforma/<int:pk>',
         login_required(views.EliminarProforma.as_view()), name='eliminar_proforma'),

    path('ajax/agregar_item/', login_required(views.ajaxAgregarItem), name='agregar_item'),
    path('ajax/agregar_item_sin_existencia/',
         login_required(views.ajaxAgregarItemSinExistencia), name='agregar_item_sin_existencia'),
    path('ajax/editar_item/', login_required(views.ajaxEditarItem), name='editar_item'),
    path('ajax/editar_item_sin_existencia/',
         login_required(views.ajaxEditarItemSinExistencia), name='editar_item_sin_existencia'),

    path('ajax/eliminar_item/', login_required(views.ajaxEliminarItem), name='eliminar_item'),

    # path('ajax/total_filas_carrito/',
    #     login_required(views.ajaxGetTotalFilasCarrito), name='total_filas_carrito'),
    #path('ajax/vaciar_carrito/', login_required(views.ajaxVaciarCarrito), name='vaciar_carrito'),

    path('ajax/guardar_proforma/', login_required(views.guardarProforma), name='guardar_proforma'),

    path('crear_cliente_modal/', login_required(views.CrearClienteModal.as_view()),
         name='crear_cliente_modal'),

    path('render/pdf/<int:pk>', login_required(views.GeneratePDF.as_view()), name='render_pdf'),
    #path('render/pdf/', login_required(GeneratePDF.as_view()), name='render_pdf'),

    path('plantilla/<int:pk>', login_required(views.PlantillaProforma.as_view()), name='plantilla'),

]
