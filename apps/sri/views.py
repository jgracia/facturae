from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.http import JsonResponse
from django.template.loader import render_to_string


from .models import SriTipoComprobante, SriTipoIdentificacion, \
    SriTarifaIVA, SriTarifaICE, SriTarifaIRBPNR, \
    SriTipoDocumento, SriTipoMoneda, SriTipoImpuesto

from .forms import TipoComprobanteForm, TipoIdentificacionForm, \
    TarifaIvaForm, TarifaIceForm, TarifaIrbpnrForm, TipoDocumentoForm, \
    TipoMonedaForm, TipoImpuestoForm, TipoComprobanteModalForm, \
    TipoComprobanteNewForm

from bootstrap_modal_forms.generic import (BSModalCreateView,
                                           BSModalUpdateView,
                                           BSModalReadView,
                                           BSModalDeleteView)


# paginación
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render_to_response
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger


from django.http import HttpResponse
from django.urls import reverse

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin

# export data
import xlwt  # libreria para exportar a excel

# librerias para PDF
from django.views.generic import View
from django.http import HttpResponse
from django.template.loader import get_template
from apps.dashboard.render import render_to_pdf
from django.utils import timezone

# Create your views here.

""" FORMULARIOS TIPOS DE COMPROBANTES """


class ListadoTiposComprobantes(ListView):
    model = SriTipoComprobante
    template_name = 'sri/tipo_comprobante/listado_tipos_comprobantes.html'
    context_object_name = 'tipos_comprobantes'


class CrearTipoComprobante(BSModalCreateView):
    template_name = 'sri/tipo_comprobante/crear_tipo_comprobante.html'
    form_class = TipoComprobanteForm
    success_message = 'Success: La cuenta fue creada.'
    success_url = reverse_lazy('sri:listado_tipos_comprobantes')

    def form_valid(self, form):
        form.instance.usuario_creador = self.request.user
        return super(CrearTipoComprobante, self).form_valid(form)


class ModificarTipoComprobante(BSModalUpdateView):
    model = SriTipoComprobante
    template_name = 'sri/tipo_comprobante/modificar_tipo_comprobante.html'
    form_class = TipoComprobanteForm
    success_message = 'Success: El comprobante fue actualizado.'
    success_url = reverse_lazy('sri:listado_tipos_comprobantes')


class EliminarTipoComprobante(BSModalDeleteView):
    model = SriTipoComprobante
    template_name = 'sri/tipo_comprobante/eliminar_tipo_comprobante.html'
    success_message = 'Success: El comprobante fue eliminado.'
    success_url = reverse_lazy('sri:listado_tipos_comprobantes')


class DetalleTipoComprobante(BSModalReadView):
    model = SriTipoComprobante
    template_name = 'sri/tipo_comprobante/detalle_tipo_comprobante.html'


def crear_tipo_comprobante(request):
    data = dict()

    if request.method == 'POST':
        form = TipoComprobanteForm(request.POST)
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False
    else:
        form = TipoComprobanteForm()

    context = {'form': form}
    data['html_form'] = render_to_string('sri/includes/partial_receipt_create.html',
                                         context,
                                         request=request
                                         )
    return JsonResponse(data)


"""def comprobante_editar(request, id_comprobante):
    comprobante = SriTipoComprobante.objects.get(pk=id_comprobante)
    if request.method == 'GET':
        form = TipoComprobanteForm(instance=comprobante)
    else:
        form = TipoComprobanteForm(request.POST, instance=comprobante)
        if form.is_valid():
            form.save()
        return redirect('sri:listado_tipos_comprobantes')
    return render(request, 'sri/tipo_comprobante/update_view_modal.html', {'form': form})"""


