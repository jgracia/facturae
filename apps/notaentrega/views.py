import json

from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView

from django.urls import reverse_lazy
from django.http import JsonResponse

import datetime
from datetime import timedelta
from pytz import timezone
from django.db.models import Sum

from .models import NotaEntrega, NotaEntregaEstado, NotaEntregaDetalle
from apps.cesta.models import Cesta, Item as CestaItem, Lote as CestaLote
from apps.usuario.models import Turno
from apps.cliente.models import Cliente
from apps.cliente.forms import ClienteForm
from apps.administracion import utils
from apps.administracion.models import EntidadFinanciera, TarjetaBancaria, \
    Secuencia


from apps.sri.models import SriTarifaIVA, SriTipoComprobante, SriTipoMoneda, \
    SriFormaPago
from apps.unidadmedida.models import UnidadMedida
from apps.producto.models import Producto
from apps.almacen.models import Kardex, ProductoSaldo, \
    Almacen, TipoMovimiento, ControlProducto, ControlProductoLote
from apps.servicio.models import Servicio
from apps.contabilidad.Payment import Payment
from apps.contabilidad.models import Pago, PagoCredito, FormaPago, EstadoPago

# librerias para PDF
from apps.administracion.render import render_to_pdf
from django.http import HttpResponse
from django.views.generic import View

from django.conf import settings
import os

# raw sql
from django.db import connection

import locale
# Set to users preferred locale:
locale.setlocale(locale.LC_ALL, '')

# Create your views here.

""" FUNCIONES CALCULO RESUMEN """

'''
def getTotalFilasCarrito(usuario_actual):
    carrito = CarritoNotaEntrega.objects.filter(usuario=usuario_actual)
    # return carrito.count()
    return len(carrito)


def getSubtotalCarrito(usuario_actual):
    total = CarritoNotaEntrega.objects.filter(usuario=usuario_actual).aggregate(
        total=Sum('valor_subtotal_sin_impuesto'))['total']
    if not total:
        return 0
    return total


def getSubtotalImptoCarrito(usuario_actual):
    total = CarritoNotaEntrega.objects.filter(usuario=usuario_actual).aggregate(
        total=Sum('valor_subtotal_12'))['total']
    if not total:
        return 0
    return total


def getSubtotalZeroCarrito(usuario_actual):
    total = CarritoNotaEntrega.objects.filter(usuario=usuario_actual).aggregate(
        total=Sum('valor_subtotal_0'))['total']
    if not total:
        return 0
    return total


def getDescuentoZeroCarrito(usuario_actual):
    # Less than or equal:
    # User.objects.filter(userprofile__level__lte=0)

    # Greater than or equal
    # User.objects.filter(userprofile__level__gte=0)

    descuento = CarritoNotaEntrega.objects.filter(usuario=usuario_actual, valor_subtotal_0__level__gte=0).aggregate(
        descuento=Sum('valor_descuento'))['descuento']
    if not descuento:
        return 0
    return descuento


def getDescuentoImptoCarrito(usuario_actual):
    descuento = CarritoNotaEntrega.objects.filter(usuario=usuario_actual, valor_subtotal_12__level__gte=0).aggregate(
        descuento=Sum('valor_descuento'))['descuento']
    if not descuento:
        return 0
    return descuento


def getValorDescuentoCarrito(usuario_actual):
    total = CarritoNotaEntrega.objects.filter(usuario=usuario_actual).aggregate(
        descuento=Sum('valor_descuento'))['descuento']
    if not total:
        return 0
    return total


def getValorIvaCarrito(usuario_actual):
    total = CarritoNotaEntrega.objects.filter(
        usuario=usuario_actual).aggregate(total=Sum('valor_iva'))['total']
    if not total:
        return 0
    return total


def getValorTotalCarrito(usuario_actual):
    total = CarritoNotaEntrega.objects.filter(
        usuario=usuario_actual).aggregate(total=Sum('valor_total'))['total']
    if not total:
        return 0
    return total
'''

""" FUNCIONES CALCULO INVENTARIO """


'''def getExistencia(producto_obj):
    saldo_obj = ProductoSaldo.objects.filter(producto=producto_obj)
    if saldo_obj.exists():
        return saldo_obj[0].existencia
    else:
        return 0'''


""" FUNCIONES NOTAS ENTREGA """


class ListadoNotasEntrega(ListView):
    template_name = 'notaentrega/listado_notasentrega.html'

    def get_queryset(self):
        return NotaEntrega.objects.none()


