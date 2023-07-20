from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Sum, F, Q, Func

import json
import datetime
from datetime import timedelta
from pytz import timezone
from decimal import Decimal

from .forms import ProveedorModalForm, PagoModalForm
from django.views import generic
from django.contrib.messages.views import SuccessMessageMixin

from apps.administracion import utils
from apps.administracion.models import Empresa, EntidadFinanciera, \
    TarjetaBancaria
from apps.sri.models import SriTarifaIVA, SriTipoComprobante, \
    SriTipoImpuesto, SriTipoMoneda, SriFormaPago

from apps.contabilidad.models import Pago, PagoTransferencia, PagoCredito, \
    FormaPago, EstadoPago

# from apps.contabilidad.Payment import Payment

from .models import OrdenCompra, OrdenCompraDetalle, OrdenCompraEstado, \
    Proveedor

from apps.cesta.models import Cesta, Item as CestaItem, Lote as CestaLote

from apps.unidadmedida.models import UnidadMedida
from apps.producto.models import Producto
from apps.servicio.models import Servicio
from apps.almacen.models import Almacen, \
    TipoMovimiento, Kardex, ProductoLote, ProductoSaldo, \
    ControlProducto, ControlProductoLote

from apps.usuario.models import Turno
from apps.administracion.models import Secuencia
from apps.retencion.models import ComprobanteRetencion, \
    ComprobanteRetencionDetalle

# librerias para PDF
from apps.administracion.render import render_to_pdf
from django.views.generic import View

# raw sql
from django.db import connection

import locale
# Set to users preferred locale:
locale.setlocale(locale.LC_ALL, '')

# Create your views here.


class BuscarComprobanteModal(ListView):
    model = OrdenCompra
    template_name = 'frontend/modals/buscar_comprobante_modal.html'
    context_object_name = 'listado_comprobantes'


class ListadoCompras(ListView):
    template_name = 'compra/listado_compras.html'

    def get_queryset(self):
        return OrdenCompra.objects.none()


def ajax_listado_compras(request):
    from_date = request.POST.get("startDate")
    to_date = request.POST.get("endDate")
    format_str = '%Y-%m-%d'
    # start_date = datetime.datetime.strptime(from_date, format_str)
    # end_date = datetime.datetime.strptime(to_date, format_str)

    print(from_date)
    print(to_date)

    try:
        query = """
            select orden_id, fecha_emision, proveedor_proveedor.nombre as proveedor, numero_comprobante, compra_ordencompraestado.nombre as estado, valor_total
            from compra_ordencompra
            inner join proveedor_proveedor on compra_ordencompra.proveedor_id = proveedor_proveedor.proveedor_id
            inner join compra_ordencompraestado on compra_ordencompra.estado_id = compra_ordencompraestado.orden_estado_id
            where date(fecha_emision) >= '%s' and date(fecha_emision) <= '%s'
            order by fecha_emision desc
        """ % (from_date, to_date)
    except ValueError:
        # ningún almacén seleccionado
        id_aux = 0
        query = """
            select orden_id, fecha_emision, proveedor_proveedor.nombre as proveedor, numero_comprobante, compra_ordencompraestado.nombre as estado, valor_total
            from compra_ordencompra
            inner join proveedor_proveedor on compra_ordencompra.proveedor_id = proveedor_proveedor.proveedor_id
            inner join compra_ordencompraestado on compra_ordencompra.estado_id = compra_ordencompraestado.orden_estado_id
            where compra_ordencompra.orden_id = %s
        """ % (id_aux)

    print(query)

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        print(rows)
        results = []
        columns = ('orden_id', 'fecha_emision', 'proveedor',
                   'numero_comprobante', 'estado', 'valor_total')
        for row in rows:
            results.append(dict(zip(columns, row)))
    return JsonResponse(results, safe=False)


class CrearCompra(ListView):
    context_object_name = 'orden'
    template_name = 'compra/factura.html'
    success_url = reverse_lazy('compra:listado_compras')

    def multiply(value, arg):
        return value * arg

    def get_queryset(self):
        # return Cesta.objects.filter(
        #    usuario=self.request.user, clave_apli='apli_compra',
        # clave_pers='Proveedor-1')[0]
        # user_basket, status = Cesta.objects.get_or_create(
        #    usuario=self.request.user, clave_apli='CART-COMPRA')
        # return user_basket
        return OrdenCompra.objects.none()

    def get(self, *args, **kwargs):
        turno_obj = Turno.objects.filter(
            usuario_creador=self.request.user, activo=True)
        if turno_obj.exists():
            return super(CrearCompra, self).get(*args, **kwargs)
        else:
            return redirect('contabilidad:mensaje_vista')

    def get_context_data(self, **kwargs):
        context = super(CrearCompra, self).get_context_data(**kwargs)
        context['tarifa'] = round(
            SriTarifaIVA.objects.filter(codigo='2')[0].porcentaje)

        today = datetime.date.today()
        # context['fecha_emision'] = format(today, '%d/%m/%Y')
        context['fecha_emision'] = format(today, '%Y-%m-%d')
        context['fecha_expira'] = format(today, '%Y-%m')

        # formas_pago_obj = FormaPago.objects.all()
        # context['formas_pagos'] = formas_pago_obj

        banco_obj = EntidadFinanciera.objects.values('entidad_id', 'nombre')
        context['bancos'] = banco_obj

        tarjeta_obj = TarjetaBancaria.objects.values('tarjeta_id', 'nombre')
        context['tarjetas'] = tarjeta_obj

        proveedor_obj = Proveedor.objects.filter(
            activo=True).values('proveedor_id', 'nombre').order_by('nombre')
        # Employee.objects.all().values('eng_name','rank')
        context['proveedores'] = proveedor_obj

        unidad_obj = UnidadMedida.objects.values('abreviatura')
        context['unidades'] = unidad_obj

        unidad_servicio_obj = UnidadMedida.objects.values('abreviatura')
        context['unidades_servicio'] = unidad_servicio_obj

        almacen_obj = Almacen.objects.values(
            'almacen_id', 'codigo').order_by('codigo')
        context['almacenes'] = almacen_obj

        # Usage
        # data=MyModel.objects.values('id','title','...','...')
        # data_dict = ValuesQuerySetToDict(data)
        # data_json = simplejson.dumps(data_dict)

        # sri_forma_pago_obj = SriFormaPago.objects.order_by('codigo')
        # context['formas_pagos'] = sri_forma_pago_obj

        # calculo resumen
        # current_user = self.request.user
        # subtotal = getSubtotalCarrito(current_user)
        # valor_descuento = getValorDescuentoCarrito(current_user)
        # valor_base_imponible = getSubtotalImptoCarrito(current_user)
        # valor_tarifa_cero = getSubtotalZeroCarrito(current_user)
        # valor_iva = getValorIvaCarrito(current_user)
        # valor_total = getValorTotalCarrito(current_user)

        """subtotal = 0
        valor_descuento = 0
        valor_base_imponible = 0
        valor_tarifa_cero = 0
        valor_iva = 0
        valor_total = 0

        context['subtotal'] = subtotal
        context['descuento'] = valor_descuento
        context['tarifa_base'] = valor_base_imponible
        context['tarifa_cero'] = valor_tarifa_cero
        context['impuesto'] = valor_iva
        context['total'] = valor_total"""

        return context


# class ModificarCompra(UpdateView):
def ModificarCompra(request, orden_id):
    # model = OrdenCompra
    # template_name = 'compra/producto.html'
    # form_class = CompraForm
    # success_url = reverse_lazy('compra:listado_compras')

    now = datetime.datetime.now()
    html = "<html><body>It is now %s.</body></html>" % now
    return HttpResponse(html)


class EliminarCompra(DeleteView):
    model = OrdenCompra
    template_name = 'compra/eliminar_compra.html'
    success_url = reverse_lazy('compra:listado_compras')


def busquedaProductos(request):
    if request.method == "GET":
        if request.is_ajax():
            # #proveedorId = request.GET.get('api_key', None)
            # filtro muchos a muchos
            # productos = Producto.objects.all().filter(proveedores__proveedor_id=proveedorId).values('producto_id', 'nombre', 'codigo_principal')
            # productos = Producto.objects.all().values('producto_id', 'nombre', 'codigo_principal')
            # productos = ProductoResumen.objects.all().values('producto_id', 'nombre', 'codigo_principal', 'existencia').order_by('nombre')
            # productos = Producto.objects.all().filter(proveedores__proveedor_id=proveedorId).values('producto_id', 'nombre', 'codigo_principal')

            # #productos = ProductoSaldo.objects.filter(producto__proveedores__proveedor_id=proveedorId).values('producto_id', 'producto__nombre', 'producto__codigo_principal', 'existencia')
            productos = ProductoSaldo.objects.all().values('producto_id', 'producto__nombre',
                                                           'producto__codigo_principal', 'existencia')
            # important: convert the QuerySet to a list object
            lista_productos = list(productos)
            return JsonResponse(lista_productos, safe=False)


