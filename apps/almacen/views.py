from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Sum, F, Q, Func

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView, DeleteView

import json
import datetime
from pytz import timezone
from datetime import timedelta

from .models import Almacen, InventarioExistencia, InventarioResumen, \
    Kardex, ProductoResumen, TipoMovimiento, \
    ProductoConsolidado, ControlProducto
from apps.cesta.models import Cesta, Item as CestaItem, \
    Lote as CestaLote, Opcion as ItemOpcion
from .forms import AlmacenForm
from apps.producto.models import Producto

from apps.unidadmedida.models import UnidadMedida
from django.core import serializers
from rest_framework.views import APIView
from .serializers import KardexSerializer

# raw sql
from django.db import connection

# Create your views here.

import locale
# Set to users preferred locale:
locale.setlocale(locale.LC_ALL, '')


class ListadoAlmacenes(ListView):
    model = Almacen
    template_name = 'almacen/listado_almacenes.html'
    context_object_name = 'all_cellars'


class CrearAlmacen(CreateView):
    template_name = 'almacen/almacen.html'
    form_class = AlmacenForm
    success_url = reverse_lazy('almacen:listado_almacenes')

    def form_valid(self, form):
        f = form.save(commit=False)
        f.usuario_creador = self.request.user
        f.empresa_id = self.request.session['company_id']
        f.save()
        return super(CrearAlmacen, self).form_valid(form)


class EditarAlmacen(UpdateView):
    model = Almacen
    template_name = 'almacen/almacen.html'
    form_class = AlmacenForm
    success_url = reverse_lazy('almacen:listado_almacenes')


class DetalleAlmacen(DetailView):
    model = Almacen
    template_name = 'almacen/detalle_almacen.html'


class EliminarAlmacen(DeleteView):
    model = Almacen
    template_name = 'almacen/eliminar_almacen.html'
    success_url = reverse_lazy('almacen:listado_almacenes')


"""
Funciones Inventario
"""


class ExistenciasIndexView(ListView):
    # model = InventarioExistencia
    model = InventarioResumen
    template_name = 'almacen/listado_existencias.html'
    context_object_name = 'all_stock'


class ListadoAjustes(ListView):
    template_name = 'almacen/listado_ajustes.html'

    def get_queryset(self):
        return Kardex.objects.none()


def ajax_listado_ajustes(request):
    from_date = request.POST.get("startDate")  # + ' 00:00:00'
    to_date = request.POST.get("endDate")  # + ' 23:59:59'
    format_str = '%Y-%m-%d'

    # format_str = '%Y-%m-%d %H:%M:%S'
    start_date = datetime.datetime.strptime(from_date, format_str)
    end_date = datetime.datetime.strptime(to_date, format_str) + timedelta(days=1)

    raw_data = Kardex.objects.filter(
        Q(movimiento__es_ajuste=True) &
        Q(created_at__date__range=(start_date, end_date))
    ).order_by('-created_at')

    dictionary = {}
    if (len(raw_data) > 0):
        result = []
        for value in raw_data:
            cantidad = 0
            pos_substr = value.referencia.find('=> ')
            if pos_substr > 0:
                substr = value.referencia[pos_substr + 3:]
                cantidad = substr
            result.append({
                'id': value.pk,
                # 'fecha_operacion': format(value.created_at, '%d-%b-%Y %H:%M:%S'),
                'producto': value.producto.nombre,
                'almacen': value.almacen.codigo,
                'motivo': value.movimiento.descripcion,
                'cantidad_original': cantidad,
                'cantidad_ajustada': value.cantidad,
                'nueva_cantidad': value.cantidad_total,
                'costo': str(value.precio_total)
            })

        dictionary = list(result)  # diccionario

    return JsonResponse(dictionary, safe=False)


class AjusteInventarioView(ListView):
    template_name = 'almacen/ajuste.html'

    def get_queryset(self):
        return TipoMovimiento.objects.filter(Q(es_ajuste=True) | Q(es_existencia=True)).order_by('descripcion')

    def get_context_data(self, **kwargs):
        context = super(AjusteInventarioView, self).get_context_data(**kwargs)

        today = datetime.date.today()
        context['fecha_operacion'] = format(today, '%Y-%m-%d')
        context['unidades'] = UnidadMedida.objects.all()
        context['almacenes'] = Almacen.objects.filter(activo=True)

        return context


""" FUNCIONES CALCULO INVENTARIO """


def getExistencia(producto_obj):
    saldo_obj = ProductoResumen.objects.filter(
        producto_id=producto_obj.producto_id).only('existencia')
    if saldo_obj.exists():
        return saldo_obj[0].existencia
    else:
        return 0


class KardexIndexView(ListView):
    template_name = 'almacen/kardex.html'

    def get_queryset(self):
        return Kardex.objects.none()

    def get_context_data(self, **kwargs):
        context = super(KardexIndexView, self).get_context_data(**kwargs)

        # today = datetime.date.today()
        # context['fecha_operacion'] = format(today, '%Y-%m-%d')
        # context['unidades'] = Unidad.objects.all()

        # products = Producto.objects.all().values('producto_id', 'nombre', 'codigo_principal').order_by('nombre')

        context['almacenes'] = Almacen.objects.filter(activo=True).order_by('descripcion')
        # context['productos'] = products
        return context


def kardex_json(request):
    if request.method == "GET":
        if request.is_ajax():
            from_date = request.GET.get('from_date', None)
            to_date = request.GET.get('to_date', None)
            producto_id = int(request.GET.get('dataId', None))
            almacen_id = int(request.GET.get('almacenId', None))

            format_str = '%Y/%m/%d'
            start_date = datetime.datetime.strptime(from_date, format_str).date()
            end_date = datetime.datetime.strptime(to_date, format_str).date()

            # raw_data = Kardex.objects.filter(created_at__date__range=(start_date, end_date), producto_id=producto_id)
            # raw_data = Kardex.objects.filter(producto_id=producto_id)
            # raw_data = Kardex.objects.filter(producto_id=producto_id, almacen_id=almacen_id)
            '''raw_data = Kardex.objects.filter(
                    Q(producto__producto_id__icontains=producto_id) &
                    Q(almacen__almacen_id__icontains=almacen_id) &
                    Q(created_at__date__range=(start_date, end_date))
                    ).order_by('-kardex_id')'''

            raw_data = Kardex.objects.filter(
                Q(producto_id=producto_id) &
                Q(almacen_id=almacen_id) &
                Q(created_at__date__range=(start_date, end_date))
            ).order_by('-kardex_id')

            if (len(raw_data) > 0):
                result = []
                for value in raw_data:
                    movimiento = ''
                    balance_cantidad = value.cantidad_total
                    balance_costo = value.precio_total

                    movimiento_cantidad = value.cantidad
                    movimiento_precio = value.costo
                    if value.movimiento.es_existencia:
                        movimiento = 'Existencia'
                    elif value.movimiento.es_entrada:
                        movimiento = 'Entrada'
                    else:
                        movimiento = 'Salida'

                    result.append({
                        'fecha': format(value.created_at, '%d-%b-%Y %H:%M:%S'),
                        'comprobante': value.numero_comprobante,
                        'almacen': value.almacen.descripcion,
                        'descripcion': value.movimiento.descripcion,
                        'movimiento': movimiento,
                        'unidad': value.unidad.abreviatura,
                        'movimiento_cantidad': str(movimiento_cantidad),
                        'movimiento_precio': str(movimiento_precio),
                        'balance_cantidad': str(balance_cantidad),
                        'balance_costo': str(balance_costo),
                    })

                data = json.dumps(result)

                almacen_obj = Almacen.objects.get(pk=almacen_id)
                producto_obj = Producto.objects.get(pk=producto_id)
                control_producto = ControlProducto.objects.filter(
                    producto=producto_obj, almacen=almacen_obj)
                if control_producto.exists():
                    existencia = control_producto[0].stock
                    precio_costo = control_producto[0].precio
                    producto = control_producto[0].producto.nombre
                    precio_uno = control_producto[0].producto.precio_uno
                    precio_dos = control_producto[0].producto.precio_dos
                    precio_tres = control_producto[0].producto.precio_tres
                    precio_cuatro = control_producto[0].producto.precio_cuatro
                else:
                    existencia = 0
                    precio_costo = 0
                    producto_id = ''
                    producto = ''
                    precio_uno = 0
                    precio_dos = 0
                    precio_tres = 0
                    precio_cuatro = 0

                return JsonResponse({
                    'success': True,
                    'producto_id': producto_id,
                    'producto': producto,
                    'existencia': existencia,
                    'costo': precio_costo,
                    'precio_uno': precio_uno,
                    'precio_dos': precio_dos,
                    'precio_tres': precio_tres,
                    'precio_cuatro': precio_cuatro,
                    'data': data,
                })
            else:
                return JsonResponse({
                    'success': False,
                    'producto_id': '',
                    'producto': '',
                    'existencia': '0',
                    'costo': '0.00',
                    'precio_uno': '0.00',
                    'precio_dos': '0.00',
                    'precio_tres': '0.00',
                    'precio_cuatro': '0.00'
                })


