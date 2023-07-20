from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView, DeleteView

from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Sum, F, Q, Func

from .models import Cliente, ClienteResumen
from .forms import ClienteForm

# Create your views here.


class ClientesIndexView(ListView):
    model = ClienteResumen
    template_name = 'cliente/listado_clientes.html'
    context_object_name = 'all_customers'


class CrearCliente(CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'cliente/cliente.html'
    success_url = reverse_lazy('cliente:listado_clientes')

    def form_valid(self, form):
        cliente = form.save(commit=False)
        cliente.usuario_creador = self.request.user
        cliente.empresa_id = self.request.session['company_id']
        cliente.save()
        return super(CrearCliente, self).form_valid(form)


class EditarCliente(UpdateView):
    model = Cliente
    template_name = 'cliente/cliente.html'
    form_class = ClienteForm
    success_url = reverse_lazy('cliente:listado_clientes')


class DetalleCliente(DetailView):
    model = Cliente
    template_name = 'cliente/detalle_cliente.html'


class EliminarCliente(DeleteView):
    model = Cliente
    template_name = 'cliente/eliminar_cliente.html'
    form_class = ClienteForm
    success_url = reverse_lazy('cliente:listado_clientes')