def comprobante_editar(request, entry_pk):

    entry = get_object_or_404(SriTipoComprobante, pk=entry_pk)

    if request.method != 'POST':
        form = TipoComprobanteForm(instance=entry)
    else:
        form = TipoComprobanteForm(instance=entry, data=request.POST)

        if form.is_valid():
            form.save()
            return redirect('sri:listado_tipos_comprobantes')
    return render(request, 'sri/tipo_comprobante/update_view_modal.html', {'pk': entry_pk, 'form': form})


def detalle_comprobante(request, id):
    context = {}
    tipo_comprobante_obj = SriTipoComprobante.objects.get(pk=id)
    context['object'] = tipo_comprobante_obj
    return render(request, 'sri/tipo_comprobante/detail_view_modal.html', context=context)


""" FORMULARIOS TIPOS DE IDENTIFICACIONES """


class ListadoTiposIdentificaciones(ListView):
    model = SriTipoIdentificacion
    template_name = 'sri/tipo_identificacion/tipos_identificaciones.html'
    context_object_name = 'tipos_identificaciones'


class CrearTipoIdentificacion(BSModalCreateView):
    template_name = 'sri/tipo_identificacion/crear_tipo_identificacion.html'
    form_class = TipoIdentificacionForm
    success_message = 'Success: La identificación fue creada.'
    success_url = reverse_lazy('sri:listado_tipos_identificaciones')

    def form_valid(self, form):
        form.instance.usuario_creador = self.request.user
        return super(CrearTipoIdentificacion, self).form_valid(form)


class ModificarTipoIdentificacion(BSModalUpdateView):
    model = SriTipoIdentificacion
    template_name = 'sri/tipo_identificacion/modificar_tipo_identificacion.html'
    form_class = TipoIdentificacionForm
    success_message = 'Success: La identificación fue actualizada.'
    success_url = reverse_lazy('sri:listado_tipos_identificaciones')


class DetalleTipoIdentificacion(BSModalReadView):
    model = SriTipoIdentificacion
    template_name = 'sri/tipo_identificacion/detalle_tipo_identificacion.html'


class EliminarTipoIdentificacion(BSModalDeleteView):
    model = SriTipoIdentificacion
    template_name = 'sri/tipo_identificacion/eliminar_tipo_identificacion.html'
    success_message = 'Success: La identificación fue eliminada.'
    success_url = reverse_lazy('sri:listado_tipos_identificaciones')


""" FORMULARIOS TIPOS DE DOCUMENTOS """


class ListadoTiposDocumentos(ListView):
    model = SriTipoDocumento
    template_name = 'sri/tipo_documento/tipos_documentos.html'
    context_object_name = 'tipos_impuestos'


class CrearTipoDocumento(BSModalCreateView):
    template_name = 'sri/tipo_documento/crear_tipo_documento.html'
    form_class = TipoDocumentoForm
    success_message = 'Success: El tipo de documento fue creado.'
    success_url = reverse_lazy('sri:listado_tipos_documentos')

    def form_valid(self, form):
        form.instance.usuario_creador = self.request.user
        return super(CrearTipoDocumento, self).form_valid(form)


class ModificarTipoDocumento(BSModalUpdateView):
    model = SriTipoDocumento
    template_name = 'sri/tipo_documento/modificar_tipo_documento.html'
    form_class = TipoDocumentoForm
    success_message = 'Success: El tipo de documento fue actualizado.'
    success_url = reverse_lazy('sri:listado_tipos_documentos')


class DetalleTipoDocumento(BSModalReadView):
    model = SriTipoDocumento
    template_name = 'sri/tipo_documento/detalle_tipo_documento.html'


class EliminarTipoDocumento(BSModalDeleteView):
    model = SriTipoDocumento
    template_name = 'sri/tipo_documento/eliminar_tipo_documento.html'
    success_message = 'Success: El tipo de documento fue eliminado.'
    success_url = reverse_lazy('sri:listado_tipos_documentos')


""" FORMULARIOS TIPOS DE MONEDA """