def ajaxAgregarItem(request):
    if request.method == 'POST':
        dataId = request.POST.get('dataId', None)

        empresa_id = request.session['company_id']
        user_basket, status = Cesta.objects.get_or_create(
            usuario=request.user, clave_apli='CART-COMPRA', empresa_id=empresa_id)

        # verifica codigo (bien o servicio)
        cadena_buscada = 'SRV-'
        # Si la sub-cadena no está presente el programa imprimirá el valor -1
        posicion_coincidencia = dataId.find(cadena_buscada)

        if (posicion_coincidencia == -1):
            # agregar productos
            productoId = dataId

            producto_obj = Producto.objects.get(pk=productoId)
            precio = producto_obj.precio_costo
            qty = 1

            if producto_obj.iva.codigo == '2':
                subtotal_12 = precio
                subtotal_0 = 0
                porcentaje_iva = producto_obj.iva.porcentaje
                valor_iva = round((precio * porcentaje_iva) / 100, 5)
                valor_total = subtotal_12 + valor_iva
            else:
                subtotal_12 = 0
                subtotal_0 = precio
                valor_iva = 0
                valor_total = precio

            cesta_item = CestaItem()
            cesta_item.tipo = 'PROD'
            cesta_item.producto = producto_obj
            cesta_item.cantidad = qty
            cesta_item.unidad_medida = producto_obj.unidad_principal
            cesta_item.precio = precio
            cesta_item.valor_subtotal_sin_impuesto = precio
            cesta_item.valor_subtotal_12 = subtotal_12
            cesta_item.valor_subtotal_0 = subtotal_0
            cesta_item.valor_iva = valor_iva
            cesta_item.valor_total = valor_total
            # item.cesta = cesta
            cesta_item.save()
            user_basket.items.add(cesta_item)

            if producto_obj.tiene_vencimiento or producto_obj.tiene_serie:

                markup = "<tr>" \
                    "<td style='display:none;'>" + str(cesta_item.pk) + "</td>" \
                    "<td data-title='Descripción'><a href=/producto/detalle_producto/" + str(productoId) + " target='_blank'>" + producto_obj.nombre + "</a></td>" \
                    "<td data-title='Cantidad' class='numeric'>" + str(locale.format('%.2f', qty)) + "</td>" \
                    "<td data-title='Und' class='text-center'>" + producto_obj.unidad_principal.abreviatura + "</td>" \
                    "<td data-title='Precio' class='numeric'>" + str(locale.currency(precio)) + "</td>" \
                    "<td data-title='Total' class='numeric'>" + str(locale.currency(qty * precio)) + "</td>" \
                    "<td data-title='Acciones' class='text-center'>" \
                    "<div class='btn-group btn-group-sm'>" \
                    "<button type='button' data-id=" + str(cesta_item.pk) + " class='btn btn-primary editButton'><i class='fas fa-edit'></i></button>" \
                    "</div>" \
                    "&nbsp;" \
                    "<div class='btn-group btn-group-sm'>" \
                    "<button type='button' data-id=" + str(cesta_item.pk) + " class='btn btn-info searchButton'><i class='fas fa-search'></i></button>" \
                    "</div>" \
                    "&nbsp;" \
                    "<div class='btn-group btn-group-sm'>" \
                    "<button type='button' data-id=" + str(cesta_item.pk) + " class='btn btn-warning deleteButton'><i class='fas fa-trash'></i></button>" \
                    "</div>" \
                    "</td>" \
                    "</tr>"
            else:
                markup = "<tr>" \
                    "<td style='display:none;'>" + str(cesta_item.pk) + "</td>" \
                    "<td data-title='Descripción'><a href=/producto/detalle_producto/" + str(productoId) + " target='_blank'>" + producto_obj.nombre + "</a></td>" \
                    "<td data-title='Cantidad' class='numeric'>" + str(locale.format('%.2f', qty)) + "</td>" \
                    "<td data-title='Und' class='text-center'>" + producto_obj.unidad_principal.abreviatura + "</td>" \
                    "<td data-title='Precio' class='numeric'>" + str(locale.currency(precio)) + "</td>" \
                    "<td data-title='Total' class='numeric'>" + str(locale.currency(qty * precio)) + "</td>" \
                    "<td data-title='Acciones' class='text-center'>" \
                    "<div class='btn-group btn-group-sm'>" \
                    "<button type='button' data-id=" + str(cesta_item.pk) + " class='btn btn-primary editButton'><i class='fas fa-edit'></i></button>" \
                    "</div>" \
                    "&nbsp;" \
                    "<div class='btn-group btn-group-sm'>" \
                    "<button type='button' class='btn btn-default searchButton' disabled><i class='fas fa-search'></i></button>" \
                    "</div>" \
                    "&nbsp;" \
                    "<div class='btn-group btn-group-sm'>" \
                    "<button type='button' data-id=" + str(cesta_item.pk) + " class='btn btn-warning deleteButton'><i class='fas fa-trash'></i></button>" \
                    "</div>" \
                    "</td>" \
                    "</tr>"

            # calculo resumen
            filasEnCarrito = user_basket.obtener_total_filas()
            subtotal = user_basket.obtener_sub_total()
            valor_descuento = user_basket.obtener_total_descuento()
            valor_base_imponible = user_basket.obtener_base_imponible()
            valor_tarifa_cero = user_basket.obtener_total_tarifa_cero()
            valor_iva = user_basket.obtener_total_iva()
            valor_total = user_basket.obtener_gran_total()

            return JsonResponse({
                'success': True,
                'markup': markup,
                'totalFilas': filasEnCarrito,
                'subtotal': locale.currency(subtotal),
                'descuento': locale.currency(valor_descuento),
                'tarifa_base': locale.currency(valor_base_imponible),
                'tarifa_cero': locale.currency(valor_tarifa_cero),
                'impuesto': locale.currency(valor_iva),
                'total': locale.currency(valor_total)
            })
        else:
            # agregar servicios
            servicioId = dataId[4:]  # subtrae Id, dataId = 'SRV-1'

            servicio_obj = Servicio.objects.get(pk=servicioId)
            precio = servicio_obj.precio

            if servicio_obj.iva.codigo == '2':
                subtotal_12 = precio
                subtotal_0 = 0
                porcentaje_iva = servicio_obj.iva.porcentaje
                valor_iva = round((precio * porcentaje_iva) / 100, 5)
                valor_total = subtotal_12 + valor_iva
            else:
                subtotal_12 = 0
                subtotal_0 = precio
                valor_iva = 0
                valor_total = precio

            qty = 1
            cesta_item = CestaItem()
            cesta_item.tipo = 'SERV'
            cesta_item.servicio = servicio_obj
            cesta_item.cantidad = qty
            cesta_item.unidad_medida = servicio_obj.unidad_medida
            cesta_item.precio = precio
            cesta_item.valor_subtotal_sin_impuesto = precio
            cesta_item.valor_subtotal_12 = subtotal_12
            cesta_item.valor_subtotal_0 = subtotal_0
            cesta_item.valor_iva = valor_iva
            cesta_item.valor_total = valor_total
            # item.cesta = cesta
            cesta_item.save()
            user_basket.items.add(cesta_item)

            markup = "<tr>" \
                "<td style='display:none;'>" + str(cesta_item.pk) + "</td>" \
                "<td data-title='Descripción'><a href=/servicio/detalle_servicio/" + str(servicioId) + " target='_blank'>" + servicio_obj.nombre + "</a></td>" \
                "<td data-title='Cantidad' class='numeric'>" + str(locale.format('%.2f', qty)) + "</td>" \
                "<td data-title='Und' class='text-center'>" + servicio_obj.unidad_medida.abreviatura + "</td>" \
                "<td data-title='Precio' class='numeric'>" + str(locale.currency(precio)) + "</td>" \
                "<td data-title='Total' class='numeric'>" + str(locale.currency(qty * precio)) + "</td>" \
                "<td data-title='Acciones' class='text-center'>" \
                "<div class='btn-group btn-group-sm'>" \
                "<button type='button' data-id=" + 'SRV-' + str(cesta_item.pk) + " class='btn btn-primary editButton'><i class='fas fa-edit'></i></button>" \
                "</div>" \
                "&nbsp;" \
                "<div class='btn-group btn-group-sm'>" \
                "<button type='button' class='btn btn-default glyphicon glyphicon-search searchButton' disabled><i class='fas fa-search'></i></button>" \
                "</div>" \
                "&nbsp;" \
                "<div class='btn-group btn-group-sm'>" \
                "<button type='button' data-id=" + 'SRV-' + str(cesta_item.pk) + " class='btn btn-warning deleteButton'><i class='fas fa-trash'></i></button>" \
                "</div>" \
                "</td>" \
                "</tr>"

            # calculo resumen
            filasEnCarrito = user_basket.obtener_total_filas()
            subtotal = user_basket.obtener_sub_total()
            valor_descuento = user_basket.obtener_total_descuento()
            valor_base_imponible = user_basket.obtener_base_imponible()
            valor_tarifa_cero = user_basket.obtener_total_tarifa_cero()
            valor_iva = user_basket.obtener_total_iva()
            valor_total = user_basket.obtener_gran_total()

            return JsonResponse({
                'success': True,
                'markup': markup,
                'totalFilas': filasEnCarrito,
                'subtotal': locale.currency(subtotal),
                'descuento': locale.currency(valor_descuento),
                'tarifa_base': locale.currency(valor_base_imponible),
                'tarifa_cero': locale.currency(valor_tarifa_cero),
                'impuesto': locale.currency(valor_iva),
                'total': locale.currency(valor_total)
            })


