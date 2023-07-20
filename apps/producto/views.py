from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from django.views import generic
from django.contrib.messages.views import SuccessMessageMixin

from bootstrap_modal_forms.generic import (BSModalCreateView,
                                           BSModalUpdateView,
                                           BSModalReadView,
                                           BSModalDeleteView)


from django.views.generic.edit import UpdateView, CreateView, DeleteView

from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Sum, F, Q, Func

from .models import Categoria, Producto
from .forms import CategoriaForm, ProductoForm, CategoryForm, \
    CategoryModalForm, CategoryBSModalForm
from apps.unidadmedida.models import UnidadMedida
from apps.almacen.models import ProductoResumen, TipoMovimiento, Kardex, \
    Almacen, ControlProducto
from apps.proveedor.forms import ProveedorForm

# raw sql
from django.db import connection
import datetime
from decimal import Decimal
from django.template.loader import render_to_string
from apps.administracion.models import Empresa

from django.db import IntegrityError
from django.contrib import messages

# Create your views here.


class ListadoCategorias(ListView):
    model = Categoria
    template_name = 'categoria/listado_categorias.html'
    context_object_name = 'all_categories'


class CrearCategoria(CreateView):
    template_name = 'categoria/categoria.html'
    form_class = CategoriaForm
    success_url = reverse_lazy('producto:listado_categorias')

    def form_valid(self, form):
        f = form.save(commit=False)
        f.usuario_creador = self.request.user
        f.empresa_id = self.request.session['company_id']
        f.save()
        return super(CrearCategoria, self).form_valid(form)


class ModificarCategoria(UpdateView):
    model = Categoria
    template_name = 'categoria/categoria.html'
    form_class = CategoriaForm
    success_url = reverse_lazy('producto:listado_categorias')


class DetalleCategoria(DetailView):
    model = Categoria
    template_name = 'categoria/detalle_categoria.html'


class EliminarCategoria(DeleteView):
    model = Categoria
    template_name = 'categoria/eliminar_categoria.html'
    success_url = reverse_lazy('producto:listado_categorias')


def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
    else:
        form = CategoryForm()
    return save_category_form(request, form, 'includes/partial_category_create.html')


def save_category_form(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.instance.usuario_creador = request.user
            form.instance.empresa_id = request.session['company_id']
            form.save()
            data['form_is_valid'] = True
            categories = Categoria.objects.all()
            data['html_category_list'] = render_to_string('includes/partial_category_dropdown_list_options.html', {
                'categories': categories
            })
        else:
            data['form_is_valid'] = False
    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)


class MixinFormInvalid:
    def form_invalid(self, form):
        response = super().form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response


class CrearCategoriaModal(SuccessMessageMixin, MixinFormInvalid,
                          generic.CreateView):
    model = Categoria
    template_name = 'categoria/categoria_modal.html'
    context_object_name = 'obj'
    form_class = CategoryModalForm
    success_url = reverse_lazy('producto:listado_categorias')
    success_message = 'Success: La categoría fue creada.'

    def form_valid(self, form):
        form.instance.usuario_creador = self.request.user
        form.instance.empresa_id = self.request.session['company_id']
        return super().form_valid(form)


class CrearCategoriaBSModal(BSModalCreateView):
    template_name = 'categoria/crear_categoria_bsmodal.html'
    form_class = CategoryBSModalForm
    success_message = 'Success: La categoría fue creada.'
    success_url = reverse_lazy('producto:listado_categorias')

    def form_valid(self, form):
        form.instance.usuario_creador = self.request.user
        form.instance.empresa_id = self.request.session['company_id']
        return super(CrearCategoriaBSModal, self).form_valid(form)


class ModificarCategoriaBSModal(BSModalUpdateView):
    model = Categoria
    template_name = 'categoria/modificar_categoria_bsmodal.html'
    form_class = CategoryBSModalForm
    success_message = 'Success: La categoría fue actualizada.'
    success_url = reverse_lazy('producto:listado_categorias')