def ajax_listado_notasentrega(request):
    from_date = request.POST.get("startDate")
    to_date = request.POST.get("endDate")
    format_str = '%Y-%m-%d'
    start_date = datetime.datetime.strptime(from_date, format_str)
    end_date = datetime.datetime.strptime(to_date, format_str)

    try:
        query = """
            select nota_entrega_id, fecha_emision, c.nombre as cliente, administracion_secuencia.punto_establecimiento || '-' || administracion_secuencia.punto_emision || '-' || LPAD(numero_secuencia::text, 9, '0') as numero_comprobante, nes.situacion as estado, valor_total
            from notaentrega_notaentrega ne
            inner join cliente_cliente c on ne.cliente_id = c.cliente_id
            inner join notaentrega_notaentregaestado nes on nes.id = ne.estado_id
            inner join administracion_secuencia on administracion_secuencia.secuencia_id = ne.secuencia_id
            where date(fecha_emision) >= '%s' and date(fecha_emision) <= '%s'
            order by fecha_emision desc
        """ % (start_date, end_date)
    except ValueError:
        # ningún almacén seleccionado
        id_aux = 0
        query = """
            select nota_entrega_id, fecha_emision, c.nombre as cliente, administracion_secuencia.punto_establecimiento || '-' || administracion_secuencia.punto_emision || '-' || LPAD(numero_secuencia::text, 9, '0') as numero_comprobante, nes.situacion as estado, valor_total
            from notaentrega_notaentrega ne
            inner join cliente_cliente c on ne.cliente_id = c.cliente_id
            inner join notaentrega_notaentregaestado nes on nes.id = ne.estado_id
            inner join administracion_secuencia on administracion_secuencia.secuencia_id = ne.secuencia_id
            where venta_factura.factura_id = %s
        """ % (id_aux)

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        results = []
        columns = (
            'factura_id', 'fecha_emision', 'cliente', 'numero_comprobante', 'estado', 'valor_total'
        )
        for row in rows:
            results.append(dict(zip(columns, row)))
    return JsonResponse(results, safe=False)


class CrearNotaEntrega(ListView):
    context_object_name = 'notaentrega'
    template_name = 'notaentrega/notaentrega.html'
    success_url = reverse_lazy('notaentrega:listado_notasentrega')

    def get_queryset(self):
        return NotaEntrega.objects.none()

    # def multiply(value, arg):
    #    return value*arg

    def get(self, *args, **kwargs):
        turno_obj = Turno.objects.filter(
            usuario_creador=self.request.user, activo=True)
        if turno_obj.exists():
            return super(CrearNotaEntrega, self).get(*args, **kwargs)
        else:
            return redirect('contabilidad:mensaje_vista')

    def get_context_data(self, **kwargs):
        context = super(CrearNotaEntrega, self).get_context_data(**kwargs)
        context['tarifa'] = round(
            SriTarifaIVA.objects.filter(codigo='2')[0].porcentaje)

        today = datetime.date.today()
        context['fecha_emision'] = format(today, '%Y-%m-%d')
        context['fecha_expira'] = format(today + timedelta(days=8), '%Y-%m-%d')

        unidad_obj = UnidadMedida.objects.all()
        context['unidades'] = unidad_obj

        #sri_forma_pago_obj = SriFormaPago.objects.order_by('codigo')
        #context['formas_pagos'] = sri_forma_pago_obj
        #formas_pago_obj = FormaPago.objects.all()
        #context['formas_pagos'] = formas_pago_obj

        banco_obj = EntidadFinanciera.objects.all()
        context['bancos'] = banco_obj

        tarjeta_obj = TarjetaBancaria.objects.all()
        context['tarjetas'] = tarjeta_obj

        # calculo resumen
        '''current_user = self.request.user
        subtotal = getSubtotalCarrito(current_user)
        valor_descuento = getValorDescuentoCarrito(current_user)
        valor_base_imponible = getSubtotalImptoCarrito(current_user)
        valor_tarifa_cero = getSubtotalZeroCarrito(current_user)
        valor_iva = getValorIvaCarrito(current_user)
        valor_total = getValorTotalCarrito(current_user)

        context['subtotal'] = subtotal
        context['descuento'] = valor_descuento
        context['tarifa_base'] = valor_base_imponible
        context['tarifa_cero'] = valor_tarifa_cero
        context['impuesto'] = valor_iva
        context['total'] = valor_total'''

        return context


