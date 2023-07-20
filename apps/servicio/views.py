from django.shortcuts import render
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Sum, F, Q, Func

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView, DeleteView

from .models import Servicio
from .forms import ServicioForm

# Create your views here.


"""class ListadoServicios(ListView):
    template_name = 'servicio/listado_servicios.html'

    def get(self, request):
        queryset_list = Servicio.objects.only('nombre', 'descripcion', 'activo').order_by('nombre')
        template_name = self.template_name
        query = self.request.GET.get("q", '')
        paginate_by = self.request.GET.get('rpp', 10)

        if query:
            queryset_list = queryset_list.filter(
                    Q(nombre__icontains=query) |
                    Q(descripcion__icontains=query)
                    ).distinct().order_by('nombre')
        try:
            page = int(request.GET.get('page', 1))
            paginate_by = int(paginate_by)
            paginator = Paginator(queryset_list, paginate_by, request=request)
            queryset_list = paginator.page(page)
        except ValueError:
            raise Http404

        return render(request, template_name, {
            'page': queryset_list,
        })
"""


class ListadoServicios(ListView):
    model = Servicio
    template_name = 'servicio/listado_servicios.html'
    context_object_name = 'all_services'


class CrearServicio(CreateView):
    template_name = 'servicio/servicio.html'
    form_class = ServicioForm
    success_url = reverse_lazy('servicio:listado_servicios')

    def form_valid(self, form):
        f = form.save(commit=False)
        f.usuario_creador = self.request.user
        f.empresa_id = self.request.session['company_id']
        f.save()
        return super(CrearServicio, self).form_valid(form)


class EditarServicio(UpdateView):
    model = Servicio
    template_name = 'servicio/servicio.html'
    form_class = ServicioForm
    success_url = reverse_lazy('servicio:listado_servicios')


class DetalleServicio(DetailView):
    model = Servicio
    template_name = 'servicio/detalle_servicio.html'


class EliminarServicio(DeleteView):
    model = Servicio
    template_name = 'servicio/eliminar_servicio.html'
    success_url = reverse_lazy('servicio:listado_servicios')


def busqueda_servicios(request):
    if request.method == "GET":
        if request.is_ajax():
            servicios = Servicio.objects.all().values('servicio_id', 'nombre')
            lista_servicios = list(servicios)  # important: convert the QuerySet to a list object
            return JsonResponse(lista_servicios, safe=False)


"""
class ListadoUnidades(ListView):
    model = UnidadMedida
    template_name = 'servicio/unidad/listado_unidades.html'
    context_object_name = 'all_units'


class CrearUnidad(CreateView):
    template_name = 'app/unidad/unidad.html'
    form_class = UnidadMedidaForm
    success_url = reverse_lazy('servicio:listado_unidades')

    def form_valid(self, form):
        f = form.save(commit=False)
        f.usuario_creador = self.request.user
        f.save()
        return super(CrearUnidad, self).form_valid(form)


class ModificarUnidad(UpdateView):
    model = UnidadMedida
    template_name = 'servicio/unidad/unidad.html'
    form_class = UnidadMedidaForm
    success_url = reverse_lazy('servicio:listado_unidades')


class DetalleUnidad(DetailView):
    model = UnidadMedida
    template_name = 'servicio/unidad/detalle_unidad.html'


class EliminarUnidad(DeleteView):
    model = UnidadMedida
    template_name = 'servicio/unidad/eliminar_unidad.html'
    success_url = reverse_lazy('producto:listado_unidades')
"""