"""class KardexIndexView(ListView):
    template_name = 'almacen/kardex.html'

    def get(self, request):

        #index_end_date = datetime.date.today()
        #index_start_date = datetime.date.today() - timedelta(30)
        #queryset_list = InventarioKardex.objects.filter(created_at__date__range=(index_start_date, index_end_date)).order_by('-created_at', 'nombre', )
        #queryset_list = Kardex.objects.filter(created_at__date__range=(index_start_date, index_end_date)).order_by('-created_at', )

        template_name = self.template_name

        #paginate_by = self.request.GET.get('rpp', 10)
        paginate_by = 10

        query = self.request.GET.get("q", '')
        range = self.request.GET.get("range")
        if range and query:
            from_date = range[0:10]
            to_date = range[13:23]
            format_str = '%d/%m/%Y'
            start_date = datetime.datetime.strptime(from_date, format_str)
            end_date = datetime.datetime.strptime(to_date, format_str)

            queryset_list = Kardex.objects.all()

            queryset_list = queryset_list.filter(
                    Q(created_at__date__range=(start_date, end_date)) &
                    (Q(producto__nombre__exact=query))
                    ).order_by('-created_at')
        else:
            # not query and not range
            queryset_list = Kardex.objects.filter(kardex_id=0)

        try:
            page = int(request.GET.get('page', 1))
            paginate_by = int(paginate_by)
            paginator = Paginator(queryset_list, paginate_by, request=request)
            queryset_list = paginator.page(page)
        #except ValueError:
        #    raise Http404
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            page = 1
            paginator = Paginator(queryset_list, paginate_by, request=request)
            queryset_list = paginator.page(page)

        return render(request, template_name, {
            'page': queryset_list,
        })"""

"""class KardexIndexView(DinamicPaginationMixin, SearchMixin, ListView):
    template_name = 'almacen/kardex.html'

    def get_queryset(self):
        queryset_list = Kardex.objects.all()
        query = self.request.GET.get("q")
        if query:
            queryset_list = queryset_list.filter(
                    Q(nombre__icontains=query) |
                    Q(descripcion__icontains=query)
                    ).distinct().order_by('nombre')
        paginator = Paginator(queryset_list, 10)  # Show 10 contacts per page
        page = int(self.request.GET.get('page', 1))
        try:
            queryset_list = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            queryset_list = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 999), deliver last page of results.
            queryset_list = paginator.page(paginator.num_pages)

        return render(self.request, self.template_name, {
            'page': queryset_list,
        })
"""


def stock_is_exist(request):
    if request.method == "GET":
        if request.is_ajax():
            productoId = request.GET.get('productoId', None)
            # referenciaId = request.GET.get('referenciaId', None)
            almacenId = request.GET.get('almacenId', None)
            # producto_obj = Kardex.objects.filter(producto__producto_id=productoId, movimiento=1, referencia_id=referenciaId)
            producto_obj = Kardex.objects.filter(
                producto__producto_id=productoId, almacen_id=almacenId)

            # referencia = 1 (INVENTARIO INICIAL, UNICAMENTE UNA SOLA VEZ)
            if producto_obj.exists():
                return JsonResponse({
                    'success': True,
                    'isExist': True,
                })
            else:
                return JsonResponse({
                    'success': True,
                    'isExist': False,
                })


def cartfit_save(request):
    if request.is_ajax():
        now = datetime.datetime.now()
        ahora_obj = now.strftime('%Y-%m-%d')

        empresa_id = request.session['company_id']
        user_basket = Cesta.objects.filter(
            usuario=request.user, clave_apli='CART-INV_AJUSTE', empresa_id=empresa_id)[0]
        items = user_basket.obtener_items()

        #print("LISTA DE ITEMS...")
        # print(items)

        for item in items:
            # date_str = item.trans_date  # The date - 2018-11-24 16:51:02
            # format_str = '%Y-%m-%d %H:%M:%S'  # The format
            # fecha_operacion_obj = datetime.datetime.strptime(date_str, format_str)

            # print(fecha_operacion_obj)

            # codigo_tipo_movimiento = key['TransType']
            #opciones = item.opciones.values('nombre', 'valor')
            #opciones = item.opciones.all()

            # Direct access (ok)
            #opcion_set = ItemOpcion.objects.filter(item=item)

            # Reverse access through instance (ok)
            opcion_set = item.opciones.all()

            for opcion in opcion_set:
                #print("NOMBRE=%s | VALOR=%s" % (opcion.nombre, opcion.valor))
                if opcion.nombre == 'MOTIVO':
                    cod_movimiento = opcion.valor
                elif opcion.nombre == 'ALMACEN':
                    almacen_id = opcion.valor

            #cod_movimiento = opciones[0]['valor']
            #almacen_id = opciones[1]['valor']

            # <QuerySet [{'id': 1, 'nombre': 'MOTIVO', 'valor': 'INV_INI'}, {'id': 2, 'nombre': 'ALMACEN', 'valor': '1'}]>

            tipo_movimiento_obj = TipoMovimiento.objects.filter(
                codigo=cod_movimiento)[0]

            # productoId = key['Code']
            # unidad_abreviatura = key['Unit']
            producto_id = item.producto.pk

            producto_obj = Producto.objects.get(pk=producto_id)

            # qty = float(key['Qty'])
            # cost = float(key['Price'])
            ctrlprod = ControlProducto.objects.filter(
                almacen_id=almacen_id, producto_id=producto_id)

            cantidad_original = ctrlprod[0].stock if ctrlprod else 0

            qty = item.cantidad
            cost = item.precio
            valor_total = qty * cost

            almacen_obj = Almacen.objects.get(pk=almacen_id)

            kardex = Kardex()
            kardex.movimiento = tipo_movimiento_obj

            kardex.orden_id = 0
            kardex.numero_comprobante = 0
            kardex.producto = producto_obj
            kardex.unidad = item.unidad_medida

            metodo_costo = item.producto.metodo_costo
            if tipo_movimiento_obj.es_existencia:  # Inventario Inicial
                # kardex.referencia = motivo
                kardex.referencia = "Inventario Inicial"

                if item.unidad_medida == item.producto.unidad_secundaria:
                    # TRANFORMAR SUBMULTIPLO Y PRECIO A UNIDAD PRINCIPAL
                    #kardex.unidad = item.producto.unidad

                    equivalencia_unidad = item.producto.unidad_equivalencia
                    fraccion = item.cantidad
                    precio_fraccion = item.precio

                    qty = (fraccion * 1) / equivalencia_unidad
                    cost = precio_fraccion * equivalencia_unidad
                    valor_total = qty * cost

                kardex.cantidad = qty
                kardex.costo = cost
                kardex.total = valor_total

                kardex.cantidad_total = qty
                kardex.precio_total = cost
                kardex.valor_total = valor_total

            elif (tipo_movimiento_obj.es_entrada):
                kardex.referencia = "%s / ORIGINAL => %s" % (
                    'Ajuste', cantidad_original)

                kardex.cantidad = qty
                kardex.costo = cost
                kardex.total = valor_total

                if (metodo_costo == 'PROM'):
                    try:
                        kardex_ant = Kardex.objects.filter(producto=producto_obj,
                                                           almacen=almacen_obj,
                                                           created_at__date__lte=ahora_obj).latest('created_at')
                        stock_cantidad = qty + kardex_ant.cantidad_total
                        stock_total = valor_total + kardex_ant.valor_total
                        if stock_cantidad != 0:
                            stock_costo = stock_total / stock_cantidad
                        else:
                            stock_costo = 0

                        kardex.cantidad_total = stock_cantidad
                        kardex.valor_total = stock_total
                        kardex.precio_total = stock_costo
                    except Kardex.DoesNotExist:
                        kardex.cantidad_total = qty
                        kardex.precio_total = cost
                        kardex.valor_total = valor_total
            else:
                # SALIDAS
                # kardex.referencia = motivo
                kardex.referencia = "%s / ORIGINAL => %s" % (
                    'Ajuste', cantidad_original)

                kardex.cantidad = qty
                kardex.costo = cost
                kardex.total = valor_total

                if (metodo_costo == 'PROM'):
                    # PROM (PROMEDIO PONDERADO)
                    try:
                        kardex_ant = Kardex.objects.filter(producto=producto_obj,
                                                           almacen=almacen_obj,
                                                           created_at__date__lte=ahora_obj).latest('created_at')
                        stock_cantidad = kardex_ant.cantidad_total - qty
                        stock_total = kardex_ant.valor_total - valor_total
                        if stock_cantidad != 0:
                            stock_costo = stock_total / stock_cantidad
                        else:
                            stock_costo = 0

                        kardex.cantidad_total = stock_cantidad
                        kardex.valor_total = stock_total
                        kardex.precio_total = stock_costo
                    except Kardex.DoesNotExist:
                        kardex.cantidad_total = qty
                        kardex.precio_total = cost
                        kardex.valor_total = valor_total

            # kardex.empresa = request.user.perfil.empresa
            kardex.empresa_id = empresa_id
            kardex.almacen = almacen_obj
            kardex.usuario_creador = request.user

            kardex.save()

            if (kardex.cantidad_total == 0):
                precio_control = 0
            else:
                precio_control = kardex.valor_total / kardex.cantidad_total

            control_producto = ControlProducto.objects.update_or_create(
                almacen=kardex.almacen,
                producto=kardex.producto,
                defaults={'stock': kardex.cantidad_total,
                          'precio': precio_control}
            )

        # vaciar cesta de ajuste
        user_basket.vaciar_cesta()

        return JsonResponse({
            'success': True,
        })