def ajaxAgregarItem(request):
    dataId = request.GET.get('dataId', None)

    empresa_id = request.session['company_id']
    user_basket, status = Cesta.objects.get_or_create(
        usuario=request.user, clave_apli='CART-NOTAENTREGA', empresa_id=empresa_id)

    # verifica items por factura
    filasEnCarrito = user_basket.obtener_total_filas()

    company_id = request.session['company_id']
    secuencia_obj = Secuencia.objects.filter(
        empresa_id=company_id, sri_tipo_comprobante__codigo='101')[0]
    if not secuencia_obj:
        return JsonResponse({
            'success': False,
            'message': "Secuencia incorrecta.",
        })
    filasPorNotaEntrega = secuencia_obj.comprobante_total_filas

    if (filasEnCarrito < filasPorNotaEntrega):
        # verifica codigo (bien o servicio)
        cadena_buscada = 'SRV-'
        # Si la sub-cadena no está presente el programa imprimirá el valor -1
        posicion_coincidencia = dataId.find(cadena_buscada)

        if (posicion_coincidencia == -1):
            # agregar productos
            productoId = dataId
            producto_obj = Producto.objects.get(pk=productoId)
            #existencia = getExistencia(producto_obj)

            # new code
            almacen_obj = Almacen.objects.filter(
                es_principal=True, empresa_id=company_id)[0]
            control_producto = ControlProducto.objects.filter(
                producto=producto_obj, almacen=almacen_obj)
            existencia = 0
            if control_producto.exists():
                existencia = control_producto[0].stock

            if (existencia > 0):

                cantidad = 1
                if producto_obj.precio_principal == 1:
                    precio = producto_obj.precio_uno
                    porcentaje_descuento = producto_obj.descuento_uno
                elif producto_obj.precio_principal == 2:
                    precio = producto_obj.precio_dos
                    porcentaje_descuento = producto_obj.descuento_dos
                elif producto_obj.precio_principal == 3:
                    precio = producto_obj.precio_tres
                    porcentaje_descuento = producto_obj.descuento_tres
                else:
                    precio = producto_obj.precio_cuatro
                    porcentaje_descuento = producto_obj.descuento_cuatro

                # calculos item
                subtotal_linea = float(cantidad * precio)
                valor_descuento_linea = round(
                    (subtotal_linea * float(porcentaje_descuento)) / 100, 5)

                if producto_obj.iva.codigo == '2':
                    subtotal_12 = subtotal_linea - valor_descuento_linea
                    subtotal_0 = 0
                    porcentaje_iva = float(producto_obj.iva.porcentaje)
                    valor_iva = round((subtotal_12 * porcentaje_iva) / 100, 5)
                    valor_total = subtotal_12 + valor_iva
                else:
                    subtotal_12 = 0
                    subtotal_0 = subtotal_linea - valor_descuento_linea
                    valor_iva = 0
                    valor_total = subtotal_0

                cesta_item = CestaItem()
                cesta_item.tipo = 'PROD'
                cesta_item.producto = producto_obj
                cesta_item.cantidad = cantidad
                cesta_item.unidad_medida = producto_obj.unidad_principal
                cesta_item.precio = precio
                cesta_item.porcentaje_descuento = porcentaje_descuento
                cesta_item.valor_descuento = valor_descuento_linea
                cesta_item.valor_subtotal_sin_impuesto = subtotal_linea
                cesta_item.valor_subtotal_12 = subtotal_12
                cesta_item.valor_subtotal_0 = subtotal_0
                cesta_item.valor_iva = valor_iva
                cesta_item.valor_total = valor_total
                cesta_item.save()
                user_basket.items.add(cesta_item)

                if producto_obj.tiene_vencimiento or producto_obj.tiene_serie:
                    # Post.objects.create(author=me, title='Sample title', text='Test')
                    markup = "<tr>" \
                        "<td style='display:none;'>" + str(cesta_item.pk) + "</td>" \
                        "<td data-title='Descripción'><a href=/inventario/detalle_producto/" + str(productoId) + " target='_blank'>" + producto_obj.nombre + "</a></td>" \
                        "<td data-title='Cantidad' class='numeric'>" + str(locale.format('%.2f', cantidad)) + "</td>" \
                        "<td data-title='Und' class='text-center'>" + producto_obj.unidad_principal.abreviatura + "</td>" \
                        "<td data-title='Precio' class='numeric'>" + str(locale.currency(precio)) + "</td>" \
                        "<td data-title='Total' class='numeric'>" + str(locale.currency(cantidad * precio)) + "</td>" \
                        "<td data-title='Acciones' class='text-center'>" \
                        "<div class='btn-group btn-group-sm'>" \
                        "<button type='button' data-id=" + str(cesta_item.pk) + " class='btn btn-primary fas fa-edit editButton'></button>" \
                        "</div>" \
                        "&nbsp;" \
                        "<div class='btn-group btn-group-sm'>" \
                        "<button type='button' data-id=" + str(cesta_item.pk) + " class='btn btn-info fas fa-search searchButton'></button>" \
                        "</div>" \
                        "&nbsp;" \
                        "<div class='btn-group btn-group-sm'>" \
                        "<button type='button' data-id=" + str(cesta_item.pk) + " class='btn btn-warning fas fa-trash deleteButton'></button>" \
                        "</div>" \
                        "</td>" \
                        "</tr>"

                    # agregar lote
                    loteAgregar(cesta_item)
                else:
                    markup = "<tr>" \
                        "<td style='display:none;'>" + str(cesta_item.pk) + "</td>" \
                        "<td data-title='Descripción'><a href=/inventario/detalle_producto/" + str(productoId) + " target='_blank'>" + producto_obj.nombre + "</a></td>" \
                        "<td data-title='Cantidad' class='numeric'>" + str(locale.format('%.2f', cantidad)) + "</td>" \
                        "<td data-title='Und' class='text-center'>" + producto_obj.unidad_principal.abreviatura + "</td>" \
                        "<td data-title='Precio' class='numeric'>" + str(locale.currency(precio)) + "</td>" \
                        "<td data-title='Total' class='numeric'>" + str(locale.currency(cantidad * precio)) + "</td>" \
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
                return JsonResponse({
                    'success': False,
                    'message': "Existencia en cero.",
                    'totalFilas': 0,
                    'stock': 0,
                    'dataId': productoId,
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
                "<button type='button' class='btn btn-default searchButton' disabled><i class='fas fa-search'></i></button>" \
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

    else:
        return JsonResponse({
            'success': False,
            'message': "Ha superado el número de líneas por factura.",
            'totalFilas': 0,
        })


def loteAgregar(cesta_item):
    control_lote = ControlProductoLote.objects.filter(
        producto=cesta_item.producto)
    if control_lote:
        cantidad_venta = cesta_item.cantidad
        for lote_almacen in control_lote:
            if lote_almacen.cantidad >= cantidad_venta:
                cesta_lote = CestaLote()
                cesta_lote.lote_numero = lote_almacen.lote.lote_numero
                cesta_lote.fecha_caducidad = lote_almacen.lote.fecha_caducidad
                cesta_lote.cantidad = cesta_item.cantidad
                cesta_lote.item_id = cesta_item.pk
                cesta_lote.save()
                break
            else:
                cesta_lote = CestaLote()
                cesta_lote.lote_numero = lote_almacen.lote.lote_numero
                cesta_lote.fecha_caducidad = lote_almacen.lote.fecha_caducidad
                cesta_lote.cantidad = cesta_item.cantidad
                cesta_lote.item_id = cesta_item.pk
                cesta_lote.save()

                cantidad_venta -= lote_almacen.cantidad

    return True


def ajaxAgregarItemSinExistencia(request):
    productoId = request.GET.get('dataId', None)

    # verifica items por factura
    current_user = request.user
    filasEnCarrito = getTotalFilasCarrito(current_user)
    #filasPorFactura = current_user.perfil.empresa.factura_total_filas
    company_id = request.session['company_id']
    secuencia_obj = Secuencia.objects.filter(
        empresa_id=company_id, sri_tipo_comprobante__codigo='101')[0]
    if not secuencia_obj:
        return JsonResponse({
            'success': False,
            'message': "Secuencia incorrecta.",
        })
    filasPorNotaEntrega = secuencia_obj.comprobante_total_filas

    if (filasEnCarrito < filasPorNotaEntrega):
        producto_obj = Producto.objects.get(pk=productoId)
        cantidad = 1
        precio = producto_obj.precio_venta
        porcentaje_descuento = producto_obj.descuento

        # calculos item
        subtotal_linea = float(cantidad * precio)
        valor_descuento_linea = round(
            (subtotal_linea * float(porcentaje_descuento)) / 100, 5)

        if producto_obj.iva.codigo == '2':
            subtotal_12 = subtotal_linea - valor_descuento_linea
            subtotal_0 = 0
            porcentaje_iva = float(producto_obj.iva.porcentaje)
            valor_iva = round((subtotal_12 * porcentaje_iva) / 100, 5)
            valor_total = subtotal_12 + valor_iva
        else:
            subtotal_12 = 0
            subtotal_0 = subtotal_linea - valor_descuento_linea
            valor_iva = 0
            valor_total = subtotal_0

        # new code
        almacen_obj = Almacen.objects.filter(es_principal=True)[0]
        control_producto = ControlProducto.objects.filter(
            producto=producto_obj, almacen=almacen_obj)
        if control_producto.exists():
            precio_costo = control_producto[0].precio
        else:
            precio_costo = producto_obj.precio_costo

        #Post.objects.create(author=me, title='Sample title', text='Test')
        cart = CarritoNotaEntrega()
        cart.usuario = current_user
        cart.tipo = 1
        cart.producto = producto_obj
        # cart.servicio =
        cart.cantidad = cantidad
        cart.unidad = producto_obj.unidad
        cart.precio_costo = precio_costo
        cart.precio = precio
        cart.porcentaje_descuento = porcentaje_descuento
        cart.valor_descuento = valor_descuento_linea
        cart.valor_subtotal_sin_impuesto = subtotal_linea
        cart.valor_subtotal_12 = subtotal_12
        cart.valor_subtotal_0 = subtotal_0
        cart.valor_subtotal_no_objeto_iva = 0
        cart.valor_subtotal_exento = 0
        cart.valor_base_imponible_ibrpnr = 0
        cart.valor_subtotal_ibrpnr = 0
        cart.valor_ice = 0
        cart.valor_iva = valor_iva
        cart.valor_total = valor_total
        cart.save()

        carritoId = cart.pk

        markup = "<tr>" \
            "<td style='display:none;'>" + str(carritoId) + "</td>" \
            "<td data-title='Descripción'><a href=/inventario/detalle_producto/" + str(productoId) + " target='_blank'>" + producto_obj.nombre + "</a></td>" \
            "<td data-title='Cantidad' class='numeric'>" + str(round(cantidad, 2)) + "</td>" \
            "<td data-title='Und' class='text-center'>" + producto_obj.unidad.abreviatura + "</td>" \
            "<td data-title='Precio' class='numeric'>" + str(round(precio, 2)) + "</td>" \
            "<td data-title='Total' class='numeric'>" + str(round(subtotal_linea, 2)) + "</td>" \
            "<td data-title='Acciones' class='text-center'>" \
            "<div class='btn-group btn-group-sm'>" \
            "<button type='button' data-id=" + str(carritoId) + " class='btn btn-default fas fa-edit editButton'></button>" \
            "</div>" \
            "&nbsp;" \
            "<div class='btn-group btn-group-sm'>" \
            "<button type='button' data-id=" + str(carritoId) + " class='btn btn-default fas fa-trash deleteButton'></button>" \
            "</div>" \
            "</td>" \
            "</tr>"

        # calculo resumen
        filasEnCarrito = getTotalFilasCarrito(current_user)
        # if filasEnCarrito > 0:
        subtotal = getSubtotalCarrito(current_user)
        valor_descuento = getValorDescuentoCarrito(current_user)
        valor_base_imponible = getSubtotalImptoCarrito(current_user)
        valor_tarifa_cero = getSubtotalZeroCarrito(current_user)
        valor_iva = getValorIvaCarrito(current_user)
        valor_total = getValorTotalCarrito(current_user)
        # else:
        #    subtotal = 0
        #    valor_descuento = 0
        #    valor_base_imponible = 0
        #    valor_tarifa_cero = 0
        #    valor_iva = 0
        #    valor_total = 0

        return JsonResponse({
            'success': True,
            'markup': markup,
            'totalFilas': filasEnCarrito,
            'subtotal': subtotal,
            'descuento': valor_descuento,
            'tarifa_base': valor_base_imponible,
            'tarifa_cero': valor_tarifa_cero,
            'impuesto': valor_iva,
            'total': valor_total
        })

    else:
        return JsonResponse({
            'success': False,
            'message': "Ha superado el número de líneas por factura.",
            'totalFilas': 0,
        })


'''
def ajaxGetTotalFilasCarrito(request):
    if request.method == "GET":
        if request.is_ajax():
            current_user = request.user

            return JsonResponse({
                'success': True,
                'total_filas': getTotalFilasCarrito(current_user),
            })
'''


def ajaxEditarItem(request):
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
                'unit_secondary': None,
                'unit_equivalence': 1,
                'price': round(cesta_item.precio, 2),
                'discount': round(cesta_item.porcentaje_descuento, 2)
            })

    else:  # request.method == 'POST'
        data = request.POST.copy()
        itemID = data.get('id')
        cantidad = float(data.get('qty'))
        unidad = data.get('unit')
        precio = float(data.get('price'))
        porcentaje_descuento = float(data.get('discount'))

        empresa_id = request.session['company_id']
        user_basket = Cesta.objects.filter(
            usuario=request.user, clave_apli='CART-NOTAENTREGA', empresa_id=empresa_id)[0]

        cadena_buscada = 'SRV-'
        posicion_coincidencia = itemID.find(cadena_buscada)
        if (posicion_coincidencia == -1):
            # PRODUCTO
            unit_obj = UnidadMedida.objects.filter(abreviatura=unidad)[0]
            cesta_item = CestaItem.objects.get(pk=itemID)

            # verifica stock disponible
            almacen_obj = Almacen.objects.filter(es_principal=True)[0]
            producto_obj = cesta_item.producto
            control_producto = ControlProducto.objects.filter(
                producto=producto_obj, almacen=almacen_obj)
            existencia = 0
            if control_producto.exists():
                existencia = control_producto[0].stock

            if (existencia > 0) and (float(cantidad) <= existencia):

                # calculos linea
                subtotal_linea = float(cantidad) * float(precio)
                valor_descuento_linea = round(
                    (subtotal_linea * float(porcentaje_descuento)) / 100, 5)

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

                # actualizar carrito
                cesta_item.cantidad = cantidad
                cesta_item.unidad_medida = unit_obj
                ###cesta_item.precio_costo = precio_costo
                cesta_item.precio = precio
                cesta_item.porcentaje_descuento = porcentaje_descuento
                cesta_item.valor_descuento = valor_descuento_linea
                cesta_item.valor_subtotal_sin_impuesto = subtotal_linea
                cesta_item.valor_subtotal_12 = subtotal_12
                cesta_item.valor_subtotal_0 = subtotal_0
                cesta_item.valor_iva = valor_iva
                cesta_item.valor_total = valor_total
                cesta_item.save()

                # calculo resumen
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
            else:
                return JsonResponse({
                    'success': False,
                    'stock': existencia,
                    'exchange_cart_id': itemID,
                    'exchange_qty': cantidad,
                    'exchange_unit': unidad,
                    'exchange_price': precio,
                    'exchange_discount_percent': porcentaje_descuento
                })
        else:
            # SERVICIO
            unidad = data.get('unit_service')
            item_id = itemID[4:]  # subtrae Id, itemID = 'SRV-1'
            unit_service_obj = UnidadMedida.objects.filter(abreviatura=unidad)[
                0]
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

            # calculo resumen
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