def localizarAgregarElemento(request):
    if request.method == 'POST':
        postVar = request.POST.get('search_string', None)

        empresa_id = request.session['company_id']
        user_basket, status = Cesta.objects.get_or_create(
            usuario=request.user, clave_apli='CART-COMPRA', empresa_id=empresa_id)

        # BUSCA EN TABLA PRODUCTOS
        producto_obj = Producto.objects.get(
            Q(codigo_principal=postVar) | Q(nombre=postVar))
        if (producto_obj):
            # PRODUCTO
            precio = producto_obj.precio_costo
            qty = 1

            if producto_obj.iva.codigo == '2':
                subtotal_12 = precio
                subtotal_0 = 0
                porcentaje_iva = producto_obj.iva.porcentaje
                valor_iva = round((precio * porcentaje_iva) / 100, 5)
                valor_total = subtotal_12 + valor_iva
            else:
                subtotal_12 = 0
                subtotal_0 = precio
                valor_iva = 0
                valor_total = precio

            cesta_item = CestaItem()
            cesta_item.tipo = 'PROD'
            cesta_item.producto = producto_obj
            cesta_item.cantidad = qty
            cesta_item.unidad_medida = producto_obj.unidad_principal
            cesta_item.precio = precio
            cesta_item.valor_subtotal_sin_impuesto = precio
            cesta_item.valor_subtotal_12 = subtotal_12
            cesta_item.valor_subtotal_0 = subtotal_0
            cesta_item.valor_iva = valor_iva
            cesta_item.valor_total = valor_total
            # item.cesta = cesta
            cesta_item.save()
            user_basket.items.add(cesta_item)

            if producto_obj.tiene_vencimiento or producto_obj.tiene_serie:

                markup = "<tr>" \
                    "<td style='display:none;'>" + str(cesta_item.pk) + "</td>" \
                    "<td data-title='Descripción'><a href=/producto/detalle_producto/" + str(producto_obj.pk) + " target='_blank'>" + producto_obj.nombre + "</a></td>" \
                    "<td data-title='Cantidad' class='numeric'>" + str(locale.format('%.2f', qty)) + "</td>" \
                    "<td data-title='Und' class='text-center'>" + producto_obj.unidad_principal.abreviatura + "</td>" \
                    "<td data-title='Precio' class='numeric'>" + str(locale.currency(precio)) + "</td>" \
                    "<td data-title='Total' class='numeric'>" + str(locale.currency(qty * precio)) + "</td>" \
                    "<td data-title='Acciones' class='text-center'>" \
                    "<div class='btn-group btn-group-sm'>" \
                    "<button type='button' data-id=" + str(cesta_item.pk) + " class='btn btn-primary editButton'><i class='fas fa-edit'></i></button>" \
                    "</div>" \
                    "&nbsp;" \
                    "<div class='btn-group btn-group-sm'>" \
                    "<button type='button' data-id=" + str(cesta_item.pk) + " class='btn btn-info searchButton'><i class='fas fa-search'></i></button>" \
                    "</div>" \
                    "&nbsp;" \
                    "<div class='btn-group btn-group-sm'>" \
                    "<button type='button' data-id=" + str(cesta_item.pk) + " class='btn btn-warning deleteButton'><i class='fas fa-trash'></i></button>" \
                    "</div>" \
                    "</td>" \
                    "</tr>"
            else:
                markup = "<tr>" \
                    "<td style='display:none;'>" + str(cesta_item.pk) + "</td>" \
                    "<td data-title='Descripción'><a href=/producto/detalle_producto/" + str(producto_obj.pk) + " target='_blank'>" + producto_obj.nombre + "</a></td>" \
                    "<td data-title='Cantidad' class='numeric'>" + str(locale.format('%.2f', qty)) + "</td>" \
                    "<td data-title='Und' class='text-center'>" + producto_obj.unidad_principal.abreviatura + "</td>" \
                    "<td data-title='Precio' class='numeric'>" + str(locale.currency(precio)) + "</td>" \
                    "<td data-title='Total' class='numeric'>" + str(locale.currency(qty * precio)) + "</td>" \
                    "<td data-title='Acciones' class='text-center'>" \
                    "<div class='btn-group btn-group-sm'>" \
                    "<button type='button' data-id=" + str(cesta_item.pk) + " class='btn btn-primary editButton'><i class='fas fa-edit'></i></button>" \
                    "</div>" \
                    "&nbsp;" \
                    "<div class='btn-group btn-group-sm'>" \
                    "<button type='button' class='btn btn-default searchButton' disabled><i class='fas fa-search'></i></button>" \
                    "</div>" \
                    "&nbsp;" \
                    "<div class='btn-group btn-group-sm'>" \
                    "<button type='button' data-id=" + str(cesta_item.pk) + " class='btn btn-warning deleteButton'><i class='fas fa-trash'></i></button>" \
                    "</div>" \
                    "</td>" \
                    "</tr>"

            # calculo resumen
            filasEnCarrito = user_basket.obtener_total_filas()
            subtotal = user_basket.obtener_sub_total()
            valor_descuento = user_basket.obtener_total_descuento()
            valor_base_imponible = user_basket.obtener_base_imponible()
            valor_tarifa_cero = user_basket.obtener_total_tarifa_cero()
            valor_iva = user_basket.obtener_total_iva()
            valor_total = user_basket.obtener_gran_total()

            return JsonResponse({
                'success': True,
                'markup': markup,
                'totalFilas': filasEnCarrito,
                'subtotal': locale.currency(subtotal),
                'descuento': locale.currency(valor_descuento),
                'tarifa_base': locale.currency(valor_base_imponible),
                'tarifa_cero': locale.currency(valor_tarifa_cero),
                'impuesto': locale.currency(valor_iva),
                'total': locale.currency(valor_total)
            })
        else:
            # SERVICIO
            return JsonResponse({
                'success': False,
            })