"""
FUNCIONES ENTRADA INVENTARIO
"""


class ListadoEntradas(ListView):
    template_name = 'almacen/listado_entradas.html'

    def get_queryset(self):
        return Kardex.objects.none()


def ajax_listado_entradas(request):
    from_date = request.GET.get("startDate")
    to_date = request.GET.get("endDate")
    format_str = '%Y-%m-%d'
    start_date = datetime.datetime.strptime(from_date, format_str).date()
    end_date = datetime.datetime.strptime(to_date, format_str).date() + timedelta(days=1)

    # raw_data = Kardex.objects.filter(movimiento__es_entrada=True, created_at__date__range=(start_date, end_date)).order_by('-created_at')
    raw_data = Kardex.objects.filter(
        Q(movimiento__es_entrada=True) &
        Q(created_at__date__range=(start_date, end_date))
    ).order_by('-created_at')

    dictionary = {}
    if (len(raw_data) > 0):
        result = []
        for value in raw_data:
            if int(value.cantidad) > 0:
                desglose = "{} {}".format(int(value.cantidad), value.unidad.abreviatura)
            else:
                fraccion = value.cantidad - int(value.cantidad)
                piezas = int(fraccion * value.producto.unidad_equivalencia)
                desglose = "{} {}".format(piezas, ' PZ')
            result.append({
                'id': value.pk,
                # 'fecha_operacion': format(value.created_at, '%d-%b-%Y %H:%M:%S'),
                'producto': value.producto.nombre,
                'almacen': value.almacen.codigo,
                'cantidad': str(value.cantidad),
                'desglose': desglose,
                'unidad': value.unidad.abreviatura,
                'costo': str(value.costo)
            })

        # users = User.objects.all().values('first_name', 'last_name')  # or simply .values() to get all fields
        # users_list = list(users_obj)  # important: convert the QuerySet to a list object

        # data = json.dumps(result) # json
        dictionary = list(result)  # diccionario

    return JsonResponse(dictionary, safe=False)


class EntradaInventario(ListView):
    template_name = 'almacen/entrada.html'

    def get_queryset(self):
        # return TipoMovimiento.objects.filter(Q(es_entrada=True) | Q(es_existencia=True), es_ajuste=False)
        return TipoMovimiento.objects.filter(es_entrada=True, es_ajuste=False)

    def get_context_data(self, **kwargs):
        context = super(EntradaInventario, self).get_context_data(**kwargs)
        #context['unidades'] = UnidadMedida.objects.all()
        context['almacenes'] = Almacen.objects.all()

        return context


def cartin_add(request, product_id):
    if request.is_ajax():
        unit = request.POST.get('unit', None)
        cantidad = float(request.POST.get('quantity', 1))
        precio = float(request.POST.get('cost', 0))

        empresa_id = request.session['company_id']
        user_basket, status = Cesta.objects.get_or_create(
            usuario=request.user, clave_apli='CART-INV_ENTRADA', empresa_id=empresa_id)

        producto_obj = Producto.objects.get(pk=product_id)
        unidad_obj = UnidadMedida.objects.filter(abreviatura=unit)[0]
        # calculos
        subtotal_linea = cantidad * precio
        if producto_obj.iva.codigo == '2':
            subtotal_12 = subtotal_linea
            subtotal_0 = 0
            porcentaje_iva = float(producto_obj.iva.porcentaje)
            valor_iva = round((subtotal_12 * porcentaje_iva) / 100, 5)
            valor_total = subtotal_12 + valor_iva
        else:
            subtotal_12 = 0
            subtotal_0 = subtotal_linea
            valor_iva = 0
            valor_total = subtotal_0

        cesta_item = CestaItem()
        cesta_item.tipo = 'PROD'
        cesta_item.producto = producto_obj
        cesta_item.cantidad = cantidad
        cesta_item.unidad_medida = unidad_obj
        cesta_item.precio = precio
        cesta_item.valor_subtotal_sin_impuesto = precio
        cesta_item.valor_subtotal_12 = subtotal_12
        cesta_item.valor_subtotal_0 = subtotal_0
        cesta_item.valor_iva = valor_iva
        cesta_item.valor_total = valor_total
        # item.cesta = cesta
        cesta_item.save()
        user_basket.items.add(cesta_item)

        return JsonResponse({
            'success': True,
        })


def cartin_show(request):
    if request.is_ajax():
        empresa_id = request.session['company_id']
        user_basket, status = Cesta.objects.get_or_create(
            usuario=request.user, clave_apli='CART-INV_ENTRADA', empresa_id=empresa_id)
        items = user_basket.obtener_items()

        result = []
        for item in items:
            result.append({
                'cesta_pk': item.pk,
                'product_id': item.producto.pk,
                'name': item.producto.nombre,
                'unit': item.unidad_medida.abreviatura,
                'quantity': str(item.cantidad),
                'price': str(item.precio),
                'subtotal': str(item.valor_subtotal_sin_impuesto)
            })
        data = json.dumps(result)

        return JsonResponse({
            'success': True,
            'cart': data
        })


