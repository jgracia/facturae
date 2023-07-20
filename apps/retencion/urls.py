from django.urls import path
from django.contrib.auth.decorators import login_required

from .views import RetencionesIndexView, CrearRetencion, \
    load_impuesto, get_porcentaje, guardar_retencion, load_comprobantes, \
    get_baseimponible, GeneratePDF, ajax_listado_retenciones, EliminarRetencion

app_name = 'retencion'
urlpatterns = [
    path('', login_required(RetencionesIndexView.as_view()), name='listado_retenciones'),
    path('ajax_listado_retenciones/', login_required(ajax_listado_retenciones),
         name='ajax_listado_retenciones'),
    path('ingresar_retencion/', login_required(CrearRetencion.as_view()), name='ingresar_retencion'),
    path('ajax/ajax_load_impuesto/', login_required(load_impuesto), name='ajax_load_impuesto'),
    path('ajax/ajax_get_porcentaje/', login_required(get_porcentaje), name='ajax_get_porcentaje'),
    path('ajax/guardar_retencion/', login_required(guardar_retencion), name='guardar_retencion'),

    path('ajax/ajax_load_comprobantes/', login_required(load_comprobantes), name='ajax_load_comprobantes'),
    path('ajax/ajax_get_baseimponible/', login_required(get_baseimponible), name='ajax_get_baseimponible'),

    path('render/pdf/<int:pk>', login_required(GeneratePDF.as_view()), name='render_pdf'),
    path('eliminar_retencion/<int:pk>',
         login_required(EliminarRetencion.as_view()), name='eliminar_retencion'),

]