def ajaxEditarItem(request):
    import locale
    # Set to users preferred locale:
    locale.setlocale(locale.LC_ALL, '')

    if request.method == 'GET':
        getVar = request.GET.get('id', None)

        # REVISAR SI ES PRODUCTO O SERVICIO
        cadena_buscada = 'SRV-'
        posicion_coincidencia = getVar.find(cadena_buscada)

        if (posicion_coincidencia == -1):
            # PRODUCTO
            carritoId = getVar

            # buscar registro en CestaItem
            cesta_item = CestaItem.objects.get(pk=carritoId)

            return JsonResponse({
                'success': True,
                'id': carritoId,
                'product': cesta_item.producto.nombre,
                'category': 'PROD',
                'qty': round(cesta_item.cantidad, 2),
                'unit': cesta_item.unidad_medida.abreviatura,
                'unit_primary': cesta_item.producto.unidad_principal.abreviatura,
                'unit_secondary': cesta_item.producto.unidad_secundaria.abreviatura if cesta_item.producto.unidad_secundaria else None,
                'unit_equivalence': cesta_item.producto.unidad_equivalencia,
                'price': round(cesta_item.precio, 3),
                'discount': round(cesta_item.porcentaje_descuento, 2)
            })
        else:
            # SERVICIO
            carritoId = getVar[4:]  # subtrae Id, getVar = 'SRV-1'

            # buscar registro en Carrito
            cesta_item = CestaItem.objects.get(pk=carritoId)

            return JsonResponse({
                'success': True,
                'id': 'SRV-' + str(carritoId),
                'product': cesta_item.servicio.nombre,
                'category': 'SERV',
                'qty': round(cesta_item.cantidad, 2),
                'unit': cesta_item.unidad_medida.abreviatura,
                'unit_primary': cesta_item.servicio.unidad_medida.abreviatura,
                'unit_equivalence': 1,
                'price': round(cesta_item.precio, 2),
                'discount': round(cesta_item.porcentaje_descuento, 2)
            })

    else:  # request.method == 'POST'
        data = request.POST.copy()
        itemID = data.get('id')
        cantidad = locale.atof(data.get('qty', 1))
        unidad = data.get('unit')
        precio = locale.atof(data.get('price', 0))
        porcentaje_descuento = locale.atof(data.get('discount', 0))

        cadena_buscada = 'SRV-'
        posicion_coincidencia = itemID.find(cadena_buscada)
        if (posicion_coincidencia == -1):
            # PRODUCTO
            unit_obj = UnidadMedida.objects.filter(abreviatura=unidad)[0]
            cesta_item = CestaItem.objects.get(pk=itemID)

            # calculos
            subtotal_linea = cantidad * precio
            valor_descuento_linea = round(
                (subtotal_linea * porcentaje_descuento) / 100, 5)

            if cesta_item.producto.iva.codigo == '2':
                subtotal_12 = subtotal_linea - valor_descuento_linea
                subtotal_0 = 0
                porcentaje_iva = float(cesta_item.producto.iva.porcentaje)
                valor_iva = round((subtotal_12 * porcentaje_iva) / 100, 5)
                valor_total = subtotal_12 + valor_iva
            else:
                subtotal_12 = 0
                subtotal_0 = subtotal_linea - valor_descuento_linea
                valor_iva = 0
                valor_total = subtotal_0

            # actualizar item
            cesta_item.cantidad = cantidad
            cesta_item.unidad_medida = unit_obj
            cesta_item.precio = precio
            cesta_item.porcentaje_descuento = porcentaje_descuento
            cesta_item.valor_descuento = valor_descuento_linea
            cesta_item.valor_subtotal_sin_impuesto = subtotal_linea
            cesta_item.valor_subtotal_12 = subtotal_12
            cesta_item.valor_subtotal_0 = subtotal_0
            cesta_item.valor_subtotal_no_objeto_iva = 0
            cesta_item.valor_subtotal_exento = 0
            cesta_item.valor_base_imponible_ibrpnr = 0
            cesta_item.valor_subtotal_ibrpnr = 0
            cesta_item.valor_ice = 0
            cesta_item.valor_iva = valor_iva
            cesta_item.valor_total = valor_total
            cesta_item.save()

        else:
            # SERVICIO
            unidad = data.get('unit_service')
            item_id = itemID[4:]  # subtrae Id, itemID = 'SRV-1'
            unit_service_obj = UnidadMedida.objects.filter(
                abreviatura=unidad)[0]
            cesta_item = CestaItem.objects.get(pk=item_id)

            # calculos
            subtotal_linea = float(cantidad) * float(precio)
            valor_descuento_linea = round(
                (subtotal_linea * float(porcentaje_descuento)) / 100, 5)

            if cesta_item.servicio.iva.codigo == '2':
                subtotal_12 = subtotal_linea - valor_descuento_linea
                subtotal_0 = 0
                porcentaje_iva = float(cesta_item.servicio.iva.porcentaje)
                valor_iva = round((subtotal_12 * porcentaje_iva) / 100, 5)
                valor_total = subtotal_12 + valor_iva
            else:
                subtotal_12 = 0
                subtotal_0 = subtotal_linea - valor_descuento_linea
                valor_iva = 0
                valor_total = subtotal_0

            # actualizar carrito
            cesta_item.cantidad = cantidad
            # cesta_item.unidad = unit_obj
            cesta_item.unidad_medida = unit_service_obj
            cesta_item.precio = precio
            cesta_item.porcentaje_descuento = porcentaje_descuento
            cesta_item.valor_descuento = valor_descuento_linea
            cesta_item.valor_subtotal_sin_impuesto = subtotal_linea
            cesta_item.valor_subtotal_12 = subtotal_12
            cesta_item.valor_subtotal_0 = subtotal_0
            cesta_item.valor_subtotal_no_objeto_iva = 0
            cesta_item.valor_subtotal_exento = 0
            cesta_item.valor_base_imponible_ibrpnr = 0
            cesta_item.valor_subtotal_ibrpnr = 0
            cesta_item.valor_ice = 0
            cesta_item.valor_iva = valor_iva
            cesta_item.valor_total = valor_total
            cesta_item.save()

        import locale
        # Set to users preferred locale:
        locale.setlocale(locale.LC_ALL, '')

        # calculo resumen
        empresa_id = request.session['company_id']
        user_basket = Cesta.objects.filter(
            usuario=request.user, clave_apli='CART-COMPRA',
            empresa_id=empresa_id)[0]

        subtotal = user_basket.obtener_sub_total()
        valor_descuento = user_basket.obtener_total_descuento()
        valor_base_imponible = user_basket.obtener_base_imponible()
        valor_tarifa_cero = user_basket.obtener_total_tarifa_cero()
        valor_iva = user_basket.obtener_total_iva()
        valor_total = user_basket.obtener_gran_total()

        return JsonResponse({
            'success': True,
            'id': itemID,
            'cantidad': locale.format('%.2f', cantidad),
            'unidad': unidad,
            'precio': locale.currency(precio),
            'total_linea': locale.currency(cantidad * precio),
            'subtotal': locale.currency(subtotal),
            'descuento': locale.currency(valor_descuento),
            'tarifa_base': locale.currency(valor_base_imponible),
            'tarifa_cero': locale.currency(valor_tarifa_cero),
            'impuesto': locale.currency(valor_iva),
            'total': locale.currency(valor_total)
        })


def ajaxEliminarItem(request):
    if request.method == 'POST':
        if request.is_ajax():
            itemID = request.POST.get('itemId', None)
            cadena_buscada = 'SRV-'
            posicion_coincidencia = itemID.find(cadena_buscada)

            if (posicion_coincidencia == -1):
                # PRODUCTO
                item = CestaItem.objects.get(pk=itemID)
                item.delete()
            else:
                # SERVICIO
                itemID = itemID[4:]  # subtrae Id, itemID = 'SRV-1'
                item = CestaItem.objects.get(pk=itemID)
                item.delete()

            import locale
            # Set to users preferred locale:
            locale.setlocale(locale.LC_ALL, '')

            # calculo resumen
            user_basket = Cesta.objects.filter(
                usuario=request.user, clave_apli='CART-COMPRA')[0]
            filasEnCarrito = user_basket.obtener_total_filas()
            subtotal = user_basket.obtener_sub_total()
            valor_descuento = user_basket.obtener_total_descuento()
            valor_base_imponible = user_basket.obtener_base_imponible()
            valor_tarifa_cero = user_basket.obtener_total_tarifa_cero()
            valor_iva = user_basket.obtener_total_iva()
            valor_total = user_basket.obtener_gran_total()

            return JsonResponse({
                'success': True,
                'total_filas': filasEnCarrito,
                'subtotal': locale.currency(subtotal),
                'descuento': locale.currency(valor_descuento),
                'tarifa_base': locale.currency(valor_base_imponible),
                'tarifa_cero': locale.currency(valor_tarifa_cero),
                'impuesto': locale.currency(valor_iva),
                'total': locale.currency(valor_total)
            })


class SimpleObject(object):

    def __init__(self, _dict):
        self.__dict__.update(_dict)


def agregar_lote(request):
    if request.method == "GET":
        itemID = request.GET.get('id', None)

        # cesta_item = CestaItem.objects.get(pk=itemID)

        # cesta = Cesta.objects.filter(
        # usuario=request.user, clave_apli='apli_compra',
        # clave_pers='Proveedor-1')[0]

        cesta_lote = CestaLote.objects.filter(item__pk=itemID)

        result = []
        if cesta_lote:
            for item in cesta_lote:
                result.append({
                    'lote_pk': item.id,
                    'lote_numero': item.lote_numero,
                    'fecha_caducidad': item.fecha_caducidad.strftime(
                        '%Y-%m-%d'),
                    'cantidad': str(item.cantidad),
                })
        data = json.dumps(result)

        return JsonResponse({
            'success': True,
            'cesta_item_pk': itemID,
            'lotejson': data
        })
    else:  # request.method == 'POST'
        # cesta_item_pk = request.POST.get("id")
        # arrayLote = request.POST.getlist('loteArray[]')
        # arrayExpira = request.POST.getlist('expiraArray[]')
        # arrayQty = request.POST.getlist('qtyArray[]')

        form_data = request.POST.get("formData")
        form_data_dict = {}
        form_data_list = json.loads(form_data)

        i = 0
        vc = 0
        arrayLote = []
        arrayExpira = []
        arrayQty = []
        for field in form_data_list:
            form_data_dict[field["name"]] = field["value"]
            if i >= 3:
                if (i % 3) == 0:
                    vc = 0
                if (vc == 0):
                    arrayLote.append(field["value"])
                elif (vc == 1):
                    arrayExpira.append(field["value"])
                else:
                    arrayQty.append(field["value"])
                vc = vc + 1
            i = i + 1

        cesta_item_pk = form_data_dict['id']

        # eliminar lotes existentes
        CestaLote.objects.filter(item_id=cesta_item_pk).delete()

        i = 0
        while i < len(arrayLote):
            # print(arrayLote[i])
            # print(arrayExpira[i])
            # print(arrayQty[i])

            # if arrayPk[i]:
            # modificar lote
            #    cesta_lote = CestaLote.objects.get(pk=arrayPk[i])
            #    cesta_lote.lote_numero = arrayLote[i]
            #    cesta_lote.fecha_caducidad = arrayExpira[i]
            #    cesta_lote.cantidad = arrayQty[i]
            #    cesta_lote.save()
            # else:

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