def cartin_update(request):
    if request.method == 'GET':
        cesta_pk = request.GET.get('id', None)
        if cesta_pk is not None:
            # buscar registro en CestaItem
            cesta_item = CestaItem.objects.get(pk=cesta_pk)
            return JsonResponse({
                'success': True,
                'id': cesta_pk,
                'product': cesta_item.producto.nombre,
                'qty': round(cesta_item.cantidad, 3),
                'unit': cesta_item.unidad_medida.abreviatura,
                'unit_primary': cesta_item.producto.unidad_principal.abreviatura,
                'unit_secondary': cesta_item.producto.unidad_secundaria.abreviatura if cesta_item.producto.unidad_secundaria else None,
                'unit_equivalence': cesta_item.producto.unidad_equivalencia,
                'cost': round(cesta_item.precio, 3),
            })

    else:  # request.method == 'POST'
        data = request.POST.copy()
        itemID = data.get('id')
        cantidad = locale.atof(data.get('qty', 1))
        unidad = data.get('unit')
        precio = locale.atof(data.get('cost', 0))

        unit_obj = UnidadMedida.objects.filter(abreviatura=unidad)[0]
        cesta_item = CestaItem.objects.get(pk=itemID)

        # calculos
        subtotal_linea = cantidad * precio

        if cesta_item.producto.iva.codigo == '2':
            subtotal_12 = subtotal_linea
            subtotal_0 = 0
            porcentaje_iva = float(cesta_item.producto.iva.porcentaje)
            valor_iva = round((subtotal_12 * porcentaje_iva) / 100, 5)
            valor_total = subtotal_12 + valor_iva
        else:
            subtotal_12 = 0
            subtotal_0 = subtotal_linea
            valor_iva = 0
            valor_total = subtotal_0

        # actualizar item
        cesta_item.cantidad = cantidad
        cesta_item.unidad_medida = unit_obj
        cesta_item.precio = precio
        cesta_item.valor_subtotal_sin_impuesto = subtotal_linea
        cesta_item.valor_subtotal_12 = subtotal_12
        cesta_item.valor_subtotal_0 = subtotal_0
        cesta_item.valor_iva = valor_iva
        cesta_item.valor_total = valor_total
        cesta_item.save()

        return JsonResponse({
            'success': True,
        })


def cartin_remove(request):
    if request.method == 'POST':
        if request.is_ajax():
            itemID = request.POST.get('cesta_id', None)
            item = CestaItem.objects.get(pk=itemID)
            item.delete()

            return JsonResponse({
                'success': True,
            })


def cartin_save(request):
    if request.is_ajax():
        referencia_id = request.GET.get('referencia_id', None)
        almacen_id = request.GET.get('almacen_id', None)
        nroComprobante = request.GET.get('nro_comp', None)

        tipo_movimiento_obj = TipoMovimiento.objects.get(pk=referencia_id)
        empresa_id = request.session['company_id']
        # metodo_costo = request.user.perfil.empresa.metodo_costo

        almacen_obj = Almacen.objects.get(pk=almacen_id)
        now = datetime.datetime.now()
        ahora_obj = now.strftime('%Y-%m-%d')

        user_basket = Cesta.objects.filter(
            usuario=request.user, clave_apli='CART-INV_ENTRADA', empresa_id=empresa_id)[0]
        items = user_basket.obtener_items()
        for item in items:

            qty = item.cantidad
            cost = item.precio

            kardex = Kardex()
            kardex.movimiento = tipo_movimiento_obj
            kardex.referencia = 'Entrada'

            kardex.orden_id = 0
            kardex.numero_comprobante = nroComprobante
            kardex.producto = item.producto

            if item.unidad_medida == item.producto.unidad_secundaria:
                # TRANFORMAR SUBMULTIPLO Y PRECIO A UNIDAD PRINCIPAL
                kardex.unidad = item.producto.unidad_principal

                equivalencia_unidad = item.producto.unidad_equivalencia
                fraccion = item.cantidad
                precio_fraccion = item.precio

                qty = (fraccion * 1) / equivalencia_unidad
                cost = precio_fraccion * equivalencia_unidad
                valor_total = qty * cost

            else:
                kardex.unidad = item.unidad_medida

                # kardex.created_at =
                # kardex.update_at =

                qty = item.cantidad
                cost = item.precio
                valor_total = qty * cost

            kardex.cantidad = qty
            kardex.costo = cost
            kardex.total = valor_total

            metodo_costo = item.producto.metodo_costo
            if (metodo_costo == 'PROM'):
                try:
                    kardex_ant = Kardex.objects.filter(producto=item.producto,
                                                       almacen=almacen_obj,
                                                       created_at__date__lte=ahora_obj).latest('created_at')
                    stock_cantidad = qty + kardex_ant.cantidad_total
                    stock_total = valor_total + kardex_ant.valor_total
                    if stock_cantidad != 0:
                        stock_costo = stock_total / stock_cantidad
                    else:
                        stock_costo = 0

                    kardex.cantidad_total = stock_cantidad
                    kardex.valor_total = stock_total
                    kardex.precio_total = stock_costo
                except Kardex.DoesNotExist:
                    kardex.cantidad_total = qty
                    kardex.precio_total = cost
                    kardex.valor_total = valor_total

            # kardex.empresa = request.user.perfil.empresa
            kardex.empresa_id = empresa_id
            kardex.almacen = almacen_obj
            kardex.usuario_creador = request.user

            kardex.save()

            if (kardex.cantidad_total == 0):
                precio_control = 0
            else:
                precio_control = kardex.valor_total / kardex.cantidad_total

            control_producto = ControlProducto.objects.update_or_create(
                almacen=kardex.almacen,
                producto=kardex.producto,
                defaults={'stock': kardex.cantidad_total,
                          'precio': precio_control}
            )

        # vaciar cesta de compras
        user_basket.vaciar_cesta()

        return JsonResponse({
            'success': True,
        })


"""
FUNCIONES SALIDA INVENTARIO
"""


class ListadoSalidas(ListView):
    template_name = 'almacen/listado_salidas.html'

    def get_queryset(self):
        return Kardex.objects.none()


def ajax_listado_salidas(request):
    from_date = request.GET.get("startDate")
    to_date = request.GET.get("endDate")
    format_str = '%Y-%m-%d'
    start_date = datetime.datetime.strptime(from_date, format_str)
    end_date = datetime.datetime.strptime(to_date, format_str)

    # raw_data = Kardex.objects.filter(movimiento__es_salida=True, created_at__date__range=(start_date, end_date)).order_by('-created_at')
    raw_data = Kardex.objects.filter(
        Q(movimiento__es_salida=True) &
        Q(created_at__date__range=(start_date, end_date))
    ).order_by('-created_at')

    dictionary = {}
    if (len(raw_data) > 0):
        result = []
        for value in raw_data:
            if int(value.cantidad) > 0:
                desglose = "{} {}".format(int(value.cantidad), value.unidad.abreviatura)
            else:
                fraccion = value.cantidad - int(value.cantidad)
                piezas = int(fraccion * value.producto.unidad_equivalencia)
                desglose = "{} {}".format(piezas, ' PZ')
            result.append({
                'id': value.pk,
                # 'fecha_operacion': format(value.created_at, '%d-%b-%Y %H:%M:%S'),
                'producto': value.producto.nombre,
                'almacen': value.almacen.codigo,
                'cantidad': str(value.cantidad),
                'desglose': desglose,
                'unidad': value.unidad.abreviatura,
                'costo': str(value.costo)
            })

        # users = User.objects.all().values('first_name', 'last_name')  # or simply .values() to get all fields
        # users_list = list(users_obj)  # important: convert the QuerySet to a list object

        # data = json.dumps(result) # json
        dictionary = list(result)  # diccionario

    return JsonResponse(dictionary, safe=False)

    '''try:
        query = """
            select k.kardex_id as id, k.created_at as fecha_operacion, p.nombre as producto, a.descripcion as almacen, k.cantidad,
            case when trunc(k.cantidad) > 0 then
                concat(trunc(k.cantidad), ' ', u.abreviatura)
            else
                concat(round(abs(-k.cantidad - trunc(-k.cantidad)) * p.unidad_equivalencia, 0), ' PZ')
            end as desglose,
            u.abreviatura as unidad, k.costo
            from almacen_kardex k
            inner join producto_producto p on p.producto_id = k.producto_id
            inner join almacen_almacen a on k.almacen_id = a.almacen_id
            inner join producto_unidad u on u.unidad_id = k.unidad_id
            where k.tipo = 2 and date(k.created_at) >= '%s' and date(k.created_at) <= '%s'
            order by k.created_at desc
        """ % (start_date, end_date)
    except ValueError:
        # ningún almacén seleccionado
        id_aux = 0
        query = """
            select k.kardex_id as id, k.created_at as fecha_operacion, p.nombre as producto, a.descripcion as almacen, 0 as desglose, k.cantidad, u.abreviatura as unidad, k.costo
            from almacen_kardex k
            inner join producto_producto p on p.producto_id = k.producto_id
            inner join almacen_almacen a on k.almacen_id = a.almacen_id
            inner join producto_unidad u on u.unidad_id = k.unidad_id
            where k.kardex_id = %s
        """ % (id_aux)

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        results = []
        columns = (
            'id', 'fecha_operacion', 'producto', 'almacen', 'cantidad', 'desglose', 'unidad', 'costo'
        )
        for row in rows:
            results.append(dict(zip(columns, row)))
    return JsonResponse(results, safe=False)'''