def ajaxEditarItemSinExistencia(request):
    if request.method == 'POST':
        if request.is_ajax():
            itemID = request.POST.get('exchange_cart_id', None)
            cantidad = float(request.POST.get('exchange_qty', 0))
            unidad = request.POST.get('exchange_unit', None)
            precio = float(request.POST.get('exchange_price', 0))
            porcentaje_descuento = float(
                request.POST.get('exchange_discount_percent', 0))

            # buscar registro en Carrito
            unit_obj = UnidadMedida.objects.filter(abreviatura=unidad)[0]
            cesta_item = CestaItem.objects.get(pk=itemID)

            # calculos linea
            subtotal_linea = float(cantidad) * float(precio)
            valor_descuento_linea = round(
                (subtotal_linea * float(porcentaje_descuento)) / 100, 5)

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

            # actualizar carrito
            cesta_item.cantidad = cantidad
            cesta_item.unidad_medida = unit_obj
            cesta_item.precio = precio
            cesta_item.porcentaje_descuento = porcentaje_descuento
            cesta_item.valor_descuento = valor_descuento_linea
            cesta_item.valor_subtotal_sin_impuesto = subtotal_linea
            cesta_item.valor_subtotal_12 = subtotal_12
            cesta_item.valor_subtotal_0 = subtotal_0
            cesta_item.valor_iva = valor_iva
            cesta_item.valor_total = valor_total
            cesta_item.save()

            empresa_id = request.session['company_id']
            user_basket = Cesta.objects.filter(
                usuario=request.user, clave_apli='CART-NOTAENTREGA', empresa_id=empresa_id)[0]

            # calculo resumen
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

            # calculo resumen
            empresa_id = request.session['company_id']
            user_basket = Cesta.objects.filter(
                usuario=request.user, clave_apli='CART-NOTAENTREGA', empresa_id=empresa_id)[0]
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