"""
def total_filas_cesta(request):

    if request.method == "GET":

        user_basket = Cesta.objects.filter(usuario=request.user,
                                           clave_apli='CART-COMPRA')[0]

        return JsonResponse({
            'success': True,
            'total_filas': user_basket.obtener_total_filas()
        })
"""

""" FUNCIÓN INTERCAMBIAR INFORMACIÓN FORMULARIO DE PAGO Y EL CONTROLADOR """


def ajaxIntercambioResumen(request):
    if request.method == 'POST':
        grand_total = request.POST.get('grand_total', default=None)
        fecha_emision = request.POST.get('fecha_emision', default=None)
        proveedor_id = request.POST.get('proveedor_id', default=None)
        nro_comp = request.POST.get('nro_comp', default=None)
        nro_guia = request.POST.get('nro_guia', default=None)

        return JsonResponse({
            'success': True,
            'grand_total': grand_total,
            'fecha_emision': fecha_emision,
            'proveedor_id': proveedor_id,
            'nro_comp': nro_comp,
            'nro_guia': nro_guia,
        })


def guardarOrden(request):
    if request.method == 'POST':
        data = request.POST.copy()
        proveedor_id = data.get('proveedor_id', default=None)
        fecha_emision = data.get('fecha_emision', default=None)
        nro_comp = data.get('nro_comp', default=None)
        nro_guia = data.get('nro_guia', default=None)
        almacen_id = data.get('almacen_id', default=None)

        # sri_codigo_pago = data.get('payment_method', default=None)

        current_user = request.user
        proveedor_obj = Proveedor.objects.get(pk=proveedor_id)
        tipo_comprobante_obj = SriTipoComprobante.objects.filter(
            codigo='01')[0]
        # forma_pago_obj = SriFormaPago.objects.filter(codigo = sri_codigo_pago)[0]

        dt_obj = datetime.datetime.now()
        # 2018-11-10T18:48:20-05:00 UTC
        hora = dt_obj.strftime("%H:%M:%S")
        # date_str = datetime.datetime.strptime('%s %s' % (fecha_emision, hora), "%d/%m/%Y %H:%M:%S")
        datetime_obj = datetime.datetime.strptime(
            '%s %s' % (fecha_emision, hora), "%Y-%m-%d %H:%M:%S")
        datetime_obj_utc = datetime_obj.replace(tzinfo=timezone('UTC'))

        # calculo resumen
        # current_user = request.user
        # subtotal = getSubtotalCarrito(current_user)
        # valor_descuento = getValorDescuentoCarrito(current_user)
        # valor_base_imponible = getSubtotalImptoCarrito(current_user)
        # valor_tarifa_cero = getSubtotalZeroCarrito(current_user)
        # valor_iva = getValorIvaCarrito(current_user)
        # valor_total = getValorTotalCarrito(current_user)
        # estado_obj = OrdenCompraEstado.objects.get(pk=1)  # 1 => 'REGISTRADA'

        import locale
        # Set to users preferred locale:
        locale.setlocale(locale.LC_ALL, '')

        # calculo resumen
        empresa_id = request.session['company_id']
        user_basket = Cesta.objects.filter(
            usuario=request.user, clave_apli='CART-COMPRA',
            empresa_id=empresa_id)[0]

        subtotal = user_basket.obtener_sub_total()
        valor_descuento = user_basket.obtener_total_descuento()
        valor_base_imponible = user_basket.obtener_base_imponible()
        valor_tarifa_cero = user_basket.obtener_total_tarifa_cero()
        valor_iva = user_basket.obtener_total_iva()
        valor_total = user_basket.obtener_gran_total()

        estado_obj = OrdenCompraEstado.objects.get(pk=1)  # 1 => 'REGISTRADA'

        orden = OrdenCompra()
        orden.empresa_id = empresa_id
        orden.proveedor = proveedor_obj
        orden.sri_tipo_comprobante = tipo_comprobante_obj
        # orden.sri_forma_pago = forma_pago_obj
        orden.usuario_creador = current_user
        orden.fecha_emision = datetime_obj_utc
        orden.numero_comprobante = nro_comp
        orden.guia_remision = nro_guia
        orden.valor_descuento = valor_descuento
        orden.valor_subtotal_sin_impuesto = subtotal
        orden.valor_subtotal_12 = valor_base_imponible
        orden.valor_subtotal_0 = valor_tarifa_cero
        orden.valor_ice = 0
        orden.valor_iva = valor_iva
        orden.valor_total = valor_total
        orden.estado = estado_obj

        orden.save()

        guardarOrdenDetalle(orden, user_basket)

        agregarTransKardex(
            orden=orden, cesta=user_basket, almacen_id=almacen_id,
            usuario=current_user)

        # PROCESAR RETENCIÓN
        # guardarRetencion(orden=orden, usuario=current_user, tabla=pPayTable)

        # PROCESAR LIBRO DIARIO
        # daily = Daily(current_user, tipo_flujo="HABER",
        #              referencia="Compra", tabla=pPayTable, orden=buysell)
        # daily.procesar()

        # vaciar cesta de compras
        user_basket.vaciar_cesta()

        return JsonResponse({
            'success': True,
        })


def guardarOrdenDetalle(orden, user_basket):
    # guardar carrito en detalle de facturas
    items = user_basket.obtener_items()

    for item in items:
        orden_item = OrdenCompraDetalle()
        orden_item.compra = orden
        if item.tipo == 'PROD':  # producto
            orden_item.tipo = 'P'
            orden_item.producto = item.producto
        else:
            orden_item.tipo = 'S'
            orden_item.servicio = item.servicio
        orden_item.cantidad = item.cantidad
        orden_item.unidad = item.unidad_medida
        orden_item.precio_costo = item.precio
        orden_item.porcentaje_descuento = item.porcentaje_descuento
        orden_item.valor_descuento = item.valor_descuento
        orden_item.valor_subtotal_sin_impuesto = item.valor_subtotal_sin_impuesto
        orden_item.valor_subtotal_12 = item.valor_subtotal_12
        orden_item.valor_subtotal_0 = item.valor_subtotal_0
        orden_item.valor_subtotal_no_objeto_iva = item.valor_subtotal_no_objeto_iva
        orden_item.valor_subtotal_exento = item.valor_subtotal_exento
        orden_item.valor_base_imponible_ibrpnr = item.valor_base_imponible_ibrpnr
        orden_item.valor_subtotal_ibrpnr = item.valor_subtotal_ibrpnr
        orden_item.valor_ice = item.valor_ice
        orden_item.valor_iva = item.valor_iva
        orden_item.valor_total = item.valor_total
        orden_item.save()

        # guardarLote(buyline, item.id)

    return True


"""
def guardarLote(buyline, cart_id):
    lotes_cart_obj = CarritoCompraLote.objects.filter(carrito_id=cart_id)
    if lotes_cart_obj:
        for lote in lotes_cart_obj:
            detlote = DetalleLote()
            detlote.ordendetalle =  buyline
            detlote.producto = lote.producto
            detlote.lote_numero = lote.lote_numero
            detlote.fecha_caducidad = lote.fecha_caducidad
            detlote.cantidad = lote.cantidad
            detlote.save()
    return True
"""

""" FUNCIÓN AGREGAR TRANSACCIÓN AL INVENTARIO """


def agregarTransKardex(orden, cesta, almacen_id, usuario):
    # guardar carrito en detalle de facturas
    # productos_obj = CarritoCompra.objects.filter(usuario=usuario)
    # referencia_obj = OrigenMovimiento.objects.get(pk=2)  # 2 = 'ENTRADA =>
    # ORDEN DE COMPRA'
    """#for item in productos_obj:
        trans_inv = Kardex()
        trans_inv.movimiento = utils.inventory_flow["ENTRADA"]
        # trans_inv.referencia = referencia_obj
        trans_inv.usuario_creador = current_user
        trans_inv.producto = item.producto
        trans_inv.cantidad = item.cantidad
        trans_inv.costo = item.precio
        trans_inv.unidad = item.unidad
        trans_inv.clave_externa = buysell.pk
        trans_inv.numero_comprobante = buysell.numero_comprobante
        trans_inv.referencia = 'Compra'
        # trans_inv.compra_id = buysell.pk
        # trans_inv.venta_id = 0
        # trans_inv.proforma_id = 0
        trans_inv.bodega_id = bodega_id
        # trans_inv.comentario = referencia_obj.descripcion
        trans_inv.save()"""

    # metodo_costo = usuario.perfil.empresa.metodo_costo
    # my_company_id = request.session['company_id']

    # cart = CarritoCompra.objects.filter(usuario=usuario)

    tipo_movimiento_obj = TipoMovimiento.objects.filter(codigo='ENT_FAC')[0]

    almacen_obj = Almacen.objects.get(pk=almacen_id)
    # now = datetime.datetime.now()

    # fecha_operacion_obj = orden.fecha_emision
    fecha_operacion_obj = orden.fecha_emision.strftime('%Y-%m-%d')

    items = cesta.obtener_items()
    for item in items:
        if item.tipo == 'PROD':  # PRODUCTO
            kardex = Kardex()
            # kardex.tipo = 1
            kardex.movimiento = tipo_movimiento_obj
            kardex.orden_id = orden.pk
            kardex.numero_comprobante = orden.numero_comprobante
            kardex.referencia = "Compra"
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
                    producto_obj = item.producto
                    kardex_ant = Kardex.objects.filter(
                        producto=producto_obj,
                        almacen=almacen_obj,
                        created_at__date__lte=fecha_operacion_obj).latest('created_at')
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

            # kardex.empresa = usuario.perfil.empresa
            kardex.empresa_id = orden.empresa_id
            kardex.almacen_id = almacen_id
            kardex.usuario_creador = usuario
            kardex.save()

            seguimientoLote(kardex, item.id, usuario)

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

    return True