class SalidaInventario(ListView):
    template_name = 'almacen/salida.html'

    def get_queryset(self):
        return TipoMovimiento.objects.filter(es_salida=True, es_ajuste=False)

    def get_context_data(self, **kwargs):
        context = super(SalidaInventario, self).get_context_data(**kwargs)
        context['unidades'] = UnidadMedida.objects.all()
        context['almacenes'] = Almacen.objects.filter(activo=True)

        return context


def cartout_add(request, product_id):
    if request.is_ajax():
        unit = request.POST.get('unit', None)
        cantidad = float(request.POST.get('quantity', 1))
        precio = float(request.POST.get('cost', 0))

        empresa_id = request.session['company_id']
        user_basket, status = Cesta.objects.get_or_create(
            usuario=request.user, clave_apli='CART-INV_SALIDA', empresa_id=empresa_id)

        producto_obj = Producto.objects.get(pk=product_id)
        unidad_obj = UnidadMedida.objects.filter(abreviatura=unit)[0]
        # calculos
        subtotal_linea = cantidad * precio
        if producto_obj.iva.codigo == '2':
            subtotal_12 = subtotal_linea
            subtotal_0 = 0
            porcentaje_iva = float(producto_obj.iva.porcentaje)
            valor_iva = round((subtotal_12 * porcentaje_iva) / 100, 5)
            valor_total = subtotal_12 + valor_iva
        else:
            subtotal_12 = 0
            subtotal_0 = subtotal_linea
            valor_iva = 0
            valor_total = subtotal_0

        cesta_item = CestaItem()
        cesta_item.tipo = 'PROD'
        cesta_item.producto = producto_obj
        cesta_item.cantidad = cantidad
        cesta_item.unidad_medida = unidad_obj
        cesta_item.precio = precio
        cesta_item.valor_subtotal_sin_impuesto = precio
        cesta_item.valor_subtotal_12 = subtotal_12
        cesta_item.valor_subtotal_0 = subtotal_0
        cesta_item.valor_iva = valor_iva
        cesta_item.valor_total = valor_total
        # item.cesta = cesta
        cesta_item.save()
        user_basket.items.add(cesta_item)

        return JsonResponse({
            'success': True,
        })


def cartout_show(request):
    if request.is_ajax():
        empresa_id = request.session['company_id']
        user_basket, status = Cesta.objects.get_or_create(
            usuario=request.user, clave_apli='CART-INV_SALIDA', empresa_id=empresa_id)
        items = user_basket.obtener_items()

        result = []
        for item in items:
            result.append({
                'cesta_pk': item.pk,
                'product_id': item.producto.pk,
                'name': item.producto.nombre,
                'unit': item.unidad_medida.abreviatura,
                'quantity': str(item.cantidad),
                'price': str(item.precio),
                'subtotal': str(item.valor_subtotal_sin_impuesto)
            })
        data = json.dumps(result)

        return JsonResponse({
            'success': True,
            'cart': data
        })


def cartout_update(request):
    if request.method == 'GET':
        cesta_pk = request.GET.get('id', None)
        if cesta_pk is not None:
            # buscar registro en CestaItem
            cesta_item = CestaItem.objects.get(pk=cesta_pk)
            return JsonResponse({
                'success': True,
                'id': cesta_pk,
                'product': cesta_item.producto.nombre,
                'qty': round(cesta_item.cantidad, 3),
                'unit': cesta_item.unidad_medida.abreviatura,
                'unit_primary': cesta_item.producto.unidad_principal.abreviatura,
                'unit_secondary': cesta_item.producto.unidad_secundaria.abreviatura if cesta_item.producto.unidad_secundaria else None,
                'unit_equivalence': cesta_item.producto.unidad_equivalencia,
                'cost': round(cesta_item.precio, 3),
            })

    else:  # request.method == 'POST'
        data = request.POST.copy()
        itemID = data.get('id')
        cantidad = float(data.get('qty', 1))
        unidad = data.get('unit')
        precio = float(data.get('cost', 0))

        unit_obj = UnidadMedida.objects.filter(abreviatura=unidad)[0]
        cesta_item = CestaItem.objects.get(pk=itemID)

        # calculos
        subtotal_linea = cantidad * precio

        if cesta_item.producto.iva.codigo == '2':
            subtotal_12 = subtotal_linea
            subtotal_0 = 0
            porcentaje_iva = float(cesta_item.producto.iva.porcentaje)
            valor_iva = round((subtotal_12 * porcentaje_iva) / 100, 5)
            valor_total = subtotal_12 + valor_iva
        else:
            subtotal_12 = 0
            subtotal_0 = subtotal_linea
            valor_iva = 0
            valor_total = subtotal_0

        # actualizar item
        cesta_item.cantidad = cantidad
        cesta_item.unidad_medida = unit_obj
        cesta_item.precio = precio
        cesta_item.valor_subtotal_sin_impuesto = subtotal_linea
        cesta_item.valor_subtotal_12 = subtotal_12
        cesta_item.valor_subtotal_0 = subtotal_0
        cesta_item.valor_iva = valor_iva
        cesta_item.valor_total = valor_total
        cesta_item.save()

        return JsonResponse({
            'success': True,
        })


def cartout_remove(request):
    if request.method == 'POST':
        if request.is_ajax():
            itemID = request.POST.get('cesta_id', None)
            item = CestaItem.objects.get(pk=itemID)
            item.delete()

            return JsonResponse({
                'success': True,
            })