class ListadoTiposMoneda(ListView):
    model = SriTipoMoneda
    template_name = 'sri/tipo_moneda/tipos_monedas.html'
    context_object_name = 'tipos_monedas'


class CrearTipoMoneda(BSModalCreateView):
    template_name = 'sri/tipo_moneda/crear_tipo_moneda.html'
    form_class = TipoMonedaForm
    success_message = 'Success: El tipo de moneda fue creado.'
    success_url = reverse_lazy('sri:listado_tipos_monedas')

    def form_valid(self, form):
        form.instance.usuario_creador = self.request.user
        return super(CrearTipoMoneda, self).form_valid(form)


class ModificarTipoMoneda(BSModalUpdateView):
    model = SriTipoMoneda
    template_name = 'sri/tipo_moneda/modificar_tipo_moneda.html'
    form_class = TipoMonedaForm
    success_message = 'Success: El tipo de moneda fue actualizado.'
    success_url = reverse_lazy('sri:listado_tipos_monedas')


class DetalleTipoMoneda(BSModalReadView):
    model = SriTipoMoneda
    template_name = 'sri/tipo_moneda/detalle_tipo_moneda.html'


class EliminarTipoMoneda(BSModalDeleteView):
    model = SriTipoMoneda
    template_name = 'sri/tipo_moneda/eliminar_tipo_moneda.html'
    success_message = 'Success: El tipo de moneda fue eliminado.'
    success_url = reverse_lazy('sri:listado_tipos_monedas')


""" FORMULARIOS TARIFAS IVA """


class ListadoTarifaIva(ListView):
    model = SriTarifaIVA
    template_name = 'sri/tarifa_iva/listado_tarifas.html'
    context_object_name = 'tarifas_iva'


class CrearTarifaIva(BSModalCreateView):
    template_name = 'sri/tarifa_iva/crear_tarifa.html'
    form_class = TarifaIvaForm
    success_message = 'Success: La tarifa fue creada.'
    success_url = reverse_lazy('sri:listado_tarifa_iva')

    def form_valid(self, form):
        form.instance.usuario_creador = self.request.user
        return super(CrearTarifaIva, self).form_valid(form)


class ModificarTarifaIva(BSModalUpdateView):
    model = SriTarifaIVA
    template_name = 'sri/tarifa_iva/modificar_tarifa.html'
    form_class = TarifaIvaForm
    success_message = 'Success: La tarifa fue actualizada.'
    success_url = reverse_lazy('sri:listado_tarifa_iva')


class DetalleTarifaIva(BSModalReadView):
    model = SriTarifaIVA
    template_name = 'sri/tarifa_iva/detalle_tarifa.html'


class EliminarTarifaIva(BSModalDeleteView):
    model = SriTarifaIVA
    template_name = 'sri/tarifa_iva/eliminar_tarifa.html'
    success_message = 'Success: La tarifa de IVA fue eliminada.'
    success_url = reverse_lazy('sri:listado_tarifa_iva')


""" FORMULARIOS TARIFAS ICE """


class ListadoTarifaIce(ListView):
    model = SriTarifaICE
    template_name = 'sri/tarifa_ice/listado_tarifas.html'
    context_object_name = 'tarifas_ice'


class CrearTarifaIce(BSModalCreateView):
    template_name = 'sri/tarifa_ice/crear_tarifa.html'
    form_class = TarifaIceForm
    success_message = 'Success: La tarifa de ICE fue creada.'
    success_url = reverse_lazy('sri:listado_tarifa_ice')

    def form_valid(self, form):
        form.instance.usuario_creador = self.request.user
        return super(CrearTarifaIce, self).form_valid(form)


class ModificarTarifaIce(BSModalUpdateView):
    model = SriTarifaICE
    template_name = 'sri/tarifa_ice/modificar_tarifa.html'
    form_class = TarifaIvaForm
    success_message = 'Success: La tarifa de ICE fue actualizada.'
    success_url = reverse_lazy('sri:listado_tarifa_ice')