def seguimientoLote(kardex, item_id, current_user):
    cesta_lote = CestaLote.objects.filter(item__pk=item_id)

    if cesta_lote:
        for lote_item in cesta_lote:
            almacen_lote = ProductoLote.objects.filter(
                producto=kardex.producto,
                lote_numero=lote_item.lote_numero,
                fecha_caducidad=lote_item.fecha_caducidad)
            if almacen_lote.exists():
                lote_ant = ControlProductoLote.objects.filter(
                    producto=kardex.producto,
                    lote=almacen_lote[0],
                    almacen=kardex.almacen)
                if lote_ant:
                    cantidad_lote = lote_ant[0].cantidad + lote_item.cantidad
                else:
                    cantidad_lote = lote_item.cantidad

                control_lote = ControlProductoLote.objects.update_or_create(
                    lote=almacen_lote[0],
                    producto=almacen_lote[0].producto,
                    almacen=kardex.almacen,
                    defaults={'cantidad': cantidad_lote}
                )
            else:
                # CREAR NUEVO LOTE
                lote_almacen = ProductoLote()
                lote_almacen.usuario_creador = current_user
                # lote_almacen.kardex = kardex
                # lote_almacen.almacen = kardex.almacen
                lote_almacen.producto = lote_item.item.producto
                lote_almacen.lote_numero = lote_item.lote_numero
                lote_almacen.referencia = "Compra"
                lote_almacen.fecha_caducidad = lote_item.fecha_caducidad
                # lote_almacen.cantidad = lote_item.cantidad
                lote_almacen.save()

                control_lote = ControlProductoLote.objects.update_or_create(
                    lote=lote_almacen,
                    producto=lote_almacen.producto,
                    almacen=kardex.almacen,
                    defaults={'cantidad': lote_item.cantidad}
                )

    return True


def guardarRetencion(orden, usuario, tabla):
    total_valor_retenido = 0
    fecha_comp_modifica = ''
    # JSON to Dict
    json_data = json.loads(tabla)
    for key in json_data:
        if key["ptype"] == "RT":
            total_valor_retenido = total_valor_retenido + \
                Decimal(key["valor_retenido"])
            fecha_comp_modifica = key['fecha_comp_modifica']

    if total_valor_retenido > 0:
        date_str = fecha_comp_modifica
        format_str = '%Y-%m-%d'
        datetime_obj = datetime.datetime.strptime(date_str, format_str)

        mes = datetime_obj.strftime('%m')
        anio = datetime_obj.strftime('%Y')

        # obtener codigo de secuencia
        sri_tipo_moneda_obj = SriTipoMoneda.objects.filter(codigo='DOLAR')[0]
        # empresa_obj = usuario.perfil.empresa
        empresa_obj = orden.empresa
        tipo_comprobante_obj = SriTipoComprobante.objects.filter(codigo='07')[
            0]
        secuencia_obj = Secuencia.objects.filter(
            empresa=empresa_obj, sri_tipo_comprobante=tipo_comprobante_obj)[0]
        ultima_secuencia = secuencia_obj.ultima_secuencia
        secuencia_obj.ultima_secuencia += 1
        secuencia_obj.save()

        comprobante = ComprobanteRetencion()
        comprobante.empresa = empresa_obj
        comprobante.proveedor = orden.proveedor
        comprobante.compra = orden
        comprobante.secuencia = secuencia_obj
        comprobante.sri_tipo_comprobante = tipo_comprobante_obj
        comprobante.sri_tipo_moneda = sri_tipo_moneda_obj
        comprobante.usuario_creador = usuario
        # comprobante.created_at =
        # comprobante.update_at =
        comprobante.estado_id = '1'  # COMPROBANTE CREADO

        comprobante.fecha_emision = orden.fecha_emision
        comprobante.numero_secuencia = ultima_secuencia
        comprobante.clave_acceso = format(datetime.datetime.now())
        # comprobante.numero_autorizacion =
        # comprobante.fecha_autorizacion =
        comprobante.periodo = mes
        comprobante.anio = anio
        comprobante.valor_total = total_valor_retenido
        # comprobante.fecha_generado =
        # comprobante.archivo_generado =
        # comprobante.archivo_autorizado =
        # comprobante.fecha_error =
        # comprobante.archivo_error =
        comprobante.save()

        guardarRetencionDetalle(comprobante, tabla)

    return True


def guardarRetencionDetalle(comprobante, tabla):
    json_data = json.loads(tabla)
    for key in json_data:
        if key["ptype"] == "RT":
            sri_tipo_impuesto_obj = SriTipoImpuesto.objects.filter(
                codigo=key["cod_reten"])[0]
            sri_tipo_comprobante_modificado_obj = SriTipoComprobante.objects.filter(codigo=key[
                                                                                    "tipo_doc"])[0]

            ret_det = ComprobanteRetencionDetalle()
            ret_det.retencion = comprobante
            ret_det.sri_tipo_comprobante_modificado = sri_tipo_comprobante_modificado_obj
            ret_det.sri_tipo_impuesto = sri_tipo_impuesto_obj
            # ret_det.created_at =
            # ret_det.update_at =
            ret_det.fecha_emision_documento_modificado = key[
                "fecha_comp_modifica"]
            ret_det.numero_documento_modificado = key["documento"]
            ret_det.tipo_impuesto = key["tipo_imp"]
            ret_det.valor_base_imponible = key["base_imponible"]
            ret_det.valor_total = key["valor_retenido"]
            ret_det.save()

    return True