def cartout_save(request):
    if request.is_ajax():
        referencia_id = request.GET.get('referencia_id', None)
        almacen_id = request.GET.get('almacen_id', None)
        nroComprobante = request.GET.get('nro_comp', None)

        tipo_movimiento_obj = TipoMovimiento.objects.get(pk=referencia_id)
        empresa_id = request.session['company_id']
        # metodo_costo = request.user.perfil.empresa.metodo_costo

        almacen_obj = Almacen.objects.get(pk=almacen_id)
        now = datetime.datetime.now()
        ahora_obj = now.strftime('%Y-%m-%d')

        user_basket = Cesta.objects.filter(
            usuario=request.user, clave_apli='CART-INV_SALIDA', empresa_id=empresa_id)[0]
        items = user_basket.obtener_items()
        for item in items:

            qty = item.cantidad
            cost = item.precio

            kardex = Kardex()
            kardex.movimiento = tipo_movimiento_obj
            kardex.referencia = 'Salida'

            kardex.orden_id = 0
            kardex.numero_comprobante = nroComprobante
            kardex.producto = item.producto

            if item.unidad_medida == item.producto.unidad_secundaria:
                # TRANFORMAR SUBMULTIPLO Y PRECIO A UNIDAD PRINCIPAL
                kardex.unidad = item.producto.unidad_principal

                equivalencia_unidad = item.producto.unidad_equivalencia
                fraccion = item.cantidad
                precio_fraccion = item.precio

                qty = (fraccion * 1) / equivalencia_unidad
                cost = precio_fraccion * equivalencia_unidad
                valor_total = qty * cost

            else:
                kardex.unidad = item.unidad_medida

                # kardex.created_at =
                # kardex.update_at =

                qty = item.cantidad
                cost = item.precio
                valor_total = qty * cost

            kardex.cantidad = qty
            kardex.costo = cost
            kardex.total = valor_total

            metodo_costo = item.producto.metodo_costo
            if (metodo_costo == 'PROM'):
                try:
                    kardex_ant = Kardex.objects.filter(producto=item.producto,
                                                       almacen=almacen_obj,
                                                       created_at__date__lte=ahora_obj).latest('created_at')
                    stock_cantidad = kardex_ant.cantidad_total - qty
                    stock_total = kardex_ant.valor_total - valor_total
                    if stock_cantidad != 0:
                        stock_costo = stock_total / stock_cantidad
                    else:
                        stock_costo = 0

                    kardex.cantidad_total = stock_cantidad
                    kardex.valor_total = stock_total
                    kardex.precio_total = stock_costo
                except Kardex.DoesNotExist:
                    kardex.cantidad_total = qty
                    kardex.precio_total = cost
                    kardex.valor_total = valor_total

            # kardex.empresa = request.user.perfil.empresa
            kardex.empresa_id = empresa_id
            kardex.almacen = almacen_obj
            kardex.usuario_creador = request.user

            kardex.save()

            if (kardex.cantidad_total == 0):
                precio_control = 0
            else:
                precio_control = kardex.valor_total / kardex.cantidad_total

            control_producto = ControlProducto.objects.update_or_create(
                almacen=kardex.almacen,
                producto=kardex.producto,
                defaults={'stock': kardex.cantidad_total,
                          'precio': precio_control}
            )

        # vaciar cesta de salida
        user_basket.vaciar_cesta()

        return JsonResponse({
            'success': True,
        })


"""
FUNCIONES AJUSTE DE INVENTARIO
"""


def cartfit_add(request, product_id):
    if request.is_ajax():
        unit = request.POST.get('unit', None)
        cantidad = float(request.POST.get('quantity', 1))
        precio = float(request.POST.get('cost', 0))
        current_qty = request.POST.get('current_qty', 0)

        reason = request.POST.get('reason', None)
        warehouse = request.POST.get('warehouse', None)
        trans_date = request.POST.get('trans_date', None)

        empresa_id = request.session['company_id']
        user_basket, status = Cesta.objects.get_or_create(
            usuario=request.user, clave_apli='CART-INV_AJUSTE', empresa_id=empresa_id)

        producto_obj = Producto.objects.get(pk=product_id)
        unidad_obj = UnidadMedida.objects.filter(abreviatura=unit)[0]
        # calculos
        subtotal_linea = cantidad * precio
        if producto_obj.iva.codigo == '2':
            subtotal_12 = subtotal_linea
            subtotal_0 = 0
            porcentaje_iva = float(producto_obj.iva.porcentaje)
            valor_iva = round((subtotal_12 * porcentaje_iva) / 100, 5)
            valor_total = subtotal_12 + valor_iva
        else:
            subtotal_12 = 0
            subtotal_0 = subtotal_linea
            valor_iva = 0
            valor_total = subtotal_0

        cesta_item = CestaItem()
        cesta_item.tipo = 'PROD'
        cesta_item.producto = producto_obj
        cesta_item.cantidad = cantidad
        cesta_item.cantidad_aux = current_qty
        cesta_item.unidad_medida = unidad_obj
        cesta_item.precio = precio
        cesta_item.valor_subtotal_sin_impuesto = precio
        cesta_item.valor_subtotal_12 = subtotal_12
        cesta_item.valor_subtotal_0 = subtotal_0
        cesta_item.valor_iva = valor_iva
        cesta_item.valor_total = valor_total
        # item.cesta = cesta
        cesta_item.save()
        user_basket.items.add(cesta_item)

        motivo = ItemOpcion.objects.create(nombre="MOTIVO", valor=reason, item=cesta_item)
        almacen = ItemOpcion.objects.create(nombre="ALMACEN", valor=warehouse, item=cesta_item)

        items = user_basket.obtener_items()

        result = []
        for item in items:
            result.append({
                'cesta_pk': item.pk,
                'name': item.producto.nombre,
                'unit': item.unidad_medida.abreviatura,
                'quantity': str(item.cantidad),
                'price': str(item.precio),
                'subtotal': str(item.valor_subtotal_sin_impuesto),
            })
        data = json.dumps(result)

        return JsonResponse({
            'success': True,
            'cart': data
        })


def ajuste_agregar_lote(request):
    if request.method == "GET":
        itemID = request.GET.get('id', None)

        cesta_lote = CestaLote.objects.filter(item__pk=itemID)

        result = []
        if cesta_lote:
            for item in cesta_lote:
                result.append({
                    'lote_pk': item.id,
                    'lote_numero': item.lote_numero,
                    'fecha_caducidad': item.fecha_caducidad.strftime('%Y-%m-%d'),
                    'cantidad': str(item.cantidad),
                })
        data = json.dumps(result)

        return JsonResponse({
            'success': True,
            'cesta_item_pk': itemID,
            'lotejson': data
        })
    else:  # request.method == 'POST'
        cesta_item_pk = request.POST.get("id")
        # arrayPk = request.POST.getlist('pkArray[]')
        arrayLote = request.POST.getlist('loteArray[]')
        arrayExpira = request.POST.getlist('expiraArray[]')
        arrayQty = request.POST.getlist('qtyArray[]')

        # eliminar lotes existentes
        CestaLote.objects.filter(item_id=cesta_item_pk).delete()

        i = 0
        while i < len(arrayLote):
            # nuevo lote
            cesta_lote = CestaLote()
            cesta_lote.lote_numero = arrayLote[i]
            cesta_lote.fecha_caducidad = arrayExpira[i]
            cesta_lote.cantidad = arrayQty[i]
            cesta_lote.item_id = cesta_item_pk
            cesta_lote.save()

            i += 1

        return JsonResponse({
            'success': True,
        })


def cart_show(request):
    if request.is_ajax():
        empresa_id = request.session['company_id']
        user_basket, status = Cesta.objects.get_or_create(
            usuario=request.user, clave_apli='CART-INV_AJUSTE', empresa_id=empresa_id)
        items = user_basket.obtener_items()

        result = []
        for item in items:
            result.append({
                'cesta_pk': item.pk,
                'product_id': item.producto.pk,
                'name': item.producto.nombre,
                'unit': item.unidad_medida.abreviatura,
                'quantity': str(item.cantidad),
                'price': str(item.precio),
                'cost': str(item.valor_subtotal_sin_impuesto),
                'subtotal': str(item.valor_subtotal_sin_impuesto)
            })
        data = json.dumps(result)

        return JsonResponse({
            'success': True,
            'cart': data
        })


def cartfit_remove_single(request):
    if request.is_ajax():
        cart = CartFit(request.session)
        product = Producto.objects.get(pk=request.POST.get('product_id'))
        cart.remove_single(product)

        result = []
        for item in cart.items:
            result.append({
                'product_id': item.product.pk,
                'name': item.product.nombre,
                'unit': item.unit,
                'quantity': str(item.quantity),
                'price': str(item.price),
                'current_qty': str(item.current_qty),
                'new_qty': str(item.new_qty),
                'cost': str(item.subtotal),
            })
        data = json.dumps(result)

        return JsonResponse({
            'success': True,
            'cart': data
        })