class DetalleTarifaIce(BSModalReadView):
    model = SriTarifaICE
    template_name = 'sri/tarifa_ice/detalle_tarifa.html'


class EliminarTarifaIce(BSModalDeleteView):
    model = SriTarifaICE
    template_name = 'sri/tarifa_ice/eliminar_tarifa.html'
    success_message = 'Success: La tarifa de ICE fue eliminada.'
    success_url = reverse_lazy('sri:listado_tarifa_ice')


""" FORMULARIOS TARIFAS IRBPNR """


class ListadoTarifaIrbpnr(ListView):
    model = SriTarifaIRBPNR
    template_name = 'sri/tarifa_irbpnr/listado_tarifas.html'
    context_object_name = 'tarifas_irbpnr'


class CrearTarifaIrbpnr(BSModalCreateView):
    template_name = 'sri/tarifa_irbpnr/crear_tarifa.html'
    form_class = TarifaIrbpnrForm
    success_message = 'Success: La tarifa de IRBPNR fue creada.'
    success_url = reverse_lazy('sri:listado_tarifa_irbpnr')

    def form_valid(self, form):
        form.instance.usuario_creador = self.request.user
        return super(CrearTarifaIrbpnr, self).form_valid(form)


class ModificarTarifaIrbpnr(BSModalUpdateView):
    model = SriTarifaIRBPNR
    template_name = 'sri/tarifa_irbpnr/modificar_tarifa.html'
    form_class = TarifaIrbpnrForm
    success_message = 'Success: La tarifa de IRBPNR fue actualizada.'
    success_url = reverse_lazy('sri:listado_tarifa_irbpnr')


class DetalleTarifaIrbpnr(BSModalReadView):
    model = SriTarifaIRBPNR
    template_name = 'sri/tarifa_irbpnr/detalle_tarifa.html'


class EliminarTarifaIrbpnr(BSModalDeleteView):
    model = SriTarifaIRBPNR
    template_name = 'sri/tarifa_irbpnr/eliminar_tarifa.html'
    success_message = 'Success: La tarifa de IRBPNR fue eliminada.'
    success_url = reverse_lazy('sri:listado_tarifa_irbpnr')


""" FORMULARIOS TIPOS DE IMPUESTOS """


class ListadoTiposImpuestos(ListView):
    model = SriTipoImpuesto
    template_name = 'sri/tipo_impuesto/tipos_impuestos.html'
    context_object_name = 'tipos_impuestos'


class CrearTipoImpuesto(BSModalCreateView):
    template_name = 'sri/tipo_impuesto/crear_tipo_impuesto.html'
    form_class = TipoImpuestoForm
    success_message = 'Success: El tipo de impuesto fue creado.'
    success_url = reverse_lazy('sri:listado_tipos_impuestos')

    def form_valid(self, form):
        form.instance.usuario_creador = self.request.user
        return super(CrearTipoImpuesto, self).form_valid(form)


class ModificarTipoImpuesto(BSModalUpdateView):
    model = SriTipoImpuesto
    template_name = 'sri/tipo_impuesto/modificar_tipo_impuesto.html'
    form_class = TipoImpuestoForm
    success_message = 'Success: El tipo de impuesto fue actualizado.'
    success_url = reverse_lazy('sri:listado_tipos_impuestos')


class DetalleTipoImpuesto(BSModalReadView):
    model = SriTipoImpuesto
    template_name = 'sri/tipo_impuesto/detalle_tipo_impuesto.html'


class EliminarTipoImpuesto(BSModalDeleteView):
    model = SriTipoImpuesto
    template_name = 'sri/tipo_impuesto/eliminar_tipo_impuesto.html'
    success_message = 'Success: El tipo de impuesto fue eliminada.'
    success_url = reverse_lazy('sri:listado_tipos_impuestos')