'''
def ajaxVaciarCarrito(request):
    if request.method == "GET":
        current_user = request.user
        CarritoNotaEntrega.objects.filter(usuario=current_user).delete()

        return JsonResponse({'success': True})
'''


def guardarNotaEntrega(request):
    if request.method == 'POST':
        # recibe datos del formulario modal 'paymentForm'
        data = request.POST.copy()
        cliente_id = data.get('cliente_id', default=None)
        fecha_emision = data.get('fecha_emision', default=None)

        #fecha_vencimiento = data.get('fecha_vencimiento', default=None)

        dt_obj = datetime.datetime.now()
        hora = dt_obj.strftime("%H:%M:%S")

        datetime_obj = datetime.datetime.strptime(
            '%s %s' % (fecha_emision, hora), "%Y-%m-%d %H:%M:%S")
        datetime_obj_utc = datetime_obj.replace(tzinfo=timezone('UTC'))

        pPayTable = data.get('pTableData', default=None)

        #today = datetime.date.today()
        current_user = request.user
        #empresa_obj = current_user.perfil.empresa
        cliente_obj = Cliente.objects.get(pk=cliente_id)

        # obtener codigo de secuencia
        tipo_comprobante_obj = SriTipoComprobante.objects.filter(codigo='101')[
            0]
        company_id = request.session['company_id']
        secuencia_obj = Secuencia.objects.filter(
            empresa_id=company_id, sri_tipo_comprobante=tipo_comprobante_obj)[0]
        ultima_secuencia = secuencia_obj.ultima_secuencia
        secuencia_obj.ultima_secuencia += 1
        secuencia_obj.save()

        # if pPayTable is not None:
        '''if pPayTable is not None:
            estado_obj = NotaEntregaEstado.objects.filter(
                situacion='REGISTRADA')[0]
        else:
            estado_obj = NotaEntregaEstado.objects.filter(
                situacion='EMITIDA')[0]'''
        estado_obj = NotaEntregaEstado.objects.filter(
            situacion='REGISTRADA')[0]

        # calculo resumen
        user_basket = Cesta.objects.filter(
            usuario=request.user, clave_apli='CART-NOTAENTREGA')[0]

        subtotal = user_basket.obtener_sub_total()
        valor_descuento = user_basket.obtener_total_descuento()
        valor_base_imponible = user_basket.obtener_base_imponible()
        valor_tarifa_cero = user_basket.obtener_total_tarifa_cero()
        valor_iva = user_basket.obtener_total_iva()
        valor_total = user_basket.obtener_gran_total()

        # guardar albarán
        notaentrega = NotaEntrega()
        notaentrega.empresa_id = company_id
        notaentrega.cliente = cliente_obj
        notaentrega.usuario_creador = current_user
        notaentrega.estado = estado_obj
        notaentrega.secuencia = secuencia_obj
        notaentrega.sri_tipo_comprobante = tipo_comprobante_obj
        #currentDT = datetime.datetime.now()
        #notaentrega.fecha_emision = fecha_emision + ' ' + currentDT.strftime("%H:%M:%S")
        notaentrega.fecha_emision = datetime_obj_utc
        #notaentrega.fecha_validez = fecha_vencimiento
        notaentrega.numero_secuencia = ultima_secuencia
        notaentrega.valor_descuento = valor_descuento
        notaentrega.valor_subtotal_sin_impuesto = subtotal
        notaentrega.valor_subtotal_12 = valor_base_imponible
        notaentrega.valor_subtotal_0 = valor_tarifa_cero
        #fact.valor_subtotal_no_objeto_iva = 0
        #fact.valor_subtotal_exento = 0
        #fact.valor_base_imponible_ibrpnr = 0
        #fact.valor_subtotal_ibrpnr = 0
        notaentrega.valor_ice = 0
        notaentrega.valor_iva = valor_iva
        #fact.valor_propina = 0
        notaentrega.valor_total = valor_total
        notaentrega.save()

        guardarOrdenDetalle(notaentrega, user_basket)
        if pPayTable is not None:
            company_id = request.session['company_id']
            agregarTransKardex(notaentrega, user_basket,
                               company_id, current_user)
            payment = Payment(current_user, tipo_flujo="DEBE",
                              referencia="Nota Entrega", tabla=pPayTable, orden=notaentrega)
            payment.procesar()

        # vaciar cesta de ventas
        user_basket.vaciar_cesta()

        return JsonResponse({
            'success': True,
            'notaentregaId': notaentrega.pk,
            # 'tabla_pagos': pPayTable,
        })