def cartfit_remove(request):
    if request.is_ajax():
        itemID = request.POST.get('cesta_id', None)

        item = CestaItem.objects.get(pk=itemID)
        item.delete()

        empresa_id = request.session['company_id']
        user_basket, status = Cesta.objects.get_or_create(
            usuario=request.user, clave_apli='CART-INV_AJUSTE', empresa_id=empresa_id)
        items = user_basket.obtener_items()

        result = []
        for item in items:
            result.append({
                'cesta_pk': item.pk,
                'name': item.producto.nombre,
                'unit': item.unidad_medida.abreviatura,
                'quantity': str(item.cantidad),
                'price': str(item.precio),
                'subtotal': str(item.valor_subtotal_sin_impuesto),
            })
        data = json.dumps(result)

        return JsonResponse({
            'success': True,
            'cart': data
        })


def cartfit_update(request):
    if request.method == 'GET':
        cesta_pk = request.GET.get('id', None)
        if cesta_pk is not None:
            # buscar registro en CestaItem
            cesta_item = CestaItem.objects.get(pk=cesta_pk)
            return JsonResponse({
                'success': True,
                'id': cesta_pk,
                'product': cesta_item.producto.nombre,
                'qty': round(cesta_item.cantidad, 3),
                'unit': cesta_item.unidad_medida.abreviatura,
                'unit_primary': cesta_item.producto.unidad_principal.abreviatura,
                'unit_secondary': cesta_item.producto.unidad_secundaria.abreviatura if cesta_item.producto.unidad_secundaria else None,
                'unit_equivalence': cesta_item.producto.unidad_equivalencia,
                'cost': round(cesta_item.precio, 3),
            })

    else:  # request.method == 'POST'
        data = request.POST.copy()
        itemID = data.get('id')
        cantidad = locale.atof(data.get('qty', 1))
        unidad = data.get('unit')
        precio = locale.atof(data.get('cost', 0))

        unit_obj = UnidadMedida.objects.filter(abreviatura=unidad)[0]
        cesta_item = CestaItem.objects.get(pk=itemID)

        # calculos
        subtotal_linea = cantidad * precio

        if cesta_item.producto.iva.codigo == '2':
            subtotal_12 = subtotal_linea
            subtotal_0 = 0
            porcentaje_iva = float(cesta_item.producto.iva.porcentaje)
            valor_iva = round((subtotal_12 * porcentaje_iva) / 100, 5)
            valor_total = subtotal_12 + valor_iva
        else:
            subtotal_12 = 0
            subtotal_0 = subtotal_linea
            valor_iva = 0
            valor_total = subtotal_0

        # actualizar item
        cesta_item.cantidad = cantidad
        cesta_item.unidad_medida = unit_obj
        cesta_item.precio = precio
        cesta_item.valor_subtotal_sin_impuesto = subtotal_linea
        cesta_item.valor_subtotal_12 = subtotal_12
        cesta_item.valor_subtotal_0 = subtotal_0
        cesta_item.valor_iva = valor_iva
        cesta_item.valor_total = valor_total
        cesta_item.save()

        empresa_id = request.session['company_id']
        user_basket, status = Cesta.objects.get_or_create(
            usuario=request.user, clave_apli='CART-INV_AJUSTE', empresa_id=empresa_id)
        items = user_basket.obtener_items()

        result = []
        for item in items:
            result.append({
                'cesta_pk': item.pk,
                'name': item.producto.nombre,
                'unit': item.unidad_medida.abreviatura,
                'quantity': str(item.cantidad),
                'price': str(item.precio),
                'subtotal': str(item.valor_subtotal_sin_impuesto),
            })
        data = json.dumps(result)

        return JsonResponse({
            'success': True,
            'cart': data
        })


def ajaxBuscarProductoDB(request):
    if request.method == "GET":
        if request.is_ajax():
            producto_id = request.GET.get('producto_id', None)

            # item.creator = owner or item.moderated = False
            producto_obj = Producto.objects.get(pk=producto_id)
            if producto_obj:
                existencia = getExistencia(producto_obj)

                return JsonResponse({
                    'success': True,
                    # 'product': 'SAMSUNG PRINTER XPRESS ML-2165W',
                    # 'productId': '1',
                    # 'cost': '65.00',
                    'product': producto_obj.nombre,
                    'productId': producto_obj.producto_id,
                    'cost': producto_obj.precio_costo,
                    # 'unitId': producto_obj.unidad.unidad_id,
                    'unit_primary': producto_obj.unidad_principal.abreviatura,
                    'unit_secondary': producto_obj.unidad_secundaria.abreviatura if producto_obj.unidad_secundaria else None,
                    'unit_equivalence': producto_obj.unidad_equivalencia,
                    'stock': existencia
                })
            else:
                return JsonResponse({
                    'success': False,
                })


"""
def get_embalaje_principal(request):
    if request.method == "GET":
        if request.is_ajax():
            producto_id = request.GET.get('producto_id', None)

            # item.creator = owner or item.moderated = False
            producto_obj = Producto.objects.get(pk=producto_id)
            if producto_obj:
                return JsonResponse({
                    'success': True,
                    'cost': producto_obj.precio_costo,
                    'unitPrimaryId': producto_obj.unidad.unidad_id,
                    'unitSecondaryId': producto_obj.unidad_secundaria.unidad_id if producto_obj.unidad_secundaria else None,
                })
            else:
                return JsonResponse({
                    'success': False,
                })"""


def product_lookup(request):
    """lista = serializers.serialize('json', Producto.objects.all(), fields=('producto_id','nombre'))
    return HttpResponse(lista, content_type='application/json')"""

    # productos = Producto.objects.all().values('producto_id', 'nombre', 'codigo_principal').order_by('nombre')
    productos = ProductoResumen.objects.all().values(
        'producto_id', 'nombre', 'codigo_principal', 'existencia').order_by('nombre')
    lista_productos = list(productos)  # important: convert the QuerySet to a list object
    return JsonResponse(lista_productos, safe=False)


"""
Reportes
"""

"""class ConsolidadoProductosIndexView(View):
    template_name = 'almacen/consolidado_productos.html'

    def get(self, request):
        queryset_list = ProductoConsolidado.objects.all().order_by('producto__nombre')
        template_name = self.template_name
        query = self.request.GET.get("q", '')
        paginate_by = self.request.GET.get('rpp', 10)

        if query:
            queryset_list = queryset_list.filter(
                    Q(producto__nombre__icontains=query) |
                    Q(producto__codigo_principal__icontains=query)
                    ).distinct().order_by('producto__nombre')
        try:
            page = int(request.GET.get('page', 1))
            paginate_by = int(paginate_by)
            paginator = Paginator(queryset_list, paginate_by, request=request)
            queryset_list = paginator.page(page)
        except ValueError:
            raise Http404

        return render(request, template_name, {
            'page': queryset_list,
        })"""

"""class ConsolidadoProductosIndexView(DinamicPaginationMixin, SearchMixin, ListView):
    template_name = 'almacen/consolidado_productos_new.html'

    def get_queryset(self):
        return ProductoResumen.objects.none()

    def get_context_data(self, **kwargs):
        context = super(ConsolidadoProductosIndexView, self).get_context_data(**kwargs)

        context['almacenes'] = Almacen.objects.filter(activo=True)

        return context"""


class ConsolidadoProductosIndexView(ListView):
    template_name = 'almacen/consolidado_productos.html'

    def get_queryset(self):
        return ProductoResumen.objects.none()

    def get_context_data(self, **kwargs):
        context = super(ConsolidadoProductosIndexView, self).get_context_data(**kwargs)

        context['almacenes'] = Almacen.objects.filter(activo=True)

        return context