class GeneratePDF(View):

    def get(self, request, *args, **kwargs):
        factura_id = request.GET.get('data', None)
        if factura_id is None:
            factura_id = kwargs.get("pk")

        # current_user = request.user
        company_id = request.session['company_id']
        empresa_obj = Empresa.objects.get(pk=company_id)
        factura_obj = OrdenCompra.objects.get(pk=factura_id)
        items = OrdenCompraDetalle.objects.filter(compra_id=factura_id)
        params = {
            # 'orden_id': factura_id,
            # 'cliente_nombre': factura_obj.cliente.nombre,
            # 'cliente_direccion': factura_obj.cliente.direccion,
            # 'cliente_telefono': factura_obj.cliente.telefono,
            'tipo_comprobante': "FACTURA COMPRA",
            'empresa': empresa_obj,
            'factura': factura_obj,
            'items': items,
        }

        # html = template.render(context)
        pdf = render_to_pdf('pdf/factura_compra.html', params)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "factura_compra_%s.pdf" % (factura_id)
            content = "inline; filename=%s" % (filename)
            download = request.GET.get("download")
            if download:
                content = "attachment; filename=%s" % (filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Error Rendering PDF", status=400)


"""class CuentasPagarIndexView(ListView):
    template_name = 'compra/cuentas_por_pagar.html'

    def get_queryset(self):
        return PagoCredito.objects.none()"""


class CuentasPagarIndexView(ListView):
    template_name = 'compra/cuentas_por_pagar.html'

    # def get_queryset(self):
    #    return PagoCredito.objects.all()

    def get_queryset(self):
        # query=08/27/2019 - 08/27/2019
        query = self.request.GET.get("daterange")
        current_company_id = self.request.session['company_id']

        if query:
            from_date = query[0:10]  # 08/27/2019
            to_date = query[13:23]  # 08/27/2019

            start_date = datetime.datetime.strptime(
                from_date, "%d/%m/%Y").date()
            end_date = datetime.datetime.strptime(to_date, "%d/%m/%Y").date()

            object_list = PagoCredito.objects.filter(
                pago__tipo_flujo='H',
                saldo__gt=0,
                estado__lt=3,
                vence__range=(
                    start_date, end_date), empresa_id=current_company_id).order_by('vence')
        else:
            # not query and not range
            # object_list = self.model.objects.none()
            '''index_end_date = datetime.date.today()
            index_start_date = datetime.date.today() - timedelta(29)
            object_list = PagoCredito.objects.all()
            object_list = object_list.filter(
                pago__tipo_flujo='H',
                saldo__gt=0,
                estado__lt=3,
                vence__range=(
                    index_start_date, index_end_date), empresa_id=current_company_id).order_by('vence')'''
            object_list = PagoCredito.objects.filter(
                pago__tipo_flujo='H', saldo__gt=0, estado__lt=3).order_by('vence')

        return object_list


'''
class CuentasPagarIndexView(ListView):
    template_name = 'compra/cuentas_por_pagar.html'
    context_object_name = 'page'

    def get_queryset(self):
        queryset_list = PagoCredito.objects.filter(pago__tipo_flujo='H', saldo__gt=0).only(
            'pago', 'vence', 'valor_cuota', 'valor_retenido', 'abono', 'saldo', 'estado').order_by('vence')
        query = self.request.GET.get("q", '')
        paginate_by = self.request.GET.get('rpp', 10)

        if query:
            queryset_list = queryset_list.filter(
                    Q(estado__lt=3) &
                    Q(pago__compra__proveedor__nombre__icontains=query) |
                    Q(pago__compra__proveedor__identificacion__icontains=query)
                    ).distinct().order_by('vence')

        page = int(self.request.GET.get('page', 1))
        paginate_by = int(paginate_by)
        paginator = Paginator(queryset_list, paginate_by, request=self.request)

        try:
            queryset_list = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            queryset_list = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 999), deliver last page of results.
            queryset_list = paginator.page(paginator.num_pages)

        return queryset_list
'''


def abonar_credito_modal(request, id_pagocredito):
    if request.method == 'POST':
        # guardar abono...
        print("abonando id=%s" % id_pagocredito)
        # form = CrearTurnoForm(request.POST)
        # if form.is_valid:

        data = request.POST.copy()
        # print("DATA...")
        # print(data)

        pPayTable = data.get('the_post', default=None)

        monto_pagado = 0
        # JSON to Dict
        json_data = json.loads(pPayTable)
        for key in json_data:
            monto_pagado += float(key["monto"])

        if monto_pagado > 0:
            current_user = request.user
            credito = PagoCredito.objects.get(pk=id_pagocredito)

            orden_id = credito.pago.orden_id
            orden_compra_obj = OrdenCompra.objects.get(pk=orden_id)

            payment = Payment(current_user, tipo_flujo="HABER",
                              referencia="Cuentas por pagar", tabla=pPayTable, orden=orden_compra_obj)
            payment.procesar()

            abono_anterior = round(credito.abono, 2)
            saldo_anterior = round(credito.saldo, 2)

            abono = round(Decimal(monto_pagado), 2)
            nuevo_saldo = saldo_anterior - abono
            nuevo_abono = abono_anterior + abono
            credito.abono = nuevo_abono
            credito.saldo = nuevo_saldo

            if nuevo_saldo <= 0:
                credito.estado_id = 3  # Saldado
            credito.save()

        # return redirect('compra:cuentas_pagar')
        response_data = {}
        response_data['result'] = 'Create payment successful!'
        now = datetime.datetime.now()
        response_data['created'] = now.strftime('%B %d, %Y %I:%M %p')
        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )

    queryset_list = EntidadFinanciera.objects.all().order_by('nombre')
    queryset_tarjetas = TarjetaBancaria.objects.all().order_by('nombre')

    credito_obj = PagoCredito.objects.get(pk=id_pagocredito)
    saldo = credito_obj.saldo
    return render(request, 'compra/abonar_credito_form.html',
                  {
                      'id_pagocredito': id_pagocredito,
                      'saldo': saldo,
                      'bancos': queryset_list,
                      'tarjetas': queryset_tarjetas
                  })


def abono_efectivo(request, id_pagocredito):
    if request.method == 'POST':
        data = request.POST.copy()

        pPayTable = data.get('the_post', default=None)

        monto_pagado = 0
        # JSON to Dict
        json_data = json.loads(pPayTable)
        for key in json_data:
            monto_pagado += float(key["monto"])

        if monto_pagado > 0:
            current_user = request.user
            credito = PagoCredito.objects.get(pk=id_pagocredito)

            orden_id = credito.pago.orden_id
            orden_compra_obj = OrdenCompra.objects.get(pk=orden_id)

            '''pPayTable = []
            pPayTable.append({
                "ptype": "EF",
                "monto": monto_pagado
            })'''

            payment = Payment(current_user, tipo_flujo="HABER",
                              referencia="Cuentas por pagar", tabla=pPayTable, orden=orden_compra_obj)
            payment.procesar()

            abono_anterior = round(credito.abono, 2)
            saldo_anterior = round(credito.saldo, 2)

            abono = round(Decimal(monto_pagado), 2)
            nuevo_saldo = saldo_anterior - abono
            nuevo_abono = abono_anterior + abono
            credito.abono = nuevo_abono
            credito.saldo = nuevo_saldo

            if nuevo_saldo <= 0:
                credito.estado_id = 3  # Saldado
            credito.save()

        return JsonResponse({
            'success': True,
        })

    credito_obj = PagoCredito.objects.get(pk=id_pagocredito)
    saldo = credito_obj.saldo
    return render(request, 'compra/abono_efectivo.html', {
        'id_pagocredito': id_pagocredito,
        'saldo': saldo,
    })


'''def ajaxPaymentView(request):
    if request.method == 'GET':
        creditoId = request.GET.get('id', None)

        # buscar registro en Credito
        entry = PagoCredito.objects.get(pk=creditoId)
        if not entry:
            saldo = 0
        else:
            saldo = entry.saldo

        return JsonResponse({
            'success': True,
            'credito_id': creditoId,
            'grand_total': saldo
        })
    else:  # request.method == 'POST'
        data = request.POST.copy()
        credito_id = data.get('credito_id')
        monto_pagado = data.get('amount_received')
        pPayTable = data.get('pTableData', default=None)

        # Table in JSON
        """pPayTable = {
            "ptype": "EF",
            "monto": monto_pagado
        }"""
        # json_string = json.dumps([{'ptype': 'ENT_FAC', 'monto': monto_pagado}])

        current_user = request.user
        credito = PagoCredito.objects.get(pk=credito_id)

        orden_id = credito.pago.compra_id
        orden_compra_obj = OrdenCompra.objects.get(pk=orden_id)
        payment = Payment(current_user, tipo_flujo="HABER",
                          referencia="Cuentas por pagar", tabla=pPayTable, orden=orden_compra_obj)
        payment.procesar()
        # payment = Payment(current_user=current_user, tipo_flujo="HABER", referencia="Cuentas por pagar", tabla=json_string, orden=orden_compra_obj)
        # payment.procesar()

        abono_anterior = round(credito.abono, 2)
        saldo_anterior = round(credito.saldo, 2)

        abono = round(Decimal(monto_pagado), 2)
        nuevo_saldo = saldo_anterior - abono
        nuevo_abono = abono_anterior + abono
        credito.abono = nuevo_abono
        credito.saldo = nuevo_saldo

        if nuevo_saldo <= 0:
            credito.estado_id = 3  # Saldado
        credito.save()

        return JsonResponse({
            'success': True,
            'monto': monto_pagado,
            'compra': orden_id
        })'''


def export_credits_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="creditos.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Créditos')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    # ('pago', 'vence', 'valor_cuota', 'abono', 'saldo', 'estado')
    columns = ['Proveedor', 'Comprobante', 'Vence',
               '$ Total', '$ Abono', '$ Saldo', 'Situación']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    rows = Credito.objects.all().values_list(
        'valor_credito', 'plazo', 'unidad_tiempo', 'num_cuotas')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response


def upload_driver(request):
    import os
    from django.conf import settings

    upload_file = request.FILES['drive_file']
    ret = {}
    if upload_file:
        # target_folder = settings.PULL_DRIVER_UPLOAD_PATH
        target_folder = settings.MEDIA_ROOT + "/compras"
        if not os.path.exists(target_folder):
            os.mkdir(target_folder)
        # rtime = str(int(time.time()))
        filename = request.POST['filename']
        target = os.path.join(target_folder, filename)
        with open(target, 'wb+') as dest:
            for c in upload_file.chunks():
                dest.write(c)
        ret['file_remote_path'] = target
    else:
        return HttpResponse(status=500)
    return HttpResponse(json.dumps(ret), content_type="application/json")


def get_comprobante_xml(request):
    filename = request.GET.get('filename', None)

    # XML to JSON
    import json
    import xmltodict
    from django.conf import settings

    with open(settings.MEDIA_ROOT + "/compras/" + filename, 'r') as f:
        xmlString = f.read()

    jsonString = json.dumps(xmltodict.parse(xmlString), indent=4)

    return JsonResponse({
        'success': True,
        'jsonString': jsonString
    })


"""
Proveedor Modal
"""

"""class CrearProveedorModal(CreateView):
    template_name = 'producto/proveedor_modal.html'
    form_class = ProveedorForm
    success_url = reverse_lazy('inventario:crear_producto')

    def form_valid(self, form):
        proveedor = form.save(commit=False)
        proveedor.usuario_creador = self.request.user
        proveedor.save()
        return super(CrearProveedorModal, self).form_valid(form)
"""