def guardarOrdenDetalle(notaentrega, user_basket):
    # guardar carrito en detalle de facturas
    items = user_basket.obtener_items()

    for item in items:
        nota_det = NotaEntregaDetalle()
        nota_det.nota_entrega_id = notaentrega.pk
        if item.tipo == 'PROD':  # producto
            nota_det.tipo = 'P'
            nota_det.producto = item.producto
        else:
            nota_det.tipo = 'S'
            nota_det.servicio = item.servicio
        nota_det.cantidad = item.cantidad
        nota_det.unidad = item.unidad_medida
        nota_det.precio_venta = item.precio
        nota_det.porcentaje_descuento = item.porcentaje_descuento
        nota_det.valor_descuento = item.valor_descuento
        nota_det.valor_subtotal_sin_impuesto = item.valor_subtotal_sin_impuesto
        nota_det.valor_subtotal_12 = item.valor_subtotal_12
        nota_det.valor_subtotal_0 = item.valor_subtotal_0
        nota_det.valor_subtotal_no_objeto_iva = item.valor_subtotal_no_objeto_iva
        nota_det.valor_subtotal_exento = item.valor_subtotal_exento
        nota_det.valor_base_imponible_ibrpnr = item.valor_base_imponible_ibrpnr
        nota_det.valor_subtotal_ibrpnr = item.valor_subtotal_ibrpnr
        nota_det.valor_ice = item.valor_ice
        nota_det.valor_iva = item.valor_iva
        nota_det.valor_total = item.valor_total
        nota_det.save()

    return True