class DetalleCategoriaBSModal(BSModalReadView):
    model = Categoria
    template_name = 'categoria/detalle_categoria_bsmodal.html'


class EliminarCategoriaBSModal(BSModalDeleteView):
    model = Categoria
    template_name = 'categoria/eliminar_categoria_bsmodal.html'
    success_message = 'Success: La categoría fue eliminada.'
    success_url = reverse_lazy('producto:listado_categorias')


"""def ajaxCrearUnidadModal(request):
    if request.method == 'POST':
        nombre = request.POST.get('unit_name', None)
        abbreviation = request.POST.get('unit_abbreviation', None)
        current_user = request.user

        unidad = Unidad()
        unidad.nombre = nombre
        unidad.abreviatura = abbreviation
        unidad.usuario_creador = current_user
        unidad.save()

        return JsonResponse({
            'success': True,
            'id': unidad.pk,
            'abbreviation': abbreviation,
            'name': nombre,
        })
"""


"""
Controlador Productos
"""

"""class IndexView(ListView):
    template_name = 'producto/index.html'

    def get(self, request):
        #queryset_list = ProductoResumen.objects.only('nombre', 'codigo_principal', 'unidad', 'precio_costo', 'precio_uno', 'descuento_uno', 'utilidad_uno', 'precio_neto_uno').order_by('nombre')
        queryset_list = ProductoResumen.objects.only('nombre', 'codigo_principal', 'unidad', 'precio_costo', 'precio_neto_uno', 'precio_neto_dos', 'precio_neto_tres', 'precio_neto_cuatro').order_by('nombre')
        template_name = self.template_name
        query = self.request.GET.get("q", '')
        paginate_by = self.request.GET.get('rpp', 10)

        print(query)

        if query:
            queryset_list = queryset_list.filter(
                    Q(nombre__icontains=query) |
                    Q(codigo_principal__icontains=query)
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


class IndexView(ListView):
    # model = ProductoResumen
    # template_name = 'producto/index.html'
    # context_object_name = 'all_products'

    template_name = 'producto/index.html'

    def get_queryset(self):
        return ProductoResumen.objects.none()

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)

        context['almacenes'] = Almacen.objects.filter(activo=True)

        return context


def ajax_producto_resumen(request):
    if request.method == 'POST':
        if request.is_ajax():
            almacen_id = request.POST.get('almacen_id', None)

            try:
                id = int(almacen_id)
                if id > 0:
                    query = """
                        select prod.producto_id, prod.codigo_principal, prod.nombre, ctrl_prod.stock, und.abreviatura as unidad, case when coalesce(ctrl_prod.precio, 0) > 0 then ctrl_prod.precio else prod.precio_costo end as costo, prod.precio_uno, prod.precio_dos, prod.precio_tres, prod.precio_cuatro
                        from almacen_controlproducto ctrl_prod
                        left join producto_producto prod on ctrl_prod.producto_id = prod.producto_id
                        inner join unidadmedida_unidadmedida und on prod.unidad_principal_id = und.unidad_medida_id
                        where ctrl_prod.almacen_id = %s
                        order by prod.nombre
                    """ % (id)
                else:
                    # todos los almacenes
                    query = """
                        select prod.producto_id, prod.codigo_principal, prod.nombre, coalesce(ctrl_prod.stock, 0) as stock, und.abreviatura as unidad, case when coalesce(ctrl_prod.precio, 0) > 0 then ctrl_prod.precio else prod.precio_costo end as costo, prod.precio_uno, prod.precio_dos, prod.precio_tres, prod.precio_cuatro
                        from producto_producto prod
                        left join almacen_controlproducto ctrl_prod on prod.producto_id = ctrl_prod.producto_id
                        inner join unidadmedida_unidadmedida und on prod.unidad_principal_id = und.unidad_medida_id
                        order by prod.nombre
                    """
            except ValueError:
                # ningún valor seleccionado
                id_aux = 0
                query = """
                    select prod.producto_id, prod.codigo_principal, prod.nombre, ctrl_prod.stock, und.abreviatura as unidad, ctrl_prod.precio as costo, prod.precio_uno, prod.precio_dos, prod.precio_tres, prod.precio_cuatro
                    from almacen_controlproducto ctrl_prod
                    left join producto_producto prod on ctrl_prod.producto_id = prod.producto_id
                    inner join unidadmedida_unidadmedida und on prod.unidad_principal_id = und.unidad_medida_id
                    where ctrl_prod.almacen_id = %s
                    order by prod.nombre
                """ % (id_aux)

            with connection.cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
                results = []
                columns = (
                    'producto_id', 'codigo_principal', 'nombre', 'stock', 'unidad', 'costo', 'precio_uno', 'precio_dos', 'precio_tres', 'precio_cuatro'
                )
                for row in rows:
                    results.append(dict(zip(columns, row)))
            return JsonResponse(results, safe=False)


'''
def ajax_listado_productos(request):
    almacen_id = request.POST.get('almacen_id', None)
    try:
        id = int(almacen_id)
        if id > 0:
            query = """
                select producto_producto.nombre, producto_producto.codigo_principal, producto_producto.producto_id, coalesce(almacen_controlproducto.stock, 0) as stock, coalesce(almacen_controlproducto.precio, 0) as costo, producto_producto.precio_uno, producto_producto.precio_dos, producto_producto.precio_tres, producto_producto.precio_cuatro
                from almacen_controlproducto
                left join producto_producto on producto_producto.producto_id = almacen_controlproducto.producto_id
                where almacen_id = %s
            """ % (id)
        else:
            # todos los almacenes
            query = """
                select producto_producto.nombre, producto_producto.codigo_principal, producto_producto.producto_id, coalesce(almacen_controlproducto.stock, 0) as stock, coalesce(almacen_controlproducto.precio, 0) as costo, producto_producto.precio_uno, producto_producto.precio_dos, producto_producto.precio_tres, producto_producto.precio_cuatro
                from producto_producto
                left join almacen_controlproducto on producto_producto.producto_id = almacen_controlproducto.producto_id
            """
    except ValueError:
        # ningún almacén seleccionado
        id_aux = 0
        query = """
            select producto_producto.nombre, producto_producto.codigo_principal, producto_producto.producto_id, coalesce(almacen_controlproducto.stock, 0) as stock, coalesce(almacen_controlproducto.precio, 0) as costo, producto_producto.precio_uno, producto_producto.precio_dos, producto_producto.precio_tres, producto_producto.precio_cuatro
            from producto_producto
            left join almacen_controlproducto on producto_producto.producto_id = almacen_controlproducto.producto_id
            where almacen_id = %s
        """ % (id_aux)

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        results = []
        columns = (
            'nombre', 'codigo_principal', 'producto_id', 'stock', 'costo', 'precio_uno', 'precio_dos', 'precio_tres', 'precio_cuatro'
        )
        for row in rows:
            results.append(dict(zip(columns, row)))
    return JsonResponse(results, safe=False)
'''


def actualizar_costos_control(request):
    from apps.almacen.models import ControlProducto

    trans_obj = Kardex.objects.all().order_by('pk')
    for row in trans_obj:
        producto_id = row.producto_id
        cantidad = row.cantidad_total
        costo = row.precio_total

        control = ControlProducto.objects.filter(producto_id=producto_id)[0]
        control.stock = cantidad
        control.precio = costo
        control.save()

    now = datetime.datetime.now()
    html = "<html><body>It is now %s.</body></html>" % now
    return HttpResponse(html)


def actualizar_costos(request):
    productos_obj = Kardex.objects.filter(pk__gte=2828).order_by('pk')

    for row in productos_obj:

        trans_id = row.kardex_id
        # print("TRANS_ID=%s" % (trans_id))

        kardex = Kardex.objects.get(pk=trans_id)

        producto_id = row.producto_id
        almacen_id = row.almacen_id
        tipo_trans = row.tipo
        qty = row.cantidad
        fecha_operacion_obj = row.created_at

        if tipo_trans == 1:
            try:
                kardex_ant = Kardex.objects.filter(producto_id=producto_id,
                                                   almacen_id=almacen_id,
                                                   pk__lt=trans_id).latest('pk')

                cost = kardex_ant.precio_total
                valor_total = qty * cost

                stock_cantidad = qty + kardex_ant.cantidad_total
                stock_total = valor_total + kardex_ant.valor_total
                if stock_cantidad != 0:
                    stock_costo = stock_total / stock_cantidad
                else:
                    stock_costo = 0

                # kardex.cantidad = qty
                kardex.costo = cost
                kardex.total = valor_total

                kardex.cantidad_total = stock_cantidad
                kardex.valor_total = stock_total
                kardex.precio_total = stock_costo
            except Kardex.DoesNotExist:
                aux_prod = Producto.objects.get(pk=producto_id)
                cost = aux_prod.precio_costo

                valor_total = qty * cost
                kardex.costo = cost
                kardex.total = valor_total

                kardex.cantidad_total = qty
                kardex.precio_total = cost
                kardex.valor_total = valor_total
            kardex.save()

        elif tipo_trans == 2:
            try:
                kardex_ant = Kardex.objects.filter(producto_id=producto_id,
                                                   almacen_id=almacen_id,
                                                   pk__lt=trans_id).latest('pk')
                cost = kardex_ant.precio_total
                valor_total = qty * cost

                if trans_id == 2837:
                    print("PRODUCTO_ID=%s" % (producto_id))
                    print("ALMACEN_ID=%s" % (almacen_id))
                    print("FECHA=%s" % (fecha_operacion_obj))

                    print("TRANS_ID=%s" % (trans_id))
                    print("K STOCK=%s" % (kardex_ant.cantidad_total))
                    print("K TOTAL=%s" % (kardex_ant.valor_total))

                stock_cantidad = kardex_ant.cantidad_total - qty
                stock_total = kardex_ant.valor_total - valor_total
                if stock_cantidad != 0:
                    stock_costo = stock_total / stock_cantidad
                else:
                    stock_costo = 0

                kardex.costo = cost
                kardex.total = valor_total

                kardex.cantidad_total = stock_cantidad
                kardex.valor_total = stock_total
                kardex.precio_total = stock_costo
            except Kardex.DoesNotExist:
                aux_prod = Producto.objects.get(pk=producto_id)
                cost = aux_prod.precio_costo

                valor_total = qty * cost
                kardex.costo = cost
                kardex.total = valor_total

                kardex.cantidad_total = qty
                kardex.precio_total = cost
                kardex.valor_total = valor_total

            kardex.save()

    now = datetime.datetime.now()
    html = "<html><body>It is now %s.</body></html>" % now
    return HttpResponse(html)

class CrearProducto(CreateView):
    template_name = 'producto/producto.html'
    form_class = ProductoForm
    success_url = reverse_lazy('producto:listado_productos')

    def form_valid(self, form):
        producto = form.save(commit=False)
        producto.usuario_creador = self.request.user
        producto.empresa_id = self.request.session['company_id']
        producto.save()

        if producto.cantidad_inicial:
            agregarInventarioInicial(producto, self.request)

        return super(CrearProducto, self).form_valid(form)


class EditarProducto(UpdateView):
    model = Producto
    template_name = 'producto/producto.html'
    form_class = ProductoForm
    success_url = reverse_lazy('producto:listado_productos')


class DetalleProducto(DetailView):
    model = Producto
    template_name = 'producto/detalle_producto.html'


class EliminarProducto(DeleteView):
    model = Producto
    template_name = 'producto/eliminar_producto.html'
    success_url = reverse_lazy('producto:listado_productos')

    def delete(self, request, *args, **kwargs):
        try:
            return(super().delete(request, *args, **kwargs))
        except IntegrityError:
            messages.error(request, "DB Error de integridad")
            return render(request, template_name=self.template_name, context=self.get_context_data())

    """def get(self, request, *args, **kwargs):
        try:
            producto = Producto.objects.get(pk=self.kwargs[self.pk_url_kwarg])
            producto.delete()

            my_render = render(request, self.success_url)
            my_render = render(request, self.success_url)
        except Producto.DoesNotExist:
            messages.error(request, "El producto no existe")
            my_render = render(request, self.success_url)
        except IntegrityError:
            messages.error(request, "DB Error de Integridad")
            my_render = render(request, self.success_url)

        return my_render"""


class DetalleProductoModal(DetailView):
    model = Producto
    template_name = 'producto/detalle_producto_modal.html'


def agregarInventarioInicial(producto, request=None):
    unidad_obj = producto.unidad_principal
    almacen_obj = Almacen.objects.filter(es_principal=True)[0]

    my_company_id = request.session['company_id']
    empresa_obj = Empresa.objects.get(pk=my_company_id)
    tipo_movimiento_obj = TipoMovimiento.objects.filter(codigo='INV_INI')[0]
    if Kardex.objects.filter(producto=producto, movimiento__codigo='INV_INI').exists():
        return False
    else:
        trans = Kardex()
        trans.movimiento = tipo_movimiento_obj
        trans.orden_id = 0
        trans.numero_comprobante = 0

        trans.producto = producto
        trans.unidad = unidad_obj

        trans.referencia = "Inventario Inicial"
        #trans.cantidad = 0
        #trans.costo = 0
        #trans.total = 0
        trans.cantidad = producto.cantidad_inicial
        trans.costo = producto.precio_costo
        trans.total = producto.cantidad_inicial * producto.precio_costo

        trans.cantidad_total = producto.cantidad_inicial
        trans.precio_total = producto.precio_costo
        trans.valor_total = producto.cantidad_inicial * producto.precio_costo

        # trans.empresa = producto.usuario_creador.perfil.empresa
        trans.empresa = empresa_obj
        trans.almacen = almacen_obj
        trans.usuario_creador = producto.usuario_creador

        trans.save()

        if (trans.cantidad_total == 0):
            precio_control = 0
        else:
            precio_control = trans.valor_total / trans.cantidad_total

        control_producto = ControlProducto.objects.update_or_create(
            almacen=trans.almacen,
            producto=trans.producto,
            defaults={'stock': trans.cantidad_total,
                      'precio': precio_control}
        )

        return True


def export_products_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="products.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Productos')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Producto', 'Código', 'Stock', 'Unidad',
               'Costo', '% Utilidad', '% Descuento', '$ P.V.P']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    rows = Producto.objects.all().values_list('nombre', 'precio_costo', 'unidad_principal_id',
                                              'utilidad_uno', 'descuento_uno', 'precio_uno')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response


def ajaxBuscarProductoDB(request):
    if request.method == "GET":
        if request.is_ajax():
            search_string = request.GET.get('search_string', None)

            # item.creator = owner or item.moderated = False
            producto_obj = Producto.objects.filter(
                Q(nombre=search_string) | Q(codigo_principal=search_string))
            if producto_obj.exists():

                return JsonResponse({
                    'success': True,
                    # 'product': 'SAMSUNG PRINTER XPRESS ML-2165W',
                    # 'productId': '1',
                    # 'cost': '65.00',
                    'product': producto_obj[0].nombre,
                    'productId': producto_obj[0].producto_id,
                    'cost': producto_obj[0].precio_costo,
                    'unitId': producto_obj[0].unidad_principal_id
                })
            else:
                return JsonResponse({
                    'success': False,
                })
