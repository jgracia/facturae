from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView, DeleteView

from django.template.loader import render_to_string
from django.http import JsonResponse

from .models import UnidadMedida
from .forms import UnidadMedidaForm, ModalUnitForm
# Create your views here.


"""
Unidades para productos
"""


class ListadoUnidades(ListView):
    model = UnidadMedida
    template_name = 'unidad/listado_unidades.html'
    context_object_name = 'all_units'


class CrearUnidad(CreateView):
    template_name = 'unidad/unidad.html'
    form_class = UnidadMedidaForm
    success_url = reverse_lazy('unidadmedida:listado_unidades')

    def form_valid(self, form):
        f = form.save(commit=False)
        f.usuario_creador = self.request.user
        f.empresa_id = self.request.session['company_id']
        f.save()
        return super(CrearUnidad, self).form_valid(form)


class ModificarUnidad(UpdateView):
    model = UnidadMedida
    template_name = 'unidad/unidad.html'
    form_class = UnidadMedidaForm
    success_url = reverse_lazy('unidadmedida:listado_unidades')


class DetalleUnidad(DetailView):
    model = UnidadMedida
    template_name = 'unidad/detalle_unidad.html'


class EliminarUnidad(DeleteView):
    model = UnidadMedida
    template_name = 'unidad/eliminar_unidad.html'
    success_url = reverse_lazy('unidadmedida:listado_unidades')


def unit_create(request):
    if request.method == 'POST':
        form = ModalUnitForm(request.POST)
    else:
        form = ModalUnitForm()
    return save_unit_form(request, form, 'includes/partial_unit_create.html')


def save_unit_form(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.instance.usuario_creador = request.user
            form.instance.empresa_id = request.session['company_id']
            form.save()
            data['form_is_valid'] = True
            units = UnidadMedida.objects.all()
            data['html_unit_list'] = render_to_string('includes/partial_unit_dropdown_list_options.html', {
                'units': units
            })
        else:
            data['form_is_valid'] = False
    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)