""" FUNCIÓN AGREGAR TRANSACCIÓN AL INVENTARIO """


def agregarTransKardex(buysell, cesta, company_id, usuario):
    # guardar carrito en detalle de facturas
    pto_establecimiento = buysell.secuencia.punto_establecimiento
    pto_emision = buysell.secuencia.punto_emision
    sec_formateado = buysell.get_numero_secuencia_formateado()
    numero_comprobante = "%s-%s-%s" % (pto_establecimiento,
                                       pto_emision, sec_formateado)

    almacen_obj = Almacen.objects.filter(es_principal=True)[0]
    tipo_movimiento_obj = TipoMovimiento.objects.filter(codigo='SAL_NE')[0]

    #metodo_costo = usuario.perfil.empresa.metodo_costo
    fecha_operacion_obj = buysell.fecha_emision.strftime('%Y-%m-%d')

    items = cesta.obtener_items()
    for item in items:
        if item.tipo == 'PROD':  # PRODUCTO
            kardex = Kardex()
            #kardex.tipo = 2
            kardex.movimiento = tipo_movimiento_obj
            kardex.orden_id = buysell.pk
            kardex.numero_comprobante = numero_comprobante
            kardex.referencia = "Nota Entrega"
            kardex.producto = item.producto

            # nuevo para buscar precio de costo
            control_producto = ControlProducto.objects.filter(
                producto=item.producto, almacen=almacen_obj)
            if control_producto.exists():
                precio_costo = control_producto[0].precio
            else:
                precio_costo = item.producto.precio_costo

            if item.unidad_medida == item.producto.unidad_secundaria:
                # TRANFORMAR SUBMULTIPLO Y PRECIO A UNIDAD PRINCIPAL
                kardex.unidad = item.producto.unidad

                equivalencia_unidad = item.producto.unidad_equivalencia
                fraccion = item.cantidad

                qty = (fraccion * 1) / equivalencia_unidad
                cost = precio_costo
                valor_total = qty * cost
            else:
                kardex.unidad = item.unidad_medida
                # kardex.created_at =
                # kardex.update_at =

                qty = item.cantidad
                cost = precio_costo
                valor_total = qty * cost

            kardex.cantidad = qty
            kardex.costo = cost
            kardex.total = valor_total

            metodo_costo = item.producto.metodo_costo
            if (metodo_costo == 'PROM'):
                try:
                    producto_obj = item.producto
                    kardex_ant = Kardex.objects.filter(producto=producto_obj,
                                                       almacen=almacen_obj,
                                                       created_at__date__lte=fecha_operacion_obj).latest('created_at')
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

            kardex.empresa_id = company_id
            kardex.almacen = almacen_obj
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
            control_lote_ant = ControlProductoLote.objects.filter(producto=kardex.producto,
                                                                  almacen=kardex.almacen,
                                                                  lote__lote_numero=lote_item.lote_numero)
            if control_lote_ant:
                new_stock = control_lote_ant[0].cantidad - lote_item.cantidad

                control_lote = ControlProductoLote.objects.update_or_create(
                    producto=kardex.producto,
                    almacen=kardex.almacen,
                    lote=control_lote_ant[0].lote,
                    defaults={
                        'cantidad': new_stock
                    }
                )

    return True


""" FORMULARIO MODAL CLIENTE """


