from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView, DeleteView

from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Sum, F, Q, Func

from .models import Proveedor, ProveedorResumen
from .forms import ProveedorForm
from apps.sri.models import SriTipoIdentificacion

# Create your views here.


class ProveedoresIndexView(ListView):
    model = ProveedorResumen
    template_name = 'proveedor/listado_proveedores.html'
    context_object_name = 'all_suppliers'


class CrearProveedor(CreateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'proveedor/proveedor.html'
    success_url = reverse_lazy('proveedor:listado_proveedores')

    def form_valid(self, form):
        proveedor = form.save(commit=False)
        proveedor.usuario_creador = self.request.user
        proveedor.empresa_id = self.request.session['company_id']
        proveedor.save()
        return super(CrearProveedor, self).form_valid(form)

        #proveedor = form.save(commit=False)
        #proveedor.usuario_creador_id = UserProfile.objects.get(user=self.request.user)
        # proveedor.save()
        # return super(CrearProveedor, self).form_valid(form)


class EditarProveedor(UpdateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'proveedor/proveedor.html'
    success_url = reverse_lazy('proveedor:listado_proveedores')


class DetalleProveedor(DetailView):
    model = Proveedor
    template_name = 'proveedor/detalle_proveedor.html'


class EliminarProveedor(DeleteView):
    model = Proveedor
    template_name = 'proveedor/eliminar_proveedor.html'
    success_url = reverse_lazy('proveedor:listado_proveedores')


"""
Proveedor Modal, desactivado llamda desde producto
"""

"""
def ajaxCrearProveedorModal(request):
    if request.method == 'POST':
        tipo_identificacion = request.POST.get('supplier_tipo_identificacion', None)
        identificacion = request.POST.get('supplier_identificacion', None)
        nombre = request.POST.get('supplier_razon_social', None)
        direccion = request.POST.get('supplier_direccion', None)
        obligado_contabilidad = request.POST.get('supplier_obligado_contabilidad', None)
        telefono = request.POST.get('supplier_telefono', None)
        extension = request.POST.get('supplier_extension', None)
        celular = request.POST.get('supplier_celular', None)
        email = request.POST.get('supplier_email', None)

        current_user = request.user
        tipo_identificacion_obj = SriTipoIdentificacion.objects.filter(codigo=tipo_identificacion)[
            0]
        contabilidad = False
        if obligado_contabilidad:
            contabilidad = True

        proveedor = Proveedor()
        proveedor.identificacion_tipo = tipo_identificacion_obj
        proveedor.identificacion = identificacion
        proveedor.nombre = nombre
        proveedor.direccion = direccion
        proveedor.obligado_contabilidad = contabilidad
        proveedor.telefono = telefono
        proveedor.extension = extension
        proveedor.celular = celular
        proveedor.email = email
        proveedor.usuario_creador = current_user
        proveedor.save()

        return JsonResponse({
            'success': True,
            'id': proveedor.pk,
            'name': nombre
        })
"""
