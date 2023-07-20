from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView, DeleteView

from .models import EntidadFinanciera, TarjetaBancaria, Empresa, Secuencia
from apps.usuario.decorators import supervisor_required

from .forms import BancoForm, TarjetaForm, EmpresaForm, SecuenciaForm

from bootstrap_modal_forms.generic import (BSModalCreateView,
                                           BSModalUpdateView,
                                           BSModalReadView,
                                           BSModalDeleteView)

# Create your views here.


class ListadoBancos(ListView):
    model = EntidadFinanciera
    template_name = 'administracion/banco/bancos.html'
    context_object_name = 'bancos'


class CrearBanco(BSModalCreateView):
    template_name = 'administracion/banco/crear_banco.html'
    form_class = BancoForm
    success_message = 'Success: La entidad financiera fue creada.'
    success_url = reverse_lazy('administracion:listado_bancos')

    def form_valid(self, form):
        form.instance.usuario_creador = self.request.user
        return super(CrearBanco, self).form_valid(form)


class ModificarBanco(BSModalUpdateView):
    model = EntidadFinanciera
    template_name = 'administracion/banco/modificar_banco.html'
    form_class = BancoForm
    success_message = 'Success: La entidad financiera fue actualizada.'
    success_url = reverse_lazy('administracion:listado_bancos')


class DetalleBanco(BSModalReadView):
    model = EntidadFinanciera
    template_name = 'administracion/banco/detalle_banco.html'


class EliminarBanco(BSModalDeleteView):
    model = EntidadFinanciera
    template_name = 'administracion/banco/eliminar_banco.html'
    success_message = 'Success: La entidad financiera fue eliminada.'
    success_url = reverse_lazy('administracion:listado_bancos')


""" FORMULARIOS TARJETAS """


class ListadoTarjetas(ListView):
    model = TarjetaBancaria
    template_name = 'administracion/tarjeta/tarjetas.html'
    context_object_name = 'tarjetas'


class CrearTarjeta(BSModalCreateView):
    template_name = 'administracion/tarjeta/crear_tarjeta.html'
    form_class = TarjetaForm
    success_message = 'Success: La tarjeta fue creada.'
    success_url = reverse_lazy('administracion:listado_tarjetas')

    def form_valid(self, form):
        form.instance.usuario_creador = self.request.user
        return super(CrearTarjeta, self).form_valid(form)


class ModificarTarjeta(BSModalUpdateView):
    model = TarjetaBancaria
    template_name = 'administracion/tarjeta/modificar_tarjeta.html'
    form_class = TarjetaForm
    success_message = 'Success:La Tarjeta fue actualizado.'
    success_url = reverse_lazy('administracion:listado_tarjetas')


class DetalleTarjeta(BSModalReadView):
    model = TarjetaBancaria
    template_name = 'administracion/tarjeta/detalle_tarjeta.html'


class EliminarTarjeta(BSModalDeleteView):
    model = TarjetaBancaria
    template_name = 'administracion/tarjeta/eliminar_tarjeta.html'
    success_message = 'Success: La tarjeta fue eliminada.'
    success_url = reverse_lazy('administracion:listado_bancos')


""" FORMULARIOS EMPRESA """


@method_decorator(supervisor_required, name='dispatch')
class ListadoEmpresas(ListView):
    model = Empresa
    template_name = 'administracion/empresa/empresas.html'
    context_object_name = 'empresas'

    def get_queryset(self):
        return Empresa.objects.filter()


class CrearEmpresa(CreateView):
    template_name = 'administracion/empresa/empresa.html'
    model = Empresa
    form_class = EmpresaForm
    success_url = reverse_lazy('administracion:listado_empresas')

    def form_valid(self, form):
        form.instance.usuario_creador = self.request.user
        return super(CrearEmpresa, self).form_valid(form)


class ModificarEmpresa(UpdateView):
    model = Empresa
    template_name = 'administracion/empresa/empresa.html'
    form_class = EmpresaForm
    success_url = reverse_lazy('administracion:listado_empresas')


class DetalleEmpresa(DetailView):
    model = Empresa
    template_name = 'administracion/empresa/detalle_empresa.html'


class EliminarEmpresa(DeleteView):
    model = Empresa
    template_name = 'administracion/empresa/eliminar_empresa.html'
    success_url = reverse_lazy('administracion:listado_empresas')


""" FORMULARIOS SECUENCIAS """


class ListadoSecuencias(ListView):
    model = Secuencia
    template_name = 'administracion/secuencia/secuencias.html'
    context_object_name = 'secuencias'

    def get_queryset(self):
        return Secuencia.objects.filter()


class CrearSecuencia(CreateView):
    template_name = 'administracion/secuencia/secuencia.html'
    model = Secuencia
    form_class = SecuenciaForm
    success_url = reverse_lazy('administracion:listado_secuencias')

    def form_valid(self, form):
        form.instance.usuario_creador = self.request.user
        return super(CrearSecuencia, self).form_valid(form)


class EditarSecuencia(UpdateView):
    model = Secuencia
    template_name = 'administracion/secuencia/secuencia.html'
    form_class = SecuenciaForm
    success_url = reverse_lazy('administracion:listado_secuencias')


class DetalleSecuencia(DetailView):
    model = Secuencia
    template_name = 'administracion/secuencia/detalle_secuencia.html'


class EliminarSecuencia(DeleteView):
    model = Secuencia
    template_name = 'administracion/secuencia/eliminar_secuencia.html'
    success_url = reverse_lazy('administracion:listado_secuencias')