class CrearClienteModal(CreateView):
    template_name = 'frontend/modals/cliente_modal.html'
    form_class = ClienteForm
    success_url = reverse_lazy('notaentrega:crear_notaentrega')

    def form_valid(self, form):
        cliente = form.save(commit=False)
        cliente.usuario_creador = self.request.user
        cliente.save()
        return super(CrearClienteModal, self).form_valid(form)


class EliminarNotaEntrega(DeleteView):
    model = NotaEntrega
    template_name = 'notaentrega/eliminar_notaentrega.html'
    success_url = reverse_lazy('notaentrega:listado_notaentrega')


class GeneratePDF(View):
    def get(self, request, *args, **kwargs):
        #template = get_template('pdf/factura.html')

        #notaentrega_id = kwargs.get("pk")

        #notaentrega_id = request.GET['data']
        notaentrega_id = request.GET.get('data', None)
        if notaentrega_id is None:
            notaentrega_id = kwargs.get("pk")

        notaentrega_obj = NotaEntrega.objects.get(pk=notaentrega_id)
        items = NotaEntregaDetalle.objects.filter(
            nota_entrega_id=notaentrega_id)

        ruta = '/media/pixmaps/%s_notaentrega.jpg' % (
            notaentrega_obj.empresa.ruc)
        url_filigrana = "{0}://{1}{2}".format(
            request.scheme, request.get_host(), ruta)

        params = {
            # 'notaentrega_id': notaentrega_id,
            # 'cliente_nombre': notaentrega_obj.cliente.nombre,
            # 'cliente_ruc': notaentrega_obj.cliente.identificacion,
            # 'cliente_direccion': notaentrega_obj.cliente.direccion,
            # 'cliente_telefono': notaentrega_obj.cliente.telefono,
            # 'fecha_emision': notaentrega_obj.fecha_emision,
            # 'notaentrega_numero': notaentrega_obj.nota_entrega_id,
            'tipo_comprobante': "NOTA DE ENTREGA",
            'notaentrega': notaentrega_obj,
            'items': items,
            # 'plantilla_url': 'media/pixmaps/%s_notaentrega.jpg' % (notaentrega_obj.empresa.ruc)
            'plantilla_url': url_filigrana
        }
        #html = template.render(context)
        pdf = render_to_pdf('pdf/notaentrega.html', params)
        destination = 'pdf/%s_notaentrega.html' % (notaentrega_obj.empresa.ruc)
        if os.path.isfile(destination):
            pdf = render_to_pdf('pdf/%s_notaentrega.html' %
                                (notaentrega_obj.empresa.ruc), params)

        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "notaentrega_%s.pdf" % (notaentrega_id)
            content = "inline; filename=%s" % (filename)
            download = request.GET.get("download")
            if download:
                content = "attachment; filename=%s" % (filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Error Rendering PDF", status=400)

    def link_callback(uri, rel):
        """
        Convert HTML URIs to absolute system paths so xhtml2pdf can access those
        resources
        """
        # use short variable names
        sUrl = settings.STATIC_URL      # Typically /static/
        sRoot = settings.STATIC_ROOT    # Typically /home/userX/project_static/
        mUrl = settings.MEDIA_URL       # Typically /static/media/
        # Typically /home/userX/project_static/media/
        mRoot = settings.MEDIA_ROOT

        # convert URIs to absolute system paths
        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri  # handle absolute uri (ie: http://some.tld/foo.png)

        # make sure that file exists
        if not os.path.isfile(path):
            raise Exception(
                'media URI must start with %s or %s' % (sUrl, mUrl)
            )
        return path


class PlantillaNotaEntrega(DetailView):
    model = NotaEntrega
    template_name = 'impresion/prueba.html'


def ajax_cash_payment(request):
    if request.method == "POST" and request.is_ajax:
        post_cliente_id = request.POST.get('cliente_id', default=0)
        post_importe = request.POST.get('grand_total', None)
        post_importe_recibido = request.POST.get('dlg_importe_recibido', None)

        if post_cliente_id == '0':
            obj = Cliente.objects.filter(identificacion='9999999999999')
            if obj.exists():
                post_cliente_id = obj[0].pk

        # cheking if post_cliente_id and post_importe have value
        if post_cliente_id and post_importe and post_importe_recibido:
            turno_obj = Turno.objects.filter(
                usuario_creador=request.user, activo=True)[0]
            app_forma_pago_obj = FormaPago.objects.filter(codigo='EF')[0]
            sri_forma_pago_obj = SriFormaPago.objects.filter(
                codigo=app_forma_pago_obj.sri_codigo)[0]
            sri_tipo_moneda_obj = SriTipoMoneda.objects.filter(codigo='DOLAR')[
                0]
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
            pago.tipo_flujo = 'D'
            ## pago.orden = 0
            # pago.numero_comprobante = post_num_fact
            pago.cliente_id = post_cliente_id
            pago.importe_recibido = post_importe_recibido
            pago.importe = post_importe
            ## pago.valor_retenido = 0
            pago.referencia = 'Nota Entrega'
            pago.save()

            return HttpResponse(
                json.dumps({"success": True}),
                content_type="application/json"
            )