""" FORMULARIO MODAL PROVEEDOR COMPRAS """


class MixinFormInvalid:

    def form_invalid(self, form):
        response = super().form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response


class CrearProveedorModal(SuccessMessageMixin, MixinFormInvalid,
                          generic.CreateView):
    model = Proveedor
    template_name = 'includes/proveedor_modal.html'
    context_object_name = 'obj'
    form_class = ProveedorModalForm
    success_url = reverse_lazy('compra:ingresar_compra')
    success_message = 'Success: Proveedor creado exitosamente.'

    def form_valid(self, form):
        form.instance.usuario_creador = self.request.user
        form.instance.empresa_id = self.request.session['company_id']
        return super().form_valid(form)


# turno_obj = Turno.objects.filter(usuario_creador=self.usuario, activo=True)[0]

class PagoEfectivoModal(SuccessMessageMixin, MixinFormInvalid,
                        generic.CreateView):
    model = Pago
    template_name = 'includes/pago_efectivo_modal.html'
    context_object_name = 'obj'
    form_class = PagoModalForm
    success_url = reverse_lazy('compra:ingresar_compra')
    success_message = 'Success: Pago creado exitosamente.'

    def form_valid(self, form):
        from apps.contabilidad.models import FormaPago, EstadoPago
        from apps.sri.models import SriFormaPago, SriTipoMoneda

        turno_obj = Turno.objects.filter(
            usuario_creador=self.request.user, activo=True)[0]

        app_forma_pago_obj = FormaPago.objects.filter(codigo='EF')[0]
        sri_forma_pago_obj = SriFormaPago.objects.filter(
            codigo=app_forma_pago_obj.sri_codigo)[0]
        sri_tipo_moneda_obj = SriTipoMoneda.objects.filter(codigo='DOLAR')[0]
        estado_pago_obj = EstadoPago.objects.filter(situacion='Confirmado')[0]

        form.instance.turno = turno_obj
        form.instance.usuario = self.request.user
        form.instance.empresa_id = self.request.session['company_id']

        form.instance.app_forma_pago = app_forma_pago_obj
        form.instance.sri_forma_pago = sri_forma_pago_obj
        form.instance.sri_tipo_moneda = sri_tipo_moneda_obj
        form.instance.estado = estado_pago_obj
        form.instance.tipo_flujo = 'H'
        # form.instance.orden = 0
        # form.instance.numero_comprobante = form.cleaned_data['']
        # form.instance.proveedor =
        # form.instance.importe = form.cleaned_data[]
        # form.instance.valor_retenido = 0
        form.instance.referencia = 'Compra'
        return super().form_valid(form)

        # payment = Payment(current_user, tipo_flujo="HABER",
        #                  referencia="Compra", tabla=pPayTable, orden=orden)


def pago_efectivoV1(request):
    if request.method == 'POST':

        post_num_comprobante = request.POST.get('num_comprobante')
        post_proveedor_id = request.POST.get('proveedor_id')
        post_importe = request.POST.get('importe_factura')
        post_importe_recibido = request.POST.get('importe_recibido')

        response_data = {}

        from apps.contabilidad.models import FormaPago, EstadoPago
        from apps.sri.models import SriFormaPago, SriTipoMoneda

        turno_obj = Turno.objects.filter(
            usuario_creador=request.user, activo=True)[0]
        app_forma_pago_obj = FormaPago.objects.filter(codigo='EF')[0]
        sri_forma_pago_obj = SriFormaPago.objects.filter(
            codigo=app_forma_pago_obj.sri_codigo)[0]
        sri_tipo_moneda_obj = SriTipoMoneda.objects.filter(codigo='DOLAR')[0]
        estado_pago_obj = EstadoPago.objects.filter(situacion='Confirmado')[0]

        pago = Pago()
        pago.turno = turno_obj
        pago.usuario = request.user
        pago.empresa_id = request.session['company_id']
        pago.app_forma_pago = app_forma_pago_obj
        pago.sri_forma_pago = sri_forma_pago_obj
        pago.sri_tipo_moneda = sri_tipo_moneda_obj
        pago.estado = estado_pago_obj
        pago.tipo_flujo = 'H'
        # pago.orden = 0
        pago.numero_comprobante = post_num_comprobante
        pago.proveedor_id = post_proveedor_id
        pago.importe_recibido = post_importe_recibido
        pago.importe = post_importe
        # pago.valor_retenido = 0
        pago.referencia = 'Compra'
        pago.save()

        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )

    else:
        return HttpResponse(
            json.dumps({"nothing to see": "this isn't happening"}),
            content_type="application/json"
        )


# pago efectivo
def cash_paymentV1(request, param1, param2, param3):
    """
    :param request:
    :param param1: proveedor_id
    :param param2: nro_fact
    :param param3: importe_fact
    :return:
    """

    context = {}
    context['proveedor_id'] = param1
    context['num_fact'] = param2
    context['importe_fact'] = param3

    return render(request, 'includes/cash_payment_modal.html', context=context)


def cash_payment(request):
    if request.method == "POST" and request.is_ajax:
        post_importe_fact = request.POST.get('importe_fact', None)
        post_importe_recibido = request.POST.get('importe_recibido', None)

        return HttpResponse(
            json.dumps({"success": True}),
            content_type="application/json"
        )

# ajax_posting function


def ajax_purchase_payment(request):
    if request.method == "POST" and request.is_ajax:
        post_num_fact = request.POST.get('num_fact', None)
        post_proveedor_id = request.POST.get('proveed_id', None)
        post_importe = request.POST.get('grand_total', 0)
        post_importe_recibido = request.POST.get('importe_recibido', 0)
        post_payment_terms = request.POST.get('terminos', None)

        bco_origen_id = request.POST.get('dlgtransfer_bank_name', 0)
        cta_origen = request.POST.get('dlgtransfer_origin_account', None)
        bco_destino_id = request.POST.get(
            'dlgtransfer_destination_bank_name', None)
        cta_destino = request.POST.get('dlgtransfer_destination_account', None)
        # nro_transf = request.POST.get('dlgtransfer_comprobante', None)
        fecha_transf = request.POST.get('dlgtransfer_fecha', None)
        # formato recibido 02/01/2022
        fecha_transf_obj = datetime.datetime.strptime(
                fecha_transf, "%d/%m/%Y").date()

        monto_local = request.POST.get('dlgtransfer_amount', 0)
        monto_transf = locale.atof(monto_local)

        # cheking if post_num_fact and post_proveedor_id have value
        if post_num_fact and post_proveedor_id and post_importe \
                and post_importe_recibido and post_payment_terms:
            turno_obj = Turno.objects.filter(
                usuario_creador=request.user, activo=True)[0]

            app_forma_pago_obj = FormaPago.objects.filter(
                codigo=post_payment_terms)[0]

            sri_forma_pago_obj = SriFormaPago.objects.filter(
                codigo=app_forma_pago_obj.sri_codigo)[0]
            sri_tipo_moneda_obj = SriTipoMoneda.objects.filter(codigo='DOLAR')[0]
            estado_pago_obj = EstadoPago.objects.filter(
                situacion='Confirmado')[0]

            pago = Pago()
            pago.turno = turno_obj
            pago.usuario = request.user
            pago.empresa_id = request.session['company_id']
            pago.app_forma_pago = app_forma_pago_obj
            pago.sri_forma_pago = sri_forma_pago_obj
            pago.sri_tipo_moneda = sri_tipo_moneda_obj
            pago.estado = estado_pago_obj
            pago.tipo_flujo = 'H'
            # pago.orden = 0
            pago.numero_comprobante = post_num_fact
            pago.proveedor_id = post_proveedor_id
            pago.importe_recibido = post_importe_recibido
            pago.importe = post_importe
            # pago.valor_retenido = 0
            pago.referencia = 'Compra'
            pago.save()

            if post_payment_terms == 'TB':
                registrarTransfenciaBancaria(
                    pago, bco_origen_id, cta_origen, bco_destino_id,
                    cta_destino, fecha_transf_obj, monto_transf)
            # elif post_payment_terms == 'CH':
            #    guardarPagoCheque()
            # elif post_payment_terms == 'TD':
            # else:
            # Tarjeta Crédito

            return HttpResponse(
                json.dumps({"success": True}),
                content_type="application/json"
            )


def registrarTransfenciaBancaria(pago, bco_origen_id, cta_origen,
    bco_destino_id, cta_destino, fecha_transf_obj, monto_transf):
    bco_origen_obj = EntidadFinanciera.objects.get(pk=bco_origen_id)
    bco_destino_obj = EntidadFinanciera.objects.get(pk=bco_destino_id)

    transf = PagoTransferencia()
    transf.pago = pago
    transf.banco_origen = bco_origen_obj
    transf.cta_origen = cta_origen
    # transf.titular = key["titular"]
    transf.banco_destino = bco_destino_obj
    transf.cta_destino = cta_destino
    transf.fecha_transf = fecha_transf_obj
    transf.monto = monto_transf
    transf.save()

    return True