def ajax_consolidado_productos(request):
    # lista = serializers.serialize('json', ProductoResumen.objects.all(), fields=('nombre', 'codigo_principal', 'existencia'))
    # return HttpResponse(lista, content_type='application/json')

    # productos = ProductoResumen.objects.values()
    # lista_productos = list(productos)  # important: convert the QuerySet to a list object
    # return JsonResponse(lista_productos, safe=False)
    """productos_obj = ProductoConsolidado.objects.all()
    formatedDate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") #  Time like '23:12:05'
    result = []
    for value in productos_obj:
        result.append({
            'nombre': value.producto.nombre,
            'codigo_principal': value.producto.codigo_principal,
            'fecha': formatedDate,
            'costo': str(value.producto.precio_costo),
            'entradas': str(value.entradas),
            'salidas': str(value.salidas),
            'existencia': str(value.saldo),
        })
    dump = json.dumps(result)
    return HttpResponse(dump, content_type='application/json')"""

    # control_producto = ControlProducto.objects.filter(producto=producto_obj, almacen=almacen_obj)

    if request.method == 'POST':
        if request.is_ajax():
            almacen_id = request.POST.get('almacen_id', None)

            try:
                id = int(almacen_id)
                if id > 0:
                    query = """
                        select prodsumm.id, prodsumm.producto_id, prod.nombre, prod.codigo_principal, coalesce(ctrlprod.precio, 0) as costo, prodsumm.entradas, prodsumm.salidas, prodsumm.saldo, current_timestamp as fecha, alm.descripcion as almacen
                        from almacen_productoconsolidado prodsumm
                        inner join producto_producto prod on prod.producto_id = prodsumm.producto_id
                        left join almacen_controlproducto ctrlprod on ctrlprod.producto_id = prodsumm.producto_id
                        inner join almacen_almacen alm on alm.almacen_id = ctrlprod.almacen_id
                        where ctrlprod.almacen_id = %s
                        order by prod.nombre
                    """ % (id)
                else:
                    # todos los almacenes
                    query = """
                        select prodsumm.id, prodsumm.producto_id, prod.nombre, prod.codigo_principal, coalesce(ctrlprod.precio, 0) as costo, prodsumm.entradas, prodsumm.salidas, prodsumm.saldo, current_timestamp as fecha, alm.descripcion as almacen
                        from almacen_productoconsolidado prodsumm
                        inner join producto_producto prod on prod.producto_id = prodsumm.producto_id
                        left join almacen_controlproducto ctrlprod on ctrlprod.producto_id = prodsumm.producto_id
                        inner join almacen_almacen alm on alm.almacen_id = ctrlprod.almacen_id
                        order by prod.nombre
                    """
            except ValueError:
                # ningún almacén seleccionado
                id_aux = 0
                query = """
                    select prodsumm.id, prodsumm.producto_id, prod.nombre, prod.codigo_principal, coalesce(ctrlprod.precio, 0) as costo, prodsumm.entradas, prodsumm.salidas, prodsumm.saldo, current_timestamp as fecha, alm.descripcion as almacen
                    from almacen_productoconsolidado prodsumm
                    inner join producto_producto prod on prod.producto_id = prodsumm.producto_id
                    left join almacen_controlproducto ctrlprod on ctrlprod.producto_id = prodsumm.producto_id
                    inner join almacen_almacen alm on alm.almacen_id = ctrlprod.almacen_id
                    where ctrlprod.almacen_id = %s
                    order by prod.nombre
                """ % (id_aux)

            with connection.cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
                results = []
                columns = (
                    'id', 'producto_id', 'nombre', 'codigo_principal', 'costo', 'entradas', 'salidas', 'saldo', 'fecha', 'almacen'
                )
                for row in rows:
                    results.append(dict(zip(columns, row)))
            return JsonResponse(results, safe=False)

            # data = serializers.serialize('json', ProductoConsolidado.objects.raw(query), fields=('producto_id', 'nombre', 'entradas', 'salidas', 'saldo'))
            # return HttpResponse(data, content_type='application/json')


class ConsolidadoMovimientosIndexView(ListView):
    template_name = 'almacen/consolidado_movimientos.html'

    def get_queryset(self):
        return Kardex.objects.none()

    def get_context_data(self, **kwargs):
        context = super(ConsolidadoMovimientosIndexView, self).get_context_data(**kwargs)

        context['almacenes'] = Almacen.objects.filter(activo=True)

        return context


def ajax_consolidado_movimientos(request):
    almacen_id = request.POST.get('almacen_id', None)
    from_date = request.POST.get("startDate")
    to_date = request.POST.get("endDate")
    format_str = '%Y-%m-%d'
    start_date = datetime.datetime.strptime(from_date, format_str)
    end_date = datetime.datetime.strptime(to_date, format_str)

    almacen_pk = int(almacen_id)
    if almacen_pk > 0:
        raw_data = Kardex.objects.filter(
            Q(almacen_id=almacen_pk) &
            Q(created_at__date__range=(start_date, end_date))
        ).values('numero_comprobante', 'almacen__descripcion', 'producto__nombre', 'referencia', 'cantidad', 'costo', 'total'
                 ).order_by('-created_at')
    else:
        # todos los almacenes
        raw_data = Kardex.objects.filter(
            created_at__date__range=(start_date, end_date)
        ).values('numero_comprobante', 'almacen__descripcion', 'producto__nombre', 'referencia', 'cantidad', 'costo', 'total'
                 ).order_by('-created_at')

    # users = User.objects.all().values('first_name', 'last_name')  # or simply .values() to get all fields
    # users_list = list(users_obj)  # important: convert the QuerySet to a list object

    kardex_list = list(raw_data)

    return JsonResponse(kardex_list, safe=False)

    # lista = serializers.serialize('json', Kardex.objects.all())
    # return HttpResponse(lista, content_type='application/json')


class KardexAPI(APIView):
    serializer = KardexSerializer

    def get(self, request, format=None):
        list = Kardex.objects.all()
        response = self.serializer(list, many=True)

        return HttpResponse(json.dumps(response.data), content_type='application/json')


def get_producto_control(request):

    if request.is_ajax():
        productoId = request.GET.get('productoId', None)
        almacenId = request.GET.get('almacenId', None)

        almacen_obj = Almacen.objects.get(pk=almacenId)
        producto_obj = Producto.objects.get(pk=productoId)
        control_producto = ControlProducto.objects.filter(
            producto=producto_obj, almacen=almacen_obj)
        if control_producto.exists():
            existencia = control_producto[0].stock
            precio_costo = control_producto[0].precio
        else:
            existencia = 0
            precio_costo = 0

        return JsonResponse({
            'success': True,
            'existencia': existencia,
            'precio_costo': precio_costo,
            'unit_primary': producto_obj.unidad_principal.abreviatura if producto_obj else None,
            'unit_secondary': producto_obj.unidad_secundaria.abreviatura if producto_obj.unidad_secundaria else None,
            'unit_equivalence': producto_obj.unidad_equivalencia if producto_obj else None,
        })


def obtener_propiedades_producto(request):
    if request.method == "GET":
        if request.is_ajax():
            search_string = request.GET.get('search_string', None)

            # item.creator = owner or item.moderated = False
            producto_obj = Producto.objects.filter(
                Q(nombre=search_string) | Q(codigo_principal=search_string))
            if producto_obj.exists():

                return JsonResponse({
                    'success': True,
                    'product': producto_obj[0].nombre,
                    'productId': producto_obj[0].producto_id,
                    'cost': producto_obj[0].precio_costo,
                    'unit_primary': producto_obj[0].unidad_principal.abreviatura,
                    'unit_secondary': producto_obj[0].unidad_secundaria.abreviatura if producto_obj[0].unidad_secundaria else None,
                    'unit_equivalence': producto_obj[0].unidad_equivalencia,
                })
            else:
                return JsonResponse({
                    'success': False,
                })
