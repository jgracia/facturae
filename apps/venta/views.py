from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Sum, F, Q, Func
from django.http import JsonResponse

import os
import base64
import datetime
from decimal import Decimal

import json
from datetime import timedelta
from pytz import timezone

# librerias para xml
from xml.dom import minidom
from xml.etree.cElementTree import Element, SubElement
from xml.etree import cElementTree as ET

from .models import FacturaEstado, Factura, FacturaDetalle
from apps.cesta.models import Cesta, Item as CestaItem, Lote as CestaLote
from apps.administracion import utils
from apps.administracion.render import render_to_pdf
from apps.administracion.models import EntidadFinanciera, TarjetaBancaria, \
    Secuencia, Empresa

from apps.unidadmedida.models import UnidadMedida
from apps.producto.models import Producto
from apps.almacen.models import Almacen, Kardex, \
    TipoMovimiento, ControlProducto, ControlProductoLote
from apps.servicio.models import Servicio
from apps.sri.models import SriTarifaIVA, SriTipoComprobante, \
    SriTipoMoneda, SriFormaPago
from apps.usuario.models import Turno
from apps.cliente.models import Cliente
#from apps.cliente.forms import ClienteForm
from .forms import ClienteModalForm
from django.views import generic
from django.contrib.messages.views import SuccessMessageMixin

from apps.contabilidad.models import Pago, PagoCredito, FormaPago, EstadoPago
from apps.contabilidad.Payment import Payment

# firma electrónica
from lxml import etree
import itertools
from .facturae.elemento import ElementoXML
from .facturae.sri.firmado import Xades
from .facturae.sri.sri import DocumentXML, SriService
from .facturae.sri.ensystems import EnSystems

# librerias para gmail
from django.core.mail import EmailMultiAlternatives
# from django.conf import settings
from django.core.mail.backends.smtp import EmailBackend

# librerias para PDF
from django.views.generic import View
from django.http import HttpResponse
from django.template.loader import get_template

# modal ajax
from django.shortcuts import render
# from .forms import RegisterEditForm

# imprimir escpos
from escpos import printer
from escpos.printer import Usb

# raw sql
from django.db import connection

import locale
# Set to users preferred locale:
locale.setlocale(locale.LC_ALL, '')

# Create your views here.


class ListadoVentas(ListView):
    template_name = 'venta/listado_ventas.html'

    def get_queryset(self):
        return Factura.objects.none()


def ajax_listado_ventas(request):
    from_date = request.POST.get("startDate")
    to_date = request.POST.get("endDate")
    #format_str = '%Y-%m-%d'
    #print("FECHA ===========================>")
    # print(from_date)

    #start_date = datetime.datetime.strptime(from_date, format_str)
    #end_date = datetime.datetime.strptime(to_date, format_str)

    try:
        query = """
            select factura_id, fecha_emision, cliente_cliente.nombre as cliente, administracion_secuencia.punto_establecimiento || '-' || administracion_secuencia.punto_emision || '-' || LPAD(numero_secuencia::text, 9, '0') as numero_comprobante, venta_facturaestado.nombre as estado, valor_total
            from venta_factura
            inner join cliente_cliente on venta_factura.cliente_id = cliente_cliente.cliente_id
            inner join venta_facturaestado on venta_facturaestado.factura_estado_id = venta_factura.estado_id
            inner join administracion_secuencia on administracion_secuencia.secuencia_id = venta_factura.secuencia_id
            where date(fecha_emision) >= '%s' and date(fecha_emision) <= '%s'
            order by fecha_emision desc
        """ % (from_date, to_date)
    except ValueError:
        # ningún almacén seleccionado
        id_aux = 0
        query = """
            select factura_id, fecha_emision, cliente_cliente.nombre as cliente, administracion_secuencia.punto_establecimiento || '-' || administracion_secuencia.punto_emision || '-' || LPAD(numero_secuencia::text, 9, '0') as numero_comprobante, venta_facturaestado.nombre as estado, valor_total
            from venta_factura
            inner join cliente_cliente on venta_factura.cliente_id = cliente_cliente.cliente_id
            inner join venta_facturaestado on venta_facturaestado.factura_estado_id = venta_factura.estado_id
            inner join administracion_secuencia on administracion_secuencia.secuencia_id = venta_factura.secuencia_id
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


class CrearVenta(ListView):
    # def CrearVenta(request):
    # model = Factura
    # form_class = FacturaForm
    context_object_name = 'factura'
    # queryset = Carrito.objects.filter(usuario = self.request.user)
    template_name = 'venta/factura.html'
    success_url = reverse_lazy('venta:listado_ventas')

    # fecha_emision = forms.DateTimeField(required=True, input_formats='%Y-%m-%dT%H:%M')

    def multiply(value, arg):
        return value * arg

    def get_queryset(self):
        # return CarritoVenta.objects.filter(usuario=self.request.user).order_by('pk')
        return Factura.objects.none()

    def get(self, *args, **kwargs):
        turno_obj = Turno.objects.filter(
            usuario_creador=self.request.user, activo=True)
        if turno_obj.exists():
            return super(CrearVenta, self).get(*args, **kwargs)
        else:
            return redirect('contabilidad:mensaje_vista')

    def get_context_data(self, **kwargs):
        context = super(CrearVenta, self).get_context_data(**kwargs)
        context['tarifa'] = round(
            SriTarifaIVA.objects.filter(codigo='2')[0].porcentaje)

        today = datetime.date.today()
        context['fecha_emision'] = format(today, '%Y-%m-%d')
        context['fecha_expira'] = format(today, '%Y-%m')

        unidad_obj = UnidadMedida.objects.all()
        context['unidades'] = unidad_obj

        unidad_servicio_obj = UnidadMedida.objects.values('abreviatura')
        context['unidades_servicio'] = unidad_servicio_obj

        # sri_forma_pago_obj = SriFormaPago.objects.order_by('codigo')
        # context['formas_pagos'] = sri_forma_pago_obj
        formas_pago_obj = FormaPago.objects.all()
        context['formas_pagos'] = formas_pago_obj

        banco_obj = EntidadFinanciera.objects.all()
        context['bancos'] = banco_obj

        tarjeta_obj = TarjetaBancaria.objects.all()
        context['tarjetas'] = tarjeta_obj

        # calculo resumen
        """current_user = self.request.user
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
        context['total'] = valor_total"""

        return context


""" FUNCIONES CALCULO INVENTARIO """
# def getExistencia(producto_obj):
#    saldo_obj = ProductoResumen.objects.filter(producto_id=producto_obj.producto_id).only('existencia')
#    if saldo_obj.exists():
#        return saldo_obj[0].existencia
#    else:
#        return 0

"""def getInventarioInicial(producto_obj):
    iinicial_obj = InventarioInicial.objects.filter(producto=producto_obj)
    if iinicial_obj.exists():
        return iinicial_obj[0].cantidad
    else:
        return 0

def getInventarioComprado(producto_obj):
    icomprado_obj = InventarioComprado.objects.filter(producto=producto_obj)
    if icomprado_obj.exists():
        return icomprado_obj[0].cantidad
    else:
        return 0


def getInventarioVendido(producto_obj):
    ivendido_obj = InventarioVendido.objects.filter(producto=producto_obj)
    if ivendido_obj.exists():
        return ivendido_obj[0].cantidad
    else:
        return 0
"""

""" FORMULARIO MODAL CLIENTE """

'''
class CrearClienteModal(CreateView):
    template_name = 'frontend/cliente_modal.html'
    form_class = ClienteForm
    success_url = reverse_lazy('venta:crear_venta')

    def form_valid(self, form):
        cliente = form.save(commit=False)
        cliente.usuario_creador = self.request.user
        cliente.empresa_id = self.request.session['company_id']
        cliente.save()
        return super(CrearClienteModal, self).form_valid(form)
'''


""" FORMULARIO MODAL CLIENTE VENTAS """


class MixinFormInvalid:

    def form_invalid(self, form):
        response = super().form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response


class CrearClienteModal(SuccessMessageMixin, MixinFormInvalid,
                        generic.CreateView):
    model = Cliente
    template_name = 'includes/cliente_modal.html'
    context_object_name = 'obj'
    form_class = ClienteModalForm
    success_url = reverse_lazy('venta:crear_venta')
    success_message = 'Success: Cliente creado exitosamente.'

    def form_valid(self, form):
        form.instance.usuario_creador = self.request.user
        form.instance.empresa_id = self.request.session['company_id']
        return super().form_valid(form)


def busquedaClientes(request):
    # opcion 1
    # clientes = Persona.objects.filter(persona_tipo = 'C')
    # customers = []
    # for i in clientes:
    #    customers += [{'id': i.persona_id, 'name': i.nombre + ' - ' + i.identificacion}]
    # lista_clientes = list(customers)
    # return JsonResponse(lista_clientes, safe=False)

    # opcion 2
    clientes = Cliente.objects.all().values(
        'cliente_id', 'nombre', 'identificacion')
    lista_clientes = list(clientes)
    return JsonResponse(lista_clientes, safe=False)


def ajaxAgregarItem(request):
    dataId = request.GET.get('dataId', None)

    empresa_id = request.session['company_id']
    user_basket, status = Cesta.objects.get_or_create(
        usuario=request.user, clave_apli='CART-VENTA', empresa_id=empresa_id)

    # verifica items por factura
    filasEnCarrito = user_basket.obtener_total_filas()
    # filasPorFactura = current_user.perfil.empresa.factura_total_filas

    # secuencia_obj = Secuencia.objects.filter(
    #    empresa=current_user.perfil.empresa, sri_tipo_comprobante_id=1)[0]

    secuencia_obj = Secuencia.objects.filter(
        empresa_id=empresa_id, sri_tipo_comprobante_id=1)[0]

    if not secuencia_obj:
        return JsonResponse({
            'success': False,
            'message': "Secuencia incorrecta.",
        })
    filasPorFactura = secuencia_obj.comprobante_total_filas

    if (filasEnCarrito < filasPorFactura):
        # verifica codigo (bien o servicio)
        cadena_buscada = 'SRV-'
        # Si la sub-cadena no está presente el programa imprimirá el valor -1
        posicion_coincidencia = dataId.find(cadena_buscada)

        if (posicion_coincidencia == -1):
            # agregar productos
            productoId = dataId
            producto_obj = Producto.objects.get(pk=productoId)

            # new code
            almacen_obj = Almacen.objects.filter(
                es_principal=True, empresa_id=empresa_id)[0]
            control_producto = ControlProducto.objects.filter(
                producto=producto_obj, almacen=almacen_obj)
            existencia = 0
            if control_producto.exists():
                existencia = control_producto[0].stock

            # print("existencia=%s" % existencia)

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
                        "<td data-title='Descripción'><a href=/producto/detalle_producto/" + str(productoId) + " target='_blank'>" + producto_obj.nombre + "</a></td>" \
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
                        "<button type='button' data-id=" + str(cesta_item.pk) + " class='btn btn-info searchButton'><i class='fas fa-search'></i></button>" \
                        "</div>" \
                        "&nbsp;" \
                        "<div class='btn-group btn-group-sm'>" \
                        "<button type='button' data-id=" + str(cesta_item.pk) + " class='btn btn-warning deleteButton'><i class='fas fa-trash'></i></button>" \
                        "</div>" \
                        "</td>" \
                        "</tr>"

                    # agregar lote
                    loteAgregar(cesta_item)
                else:
                    markup = "<tr>" \
                        "<td style='display:none;'>" + str(cesta_item.pk) + "</td>" \
                        "<td data-title='Descripción'><a href=/producto/detalle_producto/" + str(productoId) + " target='_blank'>" + producto_obj.nombre + "</a></td>" \
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


def localizarAgregarElemento(request):
    if request.method == 'POST':
        # VERIFICAR ITEMS POR FACTURA
        empresa_id = request.session['company_id']
        secuencia_obj = Secuencia.objects.filter(
            empresa_id=empresa_id, sri_tipo_comprobante_id=1)[0]

        if not secuencia_obj:
            return JsonResponse({
                'success': False,
                'message': "Secuencia incorrecta.",
            })
        itemByInvoice = secuencia_obj.comprobante_total_filas

        # OBTENER TOTAL ITEMS EN CARRITO
        user_basket, status = Cesta.objects.get_or_create(
            usuario=request.user, clave_apli='CART-VENTA', empresa_id=empresa_id)
        itemsInCart = user_basket.obtener_total_filas()

        if itemsInCart <= itemByInvoice:
            # Obtiene datos POST
            postVar = request.POST.get('search_string', None)

            # BUSCA EN TABLA PRODUCTOS
            producto_obj = Producto.objects.get(
                Q(codigo_principal=postVar) | Q(nombre=postVar))
            if (producto_obj):
                # PRODUCTO

                almacen_obj = Almacen.objects.filter(
                    es_principal=True, empresa_id=empresa_id)[0]
                control_producto = ControlProducto.objects.filter(
                    producto=producto_obj, almacen=almacen_obj)
                existencia = 0
                if control_producto.exists():
                    existencia = control_producto[0].stock

                # print("existencia=%s" % existencia)

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
                        valor_iva = round(
                            (subtotal_12 * porcentaje_iva) / 100, 5)
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
                            "<td data-title='Descripción'><a href=/producto/detalle_producto/" + str(producto_obj.pk) + " target='_blank'>" + producto_obj.nombre + "</a></td>" \
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
                            "<button type='button' data-id=" + str(cesta_item.pk) + " class='btn btn-info searchButton'><i class='fas fa-search'></i></button>" \
                            "</div>" \
                            "&nbsp;" \
                            "<div class='btn-group btn-group-sm'>" \
                            "<button type='button' data-id=" + str(cesta_item.pk) + " class='btn btn-warning deleteButton'><i class='fas fa-trash'></i></button>" \
                            "</div>" \
                            "</td>" \
                            "</tr>"

                        # agregar lote
                        loteAgregar(cesta_item)
                    else:
                        markup = "<tr>" \
                            "<td style='display:none;'>" + str(cesta_item.pk) + "</td>" \
                            "<td data-title='Descripción'><a href=/producto/detalle_producto/" + str(producto_obj.pk) + " target='_blank'>" + producto_obj.nombre + "</a></td>" \
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
                        'dataId': producto_obj.pk,
                    })
            else:
                # SERVICIO
                return JsonResponse({
                    'success': False,
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
    empresa_id = request.session['company_id']
    user_basket = Cesta.objects.filter(
        usuario=request.user, clave_apli='CART-VENTA', empresa_id=empresa_id)[0]
    filasEnCarrito = user_basket.obtener_total_filas()

    secuencia_obj = Secuencia.objects.filter(
        empresa_id=empresa_id, sri_tipo_comprobante_id=1)[0]

    secuencia_obj = Secuencia.objects.filter(
        empresa_id=empresa_id, sri_tipo_comprobante_id=1)[0]
    if not secuencia_obj:
        return JsonResponse({
            'success': False,
            'message': "Secuencia incorrecta.",
        })
    filasPorFactura = secuencia_obj.comprobante_total_filas

    if (filasEnCarrito < filasPorFactura):
        producto_obj = Producto.objects.get(pk=productoId)
        cantidad = 1
        if producto_obj.precio_principal == 1:
            precio = producto_obj.precio_uno
            porcentaje_descuento = producto_obj.descuento_uno
        elif producto_obj.precio_principal == 2:
            precio = producto_obj.precio_dos
            porcentaje_descuento = producto_obj.descuento_dos
        elif producto_obj.precio_principal == 3:
            precio = producto_obj.precio_tres
            porcentaje_descuento = producto_obj.descuento_tre
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

        markup = "<tr>" \
            "<td style='display:none;'>" + str(cesta_item.pk) + "</td>" \
            "<td data-title='Descripción'><a href=/producto/detalle_producto/" + str(productoId) + " target='_blank'>" + producto_obj.nombre + "</a></td>" \
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

        # STOCK CERO, NO EXISTE LOTE
        # loteAgregar(cesta_item)

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
                usuario=request.user, clave_apli='CART-VENTA', empresa_id=empresa_id)[0]
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


def seleccionar_lote(request):
    if request.method == "GET":
        itemID = request.GET.get('id', None)

        # carrito_obj = CarritoVenta.objects.get(pk=carrito_id)

        # lote_cart_set = CarritoVentaLote.objects.filter(
        #    carrito=carrito_obj, producto=carrito_obj.producto)

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

            # important: convert the QuerySet to a list object
            company_id = request.session['company_id']
            almacen_obj = Almacen.objects.filter(
                es_principal=True, empresa_id=company_id)[0]

            stock_lote_obj = ControlProductoLote.objects.filter(
                cantidad__gt=0, producto=cesta_lote[0].item.producto, almacen=almacen_obj).values('id', 'lote__lote_numero')
            lista_lotes = list(stock_lote_obj)

            return JsonResponse({
                'success': True,
                'id': itemID,
                'producto': cesta_lote[0].item.producto.pk,
                'lotejson': data,
                'lista_lotes': lista_lotes
            })
        else:
            return JsonResponse({
                'success': False,
            })
    else:  # request.method == 'POST'
        cesta_item_pk = request.POST.get("id")
        # producto_id = request.POST.get("producto")
        # arrayPk = request.POST.getlist('pkArray[]')
        arrayLote = request.POST.getlist('loteArray[]')
        arrayExpira = request.POST.getlist('expiraArray[]')
        arrayQty = request.POST.getlist('qtyArray[]')

        """print(arrayLote)
        print(arrayExpira)
        print(arrayQty)
        print("Longitud Array Lote=%s" % (len(arrayLote)))
        print("Primer Indice: %s" % arrayLote[0])
        print("carrito id=%s" % cesta_item_pk)"""

        # eliminar lotes existentes
        CestaLote.objects.filter(item_id=cesta_item_pk).delete()

        i = 0
        while i < len(arrayLote):
            # print(arrayLote[i])
            # print(arrayExpira[i])
            # print(arrayQty[i])

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


def buscar_lote_seleccionado(request):
    lote_num = request.GET.get('lote_num', None)
    control_lote = ControlProductoLote.objects.filter(
        lote__lote_numero=lote_num)

    fecha_caducidad = None
    if control_lote:
        fecha_caducidad = control_lote[0].lote.fecha_caducidad

    print("FECHA CADUCIDAD")
    print(fecha_caducidad)

    return JsonResponse({
        'success': True,
        'fecha_caducidad': fecha_caducidad,
    })


def get_lot_list_by_product(request):
    producto_id = request.GET.get('producto_id', None)

    company_id = request.session['company_id']
    almacen_obj = Almacen.objects.filter(
        es_principal=True, empresa_id=company_id)[0]

    control_lote = ControlProductoLote.objects.filter(
        producto_id=producto_id, almacen=almacen_obj).values('lote__lote_numero')
    lista_lotes = list(control_lote)

    return JsonResponse({
        'success': True,
        'list': lista_lotes,
    })


'''
def ajaxVaciarCarrito(request):
    if request.method == "GET":
        current_user = request.user
        CarritoVenta.objects.filter(usuario=current_user).delete()

        return JsonResponse({'success': True})
'''


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
        cantidad = locale.atof(data.get('qty', 1))
        unidad = data.get('unit')
        precio = locale.atof(data.get('price', 0))
        porcentaje_descuento = locale.atof(data.get('discount', 0))

        empresa_id = request.session['company_id']
        user_basket = Cesta.objects.filter(
            usuario=request.user, clave_apli='CART-VENTA', empresa_id=empresa_id)[0]

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

            # ======================
            # NUEVO SUBMULTIPLO
            # ======================
            cantidad_fracc = cantidad
            if unit_obj == cesta_item.producto.unidad_secundaria:
                # TRANFORMAR SUBMULTIPLO Y PRECIO A UNIDAD PRINCIPAL

                equivalencia_unidad = cesta_item.producto.unidad_equivalencia

                cantidad_fracc = (cantidad * 1) / equivalencia_unidad

                # cost = precio
                # valor_total = qty * cost

            # ======================
            # FIN SUBMULTIPLO
            # ======================
            # print("EXISTENCIA=%s" % existencia)
            # print("CANTIDAD=%s" % cantidad)
            # print("FRACCION=%s" % cantidad_fracc)

            if (existencia > 0) and (cantidad_fracc <= existencia):

                # calculos linea
                subtotal_linea = cantidad * precio
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
                # cesta_item.precio_costo = precio_costo
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
                usuario=request.user, clave_apli='CART-VENTA', empresa_id=empresa_id)[0]

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


""" FUNCIÓN INTERCAMBIAR INFORMACIÓN FORMULARIO DE PAGO Y EL CONTROLADOR """


def ajaxIntercambioResumen(request):
    if request.method == 'POST':
        grand_total = request.POST.get('grand_total', default=None)
        fecha_emision = request.POST.get('fecha_emision', default=None)
        cliente_id = request.POST.get('cliente_id', default=None)
        firmar = request.POST.get('firmar', default=None)

        if (cliente_id == '0' or cliente_id == None):
            cliente_id = Cliente.objects.filter(
                identificacion='9999999999999')[0].cliente_id

        return JsonResponse({
            'success': True,
            'grand_total': grand_total,
            'fecha_emision': fecha_emision,
            'cliente_id': cliente_id,
            'firmar': firmar
        })


def modulo11(digs):
    cifra = 0
    factor = 2
    cadena = digs[::-1]  # invertir cadena
    for i in range(0, len(cadena)):
        cifra += int(cadena[i]) * factor

        if factor == 7:
            factor = 2
        else:
            factor += 1

    digito = 11 - (cifra % 11)
    if digito == 11:
        dv = 0
    else:
        if digito == 10:
            dv = 1
        else:
            dv = digito
    return str(dv)


def guardarFactura(request):
    if request.method == 'POST':
        # recibe datos del formulario modal 'paymentForm'
        data = request.POST.copy()
        cliente_id = data.get('cliente_id', default=0)
        fecha_emision = data.get('fecha_emision', default=None)
        codigo_forma_pago = data.get(
            'forma_pago', default=None)  # fact. elec, no utilizo
        # REVISAR TABLA DETALLE ADICIONAL => FORMAS DE PAGO

        # firmar = data.get('firmar', default=None)
        # pPayTable = data.get('pTableData', default=None)

        # today = datetime.date.today()
        current_user = request.user
        # empresa_obj = current_user.perfil.empresa
        if cliente_id == '0':
            obj = Cliente.objects.filter(identificacion='9999999999999')
            if obj.exists():
                cliente_id = obj[0].pk

        app_forma_pago_obj = FormaPago.objects.filter(
            codigo=codigo_forma_pago)[0]
        sri_forma_pago_obj = SriFormaPago.objects.filter(
            codigo=app_forma_pago_obj.sri_codigo)[0]

        company_id = request.session['company_id']
        empresa_obj = Empresa.objects.get(pk=company_id)
        cliente_obj = Cliente.objects.get(pk=cliente_id)
        estado_obj = FacturaEstado.objects.filter(nombre='CREADA')[0]

        # obtener codigo de secuencia
        tipo_comprobante_obj = SriTipoComprobante.objects.filter(codigo='01')[0]
        secuencia_obj = Secuencia.objects.filter(
            empresa=empresa_obj, sri_tipo_comprobante=tipo_comprobante_obj)[0]
        ultima_secuencia = secuencia_obj.ultima_secuencia
        secuencia_obj.ultima_secuencia += 1
        secuencia_obj.save()

        # if ultima_secuencia == None:
        #    ultima_secuencia = 0

        tipo_moneda_obj = SriTipoMoneda.objects.filter(codigo='DOLAR')[0]
        # seleccionar primer metodo de pago
        # JSON to Dict
        '''
        json_data = json.loads(pPayTable)
        for key in json_data:
            if key["ptype"] != "RT":
                app_forma_pago_obj = FormaPago.objects.filter(codigo=key["ptype"])[0]
                sri_forma_pago_obj = SriFormaPago.objects.filter(
                    codigo=app_forma_pago_obj.sri_codigo)[0]
                break
                '''

        # forma_pago_obj = SriFormaPago.objects.filter(codigo=sri_codigo_pago)[0]

        dt_obj = datetime.datetime.now()
        hora = dt_obj.strftime("%H:%M:%S")

        # crea clave de acceso
        # date_str = fecha_emision  # The date - 2018-11-24
        # format_str = '%Y-%m-%d'  # The format
        # datetime_obj = datetime.datetime.strptime(date_str, format_str)

        datetime_obj = datetime.datetime.strptime(
            '%s %s' % (fecha_emision, hora), "%Y-%m-%d %H:%M:%S")
        datetime_obj_utc = datetime_obj.replace(tzinfo=timezone('UTC'))

        # clave_acceso = datetime_obj.strftime("%d%m%Y") # fecha [8] digitos
        # clave_acceso += '01' # tipo de comprobante [2] digitos (01 FACTURA, 04 NOTA CRÉDITO)
        # clave_acceso += contribuyente_obj.ruc # número de ruc del contribuyente [13] digitos
        # clave_acceso += str(contribuyente_obj.tipo_ambiente) # tipo ambiente [1] digito (1 PRUEBAS, 2 PRODUCCION)
        # clave_acceso += secuencia_obj.punto_establecimiento + secuencia_obj.punto_emision # serie [6] digitos (codest + ptoemision)
        # clave_acceso += str(ultima_secuencia).zfill(9) # número del comprabante (secuencial) [9] digitos
        # clave_acceso += '12345678' # codigo numerico [8] digitos
        # clave_acceso += '1' # tipo emision [1] digito (1 Emisión Normal, 2 Emisión por Indisponibilidad del Sistema)
        # digito_verificador = modulo11(clave_acceso)
        # clave_acceso += digito_verificador # (modulo 11) [1] digito

        # calculo resumen
        empresa_id = request.session['company_id']
        user_basket = Cesta.objects.filter(
            usuario=request.user, clave_apli='CART-VENTA', empresa_id=empresa_id)[0]

        subtotal = user_basket.obtener_sub_total()
        valor_descuento = user_basket.obtener_total_descuento()
        valor_base_imponible = user_basket.obtener_base_imponible()
        valor_tarifa_cero = user_basket.obtener_total_tarifa_cero()
        valor_iva = user_basket.obtener_total_iva()
        valor_total = user_basket.obtener_gran_total()

        # guardar factura
        fact = Factura()
        fact.empresa = empresa_obj
        fact.cliente = cliente_obj
        fact.secuencia = secuencia_obj
        fact.sri_tipo_comprobante = tipo_comprobante_obj
        fact.sri_forma_pago = sri_forma_pago_obj  # campo facturación electrónica
        fact.sri_tipo_moneda = tipo_moneda_obj  # campo facturación electrónica
        fact.usuario_creador = current_user
        # fact.created_at = xxx
        # fact.update_at = xxx
        # fact.activo = xxx
        fact.estado = estado_obj
        ## currentDT = datetime.datetime.now()
        ## fact.fecha_emision = fecha_emision + ' ' + currentDT.strftime("%H:%M:%S")
        fact.fecha_emision = datetime_obj_utc
        fact.numero_secuencia = ultima_secuencia
        fact.clave_acceso = str(ultima_secuencia).zfill(
            49)  # facturas tradicionales
        # fact.numero_autorizacion = xxx
        # fact.fecha_autorizacion = xxx
        # fact.guia_remision = xxx
        fact.valor_descuento = valor_descuento
        fact.valor_subtotal_sin_impuesto = subtotal
        fact.valor_subtotal_12 = valor_base_imponible
        fact.valor_subtotal_0 = valor_tarifa_cero
        # fact.valor_subtotal_no_objeto_iva = 0
        # fact.valor_subtotal_exento = 0
        # fact.valor_base_imponible_ibrpnr = 0
        # fact.valor_subtotal_ibrpnr = 0
        fact.valor_ice = 0
        fact.valor_iva = valor_iva
        # fact.valor_propina = 0
        fact.valor_total = valor_total
        # fact.fecha_generado = xxx
        # fact.archivo_generado = xxx
        # fact.archivo_autorizado = xxx
        # fact.fecha_error = xxx
        # fact.archivo_error = xxx
        fact.save()

        # bodega_obj = Bodega.objects.filter(es_principal=True)[0]
        # bodega_id = bodega_obj.pk

        guardarOrdenDetalle(fact, user_basket)

        empresa_obj = Empresa.objects.get(pk=empresa_id)
        agregarTransKardex(orden=fact, cesta=user_basket,
                           empresa=empresa_obj, usuario=current_user)

        # payment = Payment(current_user, tipo_flujo="DEBE",
        # referencia="Venta", tabla=pPayTable, orden=fact)
        # payment.procesar()

        # vaciar cesta de ventas
        user_basket.vaciar_cesta()

        if empresa_obj.factel:
            """ PROCESO FACTURACIÓN ELECTRÓNICA """
            try:
                elemento = ElementoXML()
                ak_temp = elemento.get_clave_acceso(
                    datetime_obj.strftime("%d%m%Y"), fact)
                access_key = SriService.create_access_key(ak_temp)

                """ Generar archivo Xml """
                elemento_xml = elemento._generar_factura_xml(fact, access_key)

                """ Guardar xml generado """
                OPT_PATH = 'opt/facturas/'
                ruta_xml = '%s%s_G.xml' % (OPT_PATH, access_key)
                tree = etree.ElementTree(elemento_xml)
                tree.write(ruta_xml, pretty_print=True, xml_declaration=False,
                           encoding='utf-8', method="xml", standalone=False)
                print("->GUARDA XML GENERADO")

                """ Firmado del xml """
                token = fact.empresa.nombre_token
                password = fact.empresa.pin_token
                PK12PATH = 'facturae/data/%s' % (token)
                pk12_path = os.path.join(os.path.dirname(__file__), PK12PATH)

                xml = open(ruta_xml)
                p12 = open(pk12_path, "rb")
                xades = Xades()
                signed_document = xades.sign_python(
                    xml.read(), p12.read(), password)
                if signed_document == -1:
                    raise Exception("Error al Firmar!")
                print("->FIRMADO CORRECTAMENTE")

                """ Validacion xsd """
                inv_xml = DocumentXML(signed_document)
                if not inv_xml.validate_xml():
                    raise Exception("El XML no cumple el formato adecuado!")
                print("->PASO VALIDACION XSD")

                """ Opcional guarda xml firmado"""
                ruta_xml_firmado = '%s%s_F.xml' % (OPT_PATH, access_key)
                file = open(ruta_xml_firmado, "w")
                file.write(str(signed_document, "utf-8"))
                file.close()
                print("->GUARDA XML FIRMADO")

                # actualizar clave de acceso en db
                fact.clave_acceso = access_key
                fact.save()

                """ Llamadas al ws del sri """
                """ Envio del XML al SRI """
                xml_firma = open(ruta_xml_firmado)
                ok, errores, code = inv_xml.send_receipt(
                    xml_firma.read())  # envio al sri
                if not ok and code != 43:
                    raise Exception(errores)
                print("->ENVIADO AL SRI")

                """ Autorizacion del XML """
                # auth, m = inv_xml.request_authorization(access_key) #autorizo la clave
                auth, m = inv_xml.request_authorization(
                    access_key)  # autorizo la clave
                if not auth:
                    msg = ' '.join(list(itertools.chain(*m)))
                    raise Exception(msg)
                print("->ENVIADO A AUTORIZAR")

                """ Guarda xml autorizado """
                ruta_xml_autorizado = '%s%s_A.xml' % (OPT_PATH, access_key)
                auth_einvoice = inv_xml.render_authorized_einvoice(auth)
                file = open(ruta_xml_autorizado, "w")
                file.write(str(auth_einvoice, "utf-8"))
                file.close()
                print("->GUARDA XML AUTORIZADO")

                """ Generación del Comprobante en PDF o RIDE """
                ruta_pdf_autorizado = '%s%s_A.pdf' % (OPT_PATH, access_key)

                ruta_logo = 'facturae/data/hacienda_logo.jpg'
                logo_path = os.path.join(os.path.dirname(__file__), ruta_logo)

                xml = open(ruta_xml_autorizado)
                signed_document = xml.read()
                logo_data = ''

                if os.path.isfile(logo_path):
                    logo = open(logo_path, 'rb')
                    logo_data = logo.read()

                inv_xml = EnSystems()
                """ Llamadas al ws de los rides """
                ok, error, pdf = inv_xml.get_ride(
                    signed_document, logo_path, logo_data)  # envio al sri
                if not ok:
                    raise Exception(error)
                print("->RIDE CORRECTO")

                """ guarda xml autorizado """
                file = open(ruta_pdf_autorizado, "wb")
                file.write(pdf)
                file.close()
                print("->GUARDA PDF AUTORIZADO")

                """ Envio por correo(XML, PDF) """
                if auth:
                    send_mail_invoice(fact, auth, access_key)

                print("*** FINALIZO CORRECTAMENTE ***")
            except Exception as e:
                print(e)
            """ FIN PROCESO FACTURACIÓN ELECTRÓNICA """

        return JsonResponse({
            'success': True,
            'facturaId': fact.pk,
            'PRTDEV': secuencia_obj.comprobante_fisico_tipo_impresora
            # 'tabla_pagos': pPayTable,
        })


def guardarOrdenDetalle(fact, user_basket):
    # guardar carrito en detalle de facturas
    items = user_basket.obtener_items()

    for item in items:
        fact_det = FacturaDetalle()
        fact_det.factura = fact
        if item.tipo == 'PROD':  # producto
            fact_det.tipo = 'P'
            fact_det.producto = item.producto
        else:
            fact_det.tipo = 'S'
            fact_det.servicio = item.servicio
        fact_det.cantidad = item.cantidad
        fact_det.unidad = item.unidad_medida
        fact_det.precio_venta = item.precio
        fact_det.porcentaje_descuento = item.porcentaje_descuento
        fact_det.valor_descuento = item.valor_descuento
        fact_det.valor_subtotal_sin_impuesto = item.valor_subtotal_sin_impuesto
        fact_det.valor_subtotal_12 = item.valor_subtotal_12
        fact_det.valor_subtotal_0 = item.valor_subtotal_0
        fact_det.valor_subtotal_no_objeto_iva = item.valor_subtotal_no_objeto_iva
        fact_det.valor_subtotal_exento = item.valor_subtotal_exento
        fact_det.valor_base_imponible_ibrpnr = item.valor_base_imponible_ibrpnr
        fact_det.valor_subtotal_ibrpnr = item.valor_subtotal_ibrpnr
        fact_det.valor_ice = item.valor_ice
        fact_det.valor_iva = item.valor_iva
        fact_det.valor_total = item.valor_total
        fact_det.save()

    return True


""" FUNCIÓN AGREGAR TRANSACCIÓN AL INVENTARIO """


def agregarTransKardex(orden, cesta, empresa, usuario):
    # guardar carrito en detalle de facturas

    # referencia_obj = ReferenciaInventario.objects.get(pk=5)  # 5 = 'Salida => Factura de Venta'
    # Unidad.objects.filter(abreviatura=unidad)[0]

    pto_establecimiento = orden.secuencia.punto_establecimiento
    pto_emision = orden.secuencia.punto_emision
    sec_formateado = orden.get_numero_secuencia_formateado()
    numero_comprobante = "%s-%s-%s" % (pto_establecimiento,
                                       pto_emision, sec_formateado)

    # metodo_costo = usuario.perfil.empresa.metodo_costo
    almacen_obj = Almacen.objects.filter(es_principal=True)[0]
    tipo_movimiento_obj = TipoMovimiento.objects.filter(codigo='SAL_FACT')[0]

    # fecha_operacion_obj = orden.fecha_emision
    fecha_operacion_obj = orden.fecha_emision.strftime('%Y-%m-%d')

    items = cesta.obtener_items()
    for item in items:
        if item.tipo == 'PROD':  # PRODUCTO
            kardex = Kardex()
            # kardex.tipo = 2
            kardex.movimiento = tipo_movimiento_obj
            kardex.orden_id = orden.pk
            kardex.numero_comprobante = numero_comprobante
            kardex.referencia = "Venta"
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
                kardex.unidad = item.producto.unidad_principal

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

            # kardex.empresa = usuario.perfil.empresa
            kardex.empresa = empresa
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


class GeneratePDF(View):

    def get(self, request, *args, **kwargs):
        factura_id = request.GET.get('data', None)
        if factura_id is None:
            factura_id = kwargs.get("pk")

        factura_obj = Factura.objects.get(pk=factura_id)
        items = FacturaDetalle.objects.filter(factura_id=factura_id)

        # from django.contrib.sites.shortcuts import get_current_site
        # dominio = get_current_site(request).domain
        # ruta = '/media/pixmaps/%s_factura.jpg' % (factura_obj.empresa.ruc)
        # url_filigrana = 'http://{domain}{path}'.format(domain=dominio, path=ruta)

        ruta = '/media/pixmaps/%s_factura.jpg' % (factura_obj.empresa.ruc)
        url_filigrana = "{0}://{1}{2}".format(
            request.scheme, request.get_host(), ruta)

        params = {
            # 'orden_id': factura_id,
            # 'cliente_nombre': factura_obj.cliente.nombre,
            # 'cliente_direccion': factura_obj.cliente.direccion,
            # 'cliente_telefono': factura_obj.cliente.telefono,
            'tipo_comprobante': "FACTURA",
            'factura': factura_obj,
            'items': items,
            'plantilla_url': url_filigrana
            # 'plantilla_url': 'media/pixmaps/%s_factura.jpg' % (factura_obj.empresa.ruc)
        }

        # html = template.render(context)
        pdf = render_to_pdf('pdf/factura.html', params)
        #destination = 'pdf/%s_factura.html' % (factura_obj.empresa.ruc)

        ruta_destination = 'templates/pdf/%s_factura.html' % (
            factura_obj.empresa.ruc)
        destination = os.path.join(os.path.dirname(__file__), ruta_destination)

        if os.path.isfile(destination):
            pdf = render_to_pdf('pdf/%s_factura.html' %
                                (factura_obj.empresa.ruc), params)

        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "factura_%s.pdf" % (factura_id)
            content = "inline; filename=%s" % (filename)
            download = request.GET.get("download")
            if download:
                content = "attachment; filename=%s" % (filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Error Rendering PDF", status=400)

# class generate_view(View):
#     def get(self, request, *args, **kwargs):
#         template = get_template('pdf/factura.html')
#         context = {
#             'orden_id': 12345678,
#             'cliente:': 'JAVIER'
#         }
#         html = template.render(context)
#         return HttpResponse(html)


"""
Anular Factura
"""


def ajaxAnularComprobante(request, pk):
    factura_obj = get_object_or_404(Factura, pk=pk)

    if request.method == "GET":
        # Factura.objects.filter(pk=pk).update(estado_id='6')

        factura_obj.estado_id = '6'  # FACTURAS ANULADA SRI
        factura_obj.save()

        return JsonResponse({
            'success': True,
            'pk': pk
        })


""" FUNCIÓN MOSTRAR TICKET """


def mostrarFactura(request):
    if request.method == 'POST':
        if request.is_ajax():
            orderId = request.POST.get('orderId', None)

            return JsonResponse({
                'success': True,
                'message': "Proceso finalizado correctamente..."
            })


def is_valid_ip(str_ip_addr):
    """
    :return: returns true if IP is valid, else returns False
    """
    ip_blocks = str(str_ip_addr).split(".")
    if len(ip_blocks) == 4:
        for block in ip_blocks:
            # Check if number is digit, if not checked before calling this function
            if not block.isdigit():
                return False

            tmp = int(block)
            if 0 > tmp > 255:
                return False
        return True
    return False


""" FUNCIÓN IMPRIMIR TICKET """


def imprimirFactura(request):
    if request.method == 'POST':
        if request.is_ajax():
            orderId = request.POST.get('orderId', None)
            fact_det = FacturaDetalle.objects.filter(factura_id=orderId)

            current_user = request.user
            turno_obj = Turno.objects.filter(
                usuario_creador=current_user, activo=True)[0]
            company_id = request.session['company_id']
            empresa_obj = Empresa.objects.get(pk=company_id)
            # impresora = turno_obj.usuario.perfil.empresa.impresora_nombre
            impresora = empresa_obj.impresora_nombre

            if not impresora:
                return JsonResponse({
                    'success': False,
                })

            if is_valid_ip(impresora):
                Epson = printer.Network(impresora)
            else:
                Epson = Usb(0x0416, 0x5011, profile="POS-5890")

            # Set tab positions
            for item in fact_det:
                Epson.text(item.cantidad)
                Epson.tab()
                Epson.text(' x ' + item.producto.nombre)
                Epson.tab()
                Epson.text('$' + item.valor_total)

            # Cut paper
            Epson.cut()
            Epson.control("LF")

            # Envía un pulso eléctrico en la interfaz de contacto cercano, abrir cajon.
            # printer.drawerKickPulse()

            return JsonResponse({
                'success': True,
                'message': "Proceso finalizado correctamente..."
            })


def send_mail_invoice(fact, auth, access_key):
    """ configuración email backend """
    # config = Configuration.objects.get(**lookup_kwargs)
    backend = EmailBackend(host=fact.empresa.smtp_servidor, port=fact.empresa.smtp_puerto,
                           username=fact.empresa.smtp_usuario, password=fact.empresa.smtp_clave,
                           use_tls=fact.empresa.smtp_seguridad, fail_silently=False)

    nroFact = fact.secuencia.punto_establecimiento + '-' + \
        fact.secuencia.punto_emision + '-' + \
        str(fact.numero_secuencia).zfill(9)
    OPT_PATH = 'opt/facturas/'
    ruta_xml = '%s%s_A.xml' % (OPT_PATH, access_key)
    ruta_pdf = '%s%s_A.pdf' % (OPT_PATH, access_key)
    # subject, from_email, to = 'Factura Electrónica ' + nroFact, 'infojavo@gmail.com', 'nolealejandrina@gmail.com'
    subject, from_email, to = 'Factura Electrónica ' + \
        nroFact, fact.empresa.smtp_usuario, fact.cliente.email
    text_content = '...'
    html_content = '<p>Estimado(a): ' + fact.cliente.nombre + '</p>'
    html_content += '<p>A continuación le presentamos los detalles de su factura electrónica.</p><br>'
    html_content += '<p><strong>DETALLES</strong><br>'
    html_content += '<br><strong>Fecha Emisión:</strong> ' + \
        fact.created_at.strftime('%d/%m/%Y %H:%M:%S')
    html_content += '<br><strong>Estado Autorización:</strong> ' + auth.estado
    html_content += '<br><strong>Ambiente:</strong> ' + auth.ambiente
    html_content += '<br><strong>Núemro de Autorización:</strong> ' + auth.numeroAutorizacion
    html_content += '<br><strong>Fecha Autorización:</strong> ' + \
        auth.fechaAutorizacion.strftime("%d/%m/%Y %H:%M:%S")
    html_content += '<br><strong>Monto cancelado:</strong> ' + \
        str(round(fact.valor_total, 2))
    html_content += '<br><br><em>Adjunto archivos XML y PDF.</em><p>'
    msg = EmailMultiAlternatives(subject, text_content, from_email, [
                                 to], connection=backend)
    msg.attach_alternative(html_content, "text/html")
    msg.attach_file(ruta_xml)
    msg.attach_file(ruta_pdf)
    msg.send()


def register_edit(request, pk):

    # Either render only the modal content, or a full standalone page
    if request.is_ajax():
        template_name = 'frontend/includes/register_edit_form_inner.html'
    else:
        template_name = 'frontend/includes/register_edit_form.html'

    register = get_object_by_uuid_or_404(Register, pk)

    if request.method == 'POST':
        form = RegisterEditForm(instance=register, data=request.POST)
        if form.is_valid():
            form.save()
    else:
        form = RegisterEditForm(instance=register)

    return render(request, template_name, {
        'register': register,
        'form': form,
    })


class CuentasCobrarIndexView(ListView):
    model = Turno
    template_name = 'venta/cuentas_por_cobrar.html'

    def get_queryset(self):
        # query=08/27/2019 - 08/27/2019
        query = self.request.GET.get("daterange")
        current_company_id = self.request.session['company_id']
        # empresa_obj = Empresa.objects.get(pk=current_company_id)

        if query:
            from_date = query[0:10]  # 08/27/2019
            to_date = query[13:23]  # 08/27/2019

            start_date = datetime.datetime.strptime(
                from_date, "%d/%m/%Y").date()
            end_date = datetime.datetime.strptime(to_date, "%d/%m/%Y").date()

            object_list = PagoCredito.objects.filter(
                pago__tipo_flujo='D',
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
                pago__tipo_flujo='D',
                saldo__gt=0,
                estado__lt=3,
                vence__range=(
                    index_start_date, index_end_date), empresa_id=current_company_id).order_by('vence')'''
            object_list = PagoCredito.objects.filter(
                pago__tipo_flujo='D', saldo__gt=0, estado__lt=3).order_by('vence')

        return object_list


""" FORMULARIOS CUENTAS POR COBRAR """
'''
class ListadoCuentasPorCobrar(ListView):
    template_name = 'venta/cuentas_por_cobrar.html'
    context_object_name = 'page'

    def get_queryset(self):
        queryset_list = PagoCredito.objects.filter(pago__tipo_flujo='D', saldo__gt=0).only(
            'pago', 'vence', 'valor_cuota', 'abono', 'saldo', 'estado').order_by('vence')
        query = self.request.GET.get("q", '')
        paginate_by = self.request.GET.get('rpp', 10)

        if query:
            queryset_list = queryset_list.filter(
                    Q(estado__lt=3) &
                    Q(pago__venta__cliente__nombre__icontains=query) |
                    Q(pago__venta__cliente__identificacion__icontains=query)
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


def ajaxPaymentView(request):
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

        current_user = request.user
        credito = PagoCredito.objects.get(pk=credito_id)

        factura_id = credito.pago.venta_id
        factura_venta_obj = Factura.objects.get(pk=factura_id)
        payment = Payment(current_user, tipo_flujo="DEBE",
                          referencia="Cuentas por cobrar", tabla=pPayTable, orden=factura_venta_obj)
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
            'monto': monto_pagado,
            'venta': factura_id
        })


class RetencionesIndexView(ListView):
    template_name = 'venta/retenciones_ventas.html'
    context_object_name = 'all_sales'

    def get_queryset(self):
        queryset_list = Factura.objects.only(
            'fecha_emision', 'cliente', 'secuencia', 'estado', 'valor_total').order_by('-fecha_emision')
        query = self.request.GET.get("q")
        if query:
            queryset_list = queryset_list.filter(
                Q(cliente__nombre__icontains=query)
            ).distinct().order_by('-fecha_emision')
        paginator = Paginator(queryset_list, 10)  # Show 10 contacts per page
        page = self.request.GET.get('page')
        try:
            queryset_list = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            queryset_list = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 999), deliver last page of results.
            queryset_list = paginator.page(paginator.num_pages)

        return queryset_list


""" FUNCIÓN IMPRIMIR TICKET """


"""def ticket_pdf(request, inflow_id):
    # inflow = get_object_or_404(Inflow, pk=inflow_id)
    params = {
        'tipo_comprobante': "FACTURA COMPRA",
    }

    # html = template.render(context)
    pdf = render_to_pdf('pdf/ticket_pdf.html', params)
    return HttpResponse(pdf, content_type='application/pdf')"""


def html_to_pdf_directly_ticket(request, inflow_id):
    if request.is_ajax():

        invoice = Factura.objects.get(pk=inflow_id)

        #from reportlab.pdfgen import canvas
        from reportlab.pdfgen.canvas import Canvas
        from reportlab.platypus import Table
        from reportlab.lib.units import cm

        pdf_file = "media/recibos/ticket_{}.pdf".format(inflow_id)
        pagesize = (7.5 * cm, 21.5 * cm)

        canvas = Canvas(pdf_file, pagesize=pagesize)
        canvas.setFont('Helvetica', 9)
        #can.drawString(0.5*mm, 45*mm, "Ticket: {}".format(inflow_id))
        #t = can.beginText()
        #t.setTextOrigin(0.5*mm, 45*mm)
        #t.textLine("Ticket: {}".format(inflow_id))
        # can.drawText(t)

        # Info
        DATE_FORMAT = "%Y-%m-%d"
        TIME_FORMAT = "%H:%M:%S"

        temp_date = invoice.fecha_emision
        fecha = temp_date.strftime(DATE_FORMAT)
        hora = temp_date.strftime(TIME_FORMAT)

        textobject = canvas.beginText(0.5 * cm, 17 * cm)
        textobject.textLine(u'TICKET: %s' % inflow_id)
        textobject.textLine(u'FEC.: %s  HORA: %s' % (fecha, hora))
        textobject.textLine(u'SR.(A): %s' % invoice.cliente.nombre)
        textobject.textLine(u'CED/RUC: %s' % invoice.cliente.identificacion)
        textobject.textLine(u'DIR: %s' % invoice.cliente.direccion)
        canvas.drawText(textobject)

        # Items
        data = [[u'CANT', u'DESCRIPCIÓN', u'V. UNIT', u'S-TOTAL'], ]
        factura_set = FacturaDetalle.objects.filter(factura_id=inflow_id)
        for item in factura_set:
            data.append([
                str(locale.format('%.2f', item.cantidad)),
                item.producto.nombre[0:15],
                str(locale.format('%.2f', item.precio_venta)),
                str(locale.format('%.2f', item.valor_total)),
            ])

        # RESUMEN (PIE DE TICKET)
        procentaje_iva = str(
            round(SriTarifaIVA.objects.filter(codigo='2')[0].porcentaje)) + '%'

        data.append([u'', u'', u'SUBTOTAL:', str(
            locale.format('%.2f', invoice.valor_subtotal_sin_impuesto))])
        data.append([u'', u'', u'DESCUENTO:', str(
            locale.format('%.2f', invoice.valor_descuento))])
        data.append([u'', u'', u'BASE %s:' % procentaje_iva, str(
            locale.format('%.2f', invoice.valor_subtotal_12))])
        data.append([u'', u'', u'BASE 0%:', str(
            locale.format('%.2f', invoice.valor_subtotal_0))])
        data.append([u'', u'', u'IVA %s:' % procentaje_iva,
                     str(locale.format('%.2f', invoice.valor_iva))])
        data.append([u'', u'', u'TOTAL:', str(
            locale.format('%.2f', invoice.valor_total))])

        table = Table(data, colWidths=[1.2 * cm, 2.80 * cm,
                                       1.5 * cm, 1.5 * cm], rowHeights=0.4 * cm)

        table.setStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            # ('TEXTCOLOR', (0, 0), (-1, -1), (0.2, 0.2, 0.2)),
            # ('GRID', (0, 0), (-1, -2), 1, (0.7, 0.7, 0.7)), # grid tabla
            # ('GRID', (-2, -1), (-1, -1), 1, (0.7, 0.7, 0.7)), # grid subtotal
            ('ALIGN', (-2, 0), (-1, -1), 'RIGHT'),
            # ('BACKGROUND', (0, 0), (-1, 0), (0.8, 0.8, 0.8)),
        ])

        # Establecemos el tamaño de la hoja que ocupará la tabla
        tw, th, = table.wrapOn(canvas, 6.5 * cm, 10 * cm)

        # Definimos la coordenada donde se dibujará la tabla
        table.drawOn(canvas, 0.25 * cm, 15 * cm - th)

        canvas.showPage()
        canvas.save()

        return JsonResponse({
            'success': True,
            'file': pdf_file,
        })


'''
def draw_header(canvas):
    from reportlab.lib.units import cm

    """ Draws the invoice header """
    canvas.setStrokeColorRGB(0.9, 0.5, 0.2)
    canvas.setFillColorRGB(0.2, 0.2, 0.2)
    canvas.setFont('Helvetica', 16)
    canvas.drawString(18 * cm, -1 * cm, 'Invoice')
    #canvas.drawInlineImage(settings.INV_LOGO, 1 * cm, -1 * cm, 250, 16)
    canvas.setLineWidth(4)
    canvas.line(0, -1.25 * cm, 21.7 * cm, -1.25 * cm)


def draw_address(canvas):
    from reportlab.lib.units import cm

    """ Draws the business address """
    business_details = (
        u'COMPANY NAME LTD',
        u'STREET',
        u'TOWN',
        U'COUNTY',
        U'POSTCODE',
        U'COUNTRY',
        u'',
        u'',
        u'Phone: +00 (0) 000 000 000',
        u'Email: example@example.com',
        u'Website: www.example.com',
        u'Reg No: 00000000'
    )
    canvas.setFont('Helvetica', 9)
    textobject = canvas.beginText(13 * cm, -2.5 * cm)
    for line in business_details:
        textobject.textLine(line)
    canvas.drawText(textobject)


def draw_footer(canvas):
    from reportlab.lib.units import cm

    """ Draws the invoice footer """
    note = (
        u'Bank Details: Street address, Town, County, POSTCODE',
        u'Sort Code: 00-00-00 Account No: 00000000 (Quote invoice number).',
        u'Please pay via bank transfer or cheque. All payments should be made in CURRENCY.',
        u'Make cheques payable to Company Name Ltd.',
    )
    textobject = canvas.beginText(1 * cm, -27 * cm)
    for line in note:
        textobject.textLine(line)
    canvas.drawText(textobject)


def html_to_pdf_directly_ticket(request, inflow_id):
    invoice = Factura.objects.get(pk=inflow_id)

    #from reportlab.pdfgen import canvas
    from reportlab.pdfgen.canvas import Canvas
    from reportlab.platypus import Table
    from reportlab.lib.units import cm
    from reportlab.lib.pagesizes import A4

    """ Draws the invoice """
    pdf_file = "media/recibos/ticket_{}.pdf".format(inflow_id)
    canvas = Canvas(pdf_file, pagesize=A4)
    canvas.translate(0, 29.7 * cm)
    canvas.setFont('Helvetica', 10)

    canvas.saveState()
    draw_header(canvas)
    canvas.restoreState()

    canvas.saveState()
    draw_footer(canvas)
    canvas.restoreState()

    canvas.saveState()
    draw_address(canvas)
    canvas.restoreState()

    invoice = Factura.objects.get(pk=inflow_id)

    # Client address
    textobject = canvas.beginText(1.5 * cm, -2.5 * cm)
    # if invoice.address.contact_name:
    #    textobject.textLine(invoice.address.contact_name)
    textobject.textLine(invoice.cliente.direccion)
    # if invoice.address.address_two:
    #    textobject.textLine(invoice.address.address_two)
    # textobject.textLine(invoice.address.town)
    # if invoice.address.county:
    #    textobject.textLine(invoice.address.county)
    # textobject.textLine(invoice.address.postcode)
    # textobject.textLine(invoice.address.country.name)
    canvas.drawText(textobject)

    # Info
    textobject = canvas.beginText(1.5 * cm, -6.75 * cm)
    textobject.textLine(u'Invoice ID: %s' % inflow_id)
    textobject.textLine(u'Invoice Date: %s' % invoice.fecha_emision.strftime('%d %b %Y'))
    textobject.textLine(u'Client: %s' % invoice.cliente.nombre)
    canvas.drawText(textobject)

    # Items
    #data = [[u'Quantity', u'Description', u'Amount', u'Total'], ]
    data = [[u'CANT', u'DESCRIPCIÓN', u'V. UNIT', u'S-TOTAL'], ]
    factura_set = FacturaDetalle.objects.filter(factura_id=inflow_id)
    for item in factura_set:
        # for item in invoice.items.all():
        data.append([
            item.cantidad,
            item.producto.nombre,
            locale.format('%.2f', item.precio_venta),
            locale.format('%.2f', item.valor_total)
        ])
        #locale.format('%.2f', item.precio_venta)
    data.append([u'', u'', u'Total:', locale.format('%.2f', item.precio_venta)])
    table = Table(data, colWidths=[2 * cm, 11 * cm, 3 * cm, 3 * cm])
    table.setStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), (0.2, 0.2, 0.2)),
        ('GRID', (0, 0), (-1, -2), 1, (0.7, 0.7, 0.7)),
        ('GRID', (-2, -1), (-1, -1), 1, (0.7, 0.7, 0.7)),
        ('ALIGN', (-2, 0), (-1, -1), 'RIGHT'),
        ('BACKGROUND', (0, 0), (-1, 0), (0.8, 0.8, 0.8)),
    ])
    tw, th, = table.wrapOn(canvas, 15 * cm, 19 * cm)
    table.drawOn(canvas, 1 * cm, -8 * cm - th)

    canvas.showPage()
    canvas.save()

    return JsonResponse({
        'success': True,
        'file': pdf_file,
    })
'''


def generar_archivo_binario(request):
    if request.method == "GET":
        #from escpos.printer import Dummy
        #dummy_printer = Dummy()
        #dummy_printer.text("This is my image:\n")
        # dummy_printer.cut()

        from escpos import printer

        # A wrapper to organise item names & prices into columns
        class item:
            def __init__(self, name="", price="", dollarSign=False):
                self.name = name
                self.price = price
                self.dollarSign = dollarSign

            def encode(self):
                rightCols = 6
                leftCols = 24
                if(self.dollarSign):
                    leftCols = leftCols / 2 - rightCols / 2
                left = self.name.ljust(leftCols)
                sign = "$" if self.dollarSign else ""
                right = (sign + self.price).rjust(rightCols)
                return (left + right + "\n").encode()

        # Information for the receipt
        items = [
            item(name="Example item #1", price="4.00"),
            item(name="Another thing", price="3.50"),
            item(name="Something else", price="1.00"),
            item(name="A final item", price="4.45")
        ]
        subtotal = item(name="Subtotal", price="12.95")
        tax = item(name="A local tax", price="1.30")
        ##total = item(name="Total", price="14.25", dollarSign=True)
        total = item(name="Total", price="14.25")

        # Date is kept the same for testing
        date = "Monday 6th of April 2015 02:56:25 PM"

        # Start the printer
        MEDIA_PATH = '../../media/recibos/'
        ruta_binary = '%sarchivo_binario.bin' % (MEDIA_PATH)
        binary_path = os.path.join(os.path.dirname(__file__), ruta_binary)
        p = printer.File(binary_path)
        #p = Dummy()

        # Print top logo
        # p.set(align="center")
        #p.image("escpos-php.png", impl="bitImageColumn")

        # Name of shop
        p.set(align="center", width=2)
        p.text("ExampleMart Ltd.\n")
        p.set(align="center")
        p.text("Shop No. 42.\n")
        p.text("\n")

        # Title of receipt
        p.set(align="center", text_type="B")
        p.text("SALES INVOICE\n")

        # Items
        p.set(align="left", text_type="B")
        p.text(item(name="", price="$"))
        p.set(align="left")
        for item in items:
            p.text(item)
        p.set(text_type="B")
        p.text(subtotal)
        p.text("\n")

        # Tax and total
        p.set()
        p.text(tax)
        # p.set(width=2)
        p.text(total)

        # Footer
        p.text("\n\n")
        p.set(align="center")
        p.text("Thank you for shopping at\nExampleMart.\n")
        p.text("For trading hours, please visit example.com\n")
        p.text("\n\n")
        p.text(date + "\n")

        # Cut the paper
        p.cut()
        p.control("LF")

        return JsonResponse({
            'success': True,
        })


def imprimirTicketLocalNetwork(request):
    if request.method == 'POST':
        if request.is_ajax():
            facturaId = request.POST.get('facturaId', None)

            current_user = request.user
            # turno_obj = Turno.objects.filter(usuario_creador=current_user, activo=True)[0]

            # secuencia_obj = Secuencia.objects.filter(
            #    empresa=current_user.perfil.empresa, sri_tipo_comprobante_id=1)[0]

            company_id = request.session['company_id']
            secuencia_obj = Secuencia.objects.filter(
                empresa_id=company_id, sri_tipo_comprobante_id=1)[0]
            # tipo_impresora = secuencia_obj.comprobante_fisico_tipo_impresora
            # tipo_protocolo = secuencia_obj.comprobante_fisico_tipo_protocolo

            factura_obj = Factura.objects.get(pk=facturaId)
            fact_det = FacturaDetalle.objects.filter(factura=factura_obj)

            # impresora = turno_obj.usuario.perfil.empresa.impresora_nombre
            # headerMargin = turno_obj.usuario.perfil.empresa.factura_margen_superior
            # footerMargin = turno_obj.usuario.perfil.empresa.factura_margen_inferior
            # copies = turno_obj.usuario.perfil.empresa.factura_total_copias

            tipo_protocolo = secuencia_obj.comprobante_fisico_tipo_protocolo
            nombre_impresora = secuencia_obj.comprobante_fisico_nombre_impresora
            headerMargin = secuencia_obj.comprobante_fisico_margen_superior
            footerMargin = secuencia_obj.comprobante_fisico_margen_inferior
            copies = secuencia_obj.comprobante_fisico_total_copias

            if not nombre_impresora:
                return JsonResponse({
                    'success': False,
                })

            array = []
            for item in fact_det:
                # MARCAR PRODUCTOS SIN IMPUESTOS
                if item.valor_subtotal_0 > 0:
                    text = '*' + item.producto.nombre
                else:
                    text = item.producto.nombre

                new_item = item_detail(str(round(item.cantidad, 2)), text, str(
                    round(item.precio_venta, 2)), str(round(item.valor_total, 2)))
                array.append(new_item.getSymplify())

            # python-escpos - Python library to manipulate ESC/POS Printers
            NETWORK, WIFI, USB = (1, 2, 3)
            if (tipo_protocolo == NETWORK or tipo_protocolo == WIFI):
                if is_valid_ip(nombre_impresora):
                    Epson = printer.Network(nombre_impresora)
                else:
                    return JsonResponse({
                        'success': False,
                    })
            else:
                # sudo lsusb
                # salida dispositivo
                # Bus 001 Device 007: ID 1a86:7584 QinHeng Electronics CH340S
                # detalles
                # lsusb -vvv -d 1a86:7584
                # output command
                # idVendor           0x1a86 QinHeng Electronics
                # idProduct          0x7584 CH340S
                # bEndpointAddress     0x82  EP 2 IN
                # bEndpointAddress     0x02  EP 2 OUT

                #Epson = Usb(0x1a86, 0x7584, profile="TM-P2.01")
                Epson = Usb(0x1a86, 0x7584, 0, 0x82, 0x02)  # LINUX OK

            # pip install python-escpos
            # Epson = printer.Network("192.168.0.20")
            # Epson.set(font='a', height=2, align='center', text_type='bold')

            # EMCABEZADO FACTURA
            Epson.charcode("MULTILINGUAL")  # para soporte UTF-8, tildes
            Epson.set(font='b')

            # Parse datetime model field to string
            DATE_FORMAT = "%Y-%m-%d"
            TIME_FORMAT = "%H:%M:%S"

            temp_date = factura_obj.fecha_emision
            fecha = temp_date.strftime(DATE_FORMAT)
            hora = temp_date.strftime(TIME_FORMAT)

            for i in range(copies):
                # margen encabezado
                for x in range(1, headerMargin):
                    Epson.text('\n')

                # Epson.image(settings.MEDIA_ROOT + '/gallery/Logo/quimico-2.png')
                # archivo_imagen = settings.MEDIA_ROOT + "/gallery/Logo/quimico-2.png"
                # Epson.image(archivo_imagen)

                # Print top logo
                # Epson.set(align="center")
                # Epson.image(archivo_imagen, impl="bitImageRaster")

                # instance = Dummy()
                # instance.set(height=2, width=2)
                # instance.image(settings.MEDIA_ROOT + "/gallery/Logo/quimico-2.png", impl="bitImageColumn", fragment_height=1)

                # instance = printer.Dummy()
                # instance.image(settings.MEDIA_ROOT + "/gallery/Logo/prueba.jpg", impl="bitImageColumn")
                # Epson._raw(instance.output)

                # d = Dummy()
                # d.image("quimico-2.png")
                # d.cut()
                # send code to printer
                # Epson._raw(d.output)

                # printer.line_spacing(2)

                new_item = item_footer("FECHA: " + fecha, "HORA: " + hora)
                Epson.text(new_item.getSymplify())
                # subtrae 31 caracteres
                Epson.text("SR.(ES): " +
                           factura_obj.cliente.nombre[:31] + "\n")
                Epson.text("DIR: " + factura_obj.cliente.direccion[:35] + "\n")

                telefono_src = factura_obj.cliente.telefono
                celular_src = factura_obj.cliente.celular
                #telefono_strip = telefono_src.strip()
                #celular_strip = celular_src.strip()
                if telefono_src:
                    telefono_strip = telefono_src.strip()
                    telefono = telefono_strip
                else:
                    if celular_src:
                        celular_strip = celular_src.strip()
                        telefono = celular_strip
                    else:
                        telefono = 'N/A'

                new_item = item_footer("TLF: " + telefono,
                                       "RUC: " + factura_obj.cliente.identificacion)
                Epson.text(new_item.getSymplify())

                # DETALLE FACTURA
                Epson.set(font='b')
                Epson.text("----------------------------------------\n")
                new_item = item_detail(
                    'CANT', 'DESCRIPCION', 'PRECIO', ' TOTAL')
                Epson.text(new_item.getSymplify())
                Epson.text("----------------------------------------\n")

                for item in array:
                    Epson.text(item)

                # PIE DE FACTURA
                # itemByInvoice = turno_obj.usuario.perfil.empresa.factura_total_filas
                itemByInvoice = secuencia_obj.comprobante_total_filas
                itemsInCart = len(array)
                blank_rows = itemByInvoice - itemsInCart
                if blank_rows > 0:
                    for x in range(1, blank_rows):
                        Epson.text('\n')

                # imprimir linea horizontal del pie de pagina
                Epson.text("----------------------------------------\n")

                if factura_obj:
                    fac_subtotal = factura_obj.valor_subtotal_sin_impuesto
                    fac_descuento = factura_obj.valor_descuento
                    fac_base_12 = factura_obj.valor_subtotal_12
                    fac_base_zero = factura_obj.valor_subtotal_0
                    fac_iva = factura_obj.valor_iva
                    fac_total = factura_obj.valor_total

                procentaje_iva = str(
                    round(SriTarifaIVA.objects.filter(codigo='2')[0].porcentaje)) + '%'

                aux_subtotal = repeat_to_length(
                    ' ', 9 - len(str('%.2f') % fac_subtotal)) + '%.2f' % fac_subtotal
                summary_subtotal = item_footer(
                    "NUM:" + facturaId, "SUBTOTAL : %s" % aux_subtotal).getSymplify()

                aux_descuento = repeat_to_length(
                    ' ', 9 - len(str('%.2f') % fac_descuento)) + '%.2f' % fac_descuento
                summary_descuento = item_footer(
                    "", "*DESC.   : %s" % aux_descuento).getSymplify()

                aux_base_12 = repeat_to_length(
                    ' ', 9 - len(str('%.2f') % fac_base_12)) + '%.2f' % fac_base_12
                summary_base_12 = item_footer("", "*BASE %s: %s" %
                                              (procentaje_iva, aux_base_12)).getSymplify()

                aux_base_zero = repeat_to_length(
                    ' ', 9 - len(str('%.2f') % fac_base_zero)) + '%.2f' % fac_base_zero
                summary_base_zero = item_footer("", "BASE   %s: %s" %
                                                ('0%', aux_base_zero)).getSymplify()

                aux_iva = repeat_to_length(
                    ' ', 9 - len(str('%.2f') % fac_iva)) + '%.2f' % fac_iva
                summary_iva = item_footer("", "IVA   %s: %s" %
                                          (procentaje_iva, aux_iva)).getSymplify()

                aux_total = repeat_to_length(' ', 9 - len(str('%.2f') %
                                                          fac_total)) + '%.2f' % fac_total
                summary_total = item_footer(
                    "", "TOT. FAC : %s" % aux_total).getSymplify()

                Epson.text(summary_subtotal)
                Epson.text(summary_descuento)
                Epson.text(summary_base_12)
                Epson.text(summary_base_zero)
                Epson.text(summary_iva)
                Epson.text(summary_total)

                # margen encabezado
                for x in range(1, footerMargin):
                    Epson.text('\n')

                # Cut paper
                Epson.cut()
                Epson.control("LF")

            return JsonResponse({
                'success': True,
                'message': "Ticket impreso correctamente...",
            })


def imprimirTicketInterfazWeb(request):
    if request.method == 'POST':
        if request.is_ajax():

            factura_id = request.POST.get('facturaId', None)
            factura_obj = Factura.objects.get(pk=factura_id)
            fact_det = FacturaDetalle.objects.filter(factura=factura_obj)

            company_id = request.session['company_id']
            secuencia_obj = Secuencia.objects.filter(
                empresa_id=company_id, sri_tipo_comprobante_id=1)[0]

            # Start the printer
            MEDIA_PATH = '../../media/recibos/'  # DIRECCION DESARROLLO
            # MEDIA_PATH = '../../../media/recibos/'  # DIRECCION PRODUCCION
            ruta_binary = '%sticket_%s.bin' % (MEDIA_PATH, factura_id)
            binary_path = os.path.join(os.path.dirname(__file__), ruta_binary)

            from escpos import printer
            p = printer.File(binary_path)
            # p.codepage="cp720"
            p.charcode("MULTILINGUAL")
            p.set(font='b')
            # p.set(font='A')

            #p.set(align="center", width=2)
            #p.set(align="left", text_type="B")

            #p.set(align="left", text_type="A")

            # items del ticket
            array = []
            for item in fact_det:
                # marcar productos sin impuestos
                if item.valor_subtotal_0 > 0:
                    text = '*' + item.producto.nombre
                else:
                    text = item.producto.nombre

                new_item = item_detail(str(round(item.cantidad, 2)), text, str(
                    round(item.precio_venta, 2)), str(round(item.valor_total, 2)))
                array.append(new_item.getSymplify())

            # margen superior ticket
            headerMargin = secuencia_obj.comprobante_fisico_margen_superior
            footerMargin = secuencia_obj.comprobante_fisico_margen_inferior
            numberCopies = secuencia_obj.comprobante_fisico_total_copias
            for x in range(1, headerMargin):
                p.text('\n')

            # encabezado del ticket
            DATE_FORMAT = "%Y-%m-%d"
            TIME_FORMAT = "%H:%M:%S"
            # Parse datetime model field to string
            temp_date = factura_obj.fecha_emision
            fecha = temp_date.strftime(DATE_FORMAT)
            hora = temp_date.strftime(TIME_FORMAT)

            new_item = item_footer("FECHA: " + fecha, "HORA: " + hora)
            p.text(new_item.getSymplify())
            # subtrae 31 caracteres
            p.text("SR.(ES): " + factura_obj.cliente.nombre[:31] + "\n")
            p.text("DIR: " + factura_obj.cliente.direccion[:35] + "\n")
            new_item = item_footer("TLF: " + factura_obj.cliente.telefono,
                                   "RUC: " + factura_obj.cliente.identificacion)
            p.text(new_item.getSymplify())

            # detalle del ticket
            p.set(font='b')
            p.text("----------------------------------------\n")
            new_item = item_detail('CANT', 'DESCRIPCION', 'PRECIO', ' TOTAL')
            p.text(new_item.getSymplify())
            p.text("----------------------------------------\n")

            for item in array:
                p.text(item)

            # pie del ticket
            itemByInvoice = secuencia_obj.comprobante_total_filas
            itemsInCart = len(array)
            blank_rows = itemByInvoice - itemsInCart
            if blank_rows > 0:
                for x in range(1, blank_rows):
                    p.text('\n')

            # imprimir linea horizontal del pie de pagina
            p.text("----------------------------------------\n")

            if factura_obj:
                fac_subtotal = factura_obj.valor_subtotal_sin_impuesto
                fac_descuento = factura_obj.valor_descuento
                fac_base_12 = factura_obj.valor_subtotal_12
                fac_base_zero = factura_obj.valor_subtotal_0
                fac_iva = factura_obj.valor_iva
                fac_total = factura_obj.valor_total

            procentaje_iva = str(
                round(SriTarifaIVA.objects.filter(codigo='2')[0].porcentaje)) + '%'

            aux_subtotal = repeat_to_length(
                ' ', 9 - len(str('%.2f') % fac_subtotal)) + '%.2f' % fac_subtotal
            summary_subtotal = item_footer(
                "NUM:" + factura_id, "SUBTOTAL : %s" % aux_subtotal).getSymplify()

            aux_descuento = repeat_to_length(
                ' ', 9 - len(str('%.2f') % fac_descuento)) + '%.2f' % fac_descuento
            summary_descuento = item_footer(
                "", "*DESC.   : %s" % aux_descuento).getSymplify()

            aux_base_12 = repeat_to_length(
                ' ', 9 - len(str('%.2f') % fac_base_12)) + '%.2f' % fac_base_12
            summary_base_12 = item_footer("", "*BASE %s: %s" %
                                          (procentaje_iva, aux_base_12)).getSymplify()

            aux_base_zero = repeat_to_length(
                ' ', 9 - len(str('%.2f') % fac_base_zero)) + '%.2f' % fac_base_zero
            summary_base_zero = item_footer("", "BASE   %s: %s" %
                                            ('0%', aux_base_zero)).getSymplify()

            aux_iva = repeat_to_length(
                ' ', 9 - len(str('%.2f') % fac_iva)) + '%.2f' % fac_iva
            summary_iva = item_footer("", "IVA   %s: %s" %
                                      (procentaje_iva, aux_iva)).getSymplify()

            aux_total = repeat_to_length(' ', 9 - len(str('%.2f') %
                                                      fac_total)) + '%.2f' % fac_total
            summary_total = item_footer(
                "", "TOT. FAC : %s" % aux_total).getSymplify()

            p.text(summary_subtotal)
            p.text(summary_descuento)
            p.text(summary_base_12)
            p.text(summary_base_zero)
            p.text(summary_iva)
            p.text(summary_total)

            # margen inferior ticket
            for x in range(1, footerMargin):
                p.text('\n')

            # Cut paper
            p.cut()

            return JsonResponse({
                'success': True,
                'copies': numberCopies,
                'file': ruta_binary,
            })


def repeat_to_length(s, wanted):
    return (s * (wanted // len(s) + 1))[:wanted]


class item_detail:

    def __init__(self, colCant, colProd, colCost, colTotal):
        self.colCant = colCant
        self.colProd = colProd
        self.colCost = colCost
        self.colTotal = colTotal

    def getSymplify(self):
        cantCols = 6
        produtCols = 18
        costCols = 6
        totalCols = 6

        qty = self.colCant.rjust(cantCols, ' ')  # produce "   Alien"
        if len(self.colProd) > produtCols:
            product = self.colProd[:produtCols]  # subtrae n caracteres
        else:
            product = self.colProd.ljust(produtCols, ' ')

        cost = self.colCost.rjust(costCols, ' ')
        total = self.colTotal.rjust(totalCols, ' ')

        cadena = qty + ' ' + product + ' ' + cost + ' ' + total + '\n'
        return cadena


class item_footer:

    def __init__(self, colA, colB):
        self.colA = colA
        self.colB = colB

    def getSymplify(self):
        rightCols = 13
        leftCols = 20

        left = self.colA.ljust(leftCols, ' ')
        right = self.colB.ljust(rightCols, ' ')

        return left + right + '\n'


# Clase para organizaar items EPSON LX-300
class item_epson_lx300:

    def __init__(self, cantidad="", detalle="", pvp="", total=""):
        self.cantidad = cantidad
        self.detalle = detalle
        self.pvp = pvp
        self.total = total

    def encode(self):
        cantidadCols = 11
        detalleCols = 50
        pvpCols = 12
        totalCols = 16

        qty = self.cantidad.rjust(cantidadCols, ' ')
        product = self.detalle[:detalleCols].ljust(detalleCols)
        # product = "XXXXXYYYYYZZZZZ XXXXXYYYYYZZZZZ XXXXXYYYYYZZZZZ  Z"
        pvp = self.pvp.rjust(pvpCols)
        total = self.total.rjust(totalCols)
        return (qty + '   ' + product + pvp + total + "\n").encode()


def tpv(request):
    from django.template import loader

    context = {}
    template = loader.get_template('venta/tpv.html')
    return HttpResponse(template.render(context, request))


def paymentListView(request):
    context = {}
    pagos = Factura.objects.none()
    if request.method == 'POST' and request.is_ajax():
        cliente_id = int(request.POST.get('cliente_id', 0))
        if cliente_id == 0:
            cliente_id = 1
        cliente = Cliente.objects.get(pk=cliente_id)

        monto = request.POST.get('monto')
        fecha_emision = request.POST.get('fecha_emision')

        # company = companys.get(id=ID)  # So we send the company instance
        # context['company'] = company
        # context['companys'] = companys
        return JsonResponse({
            'monto': monto,
            'cliente_id': cliente_id,
            'cliente': cliente.nombre,
            'fecha_emision': fecha_emision
        })
    else:
        return render(request, 'venta/payments.html', context)


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
            pago.tipo_flujo = 'D'
            ## pago.orden = 0
            # pago.numero_comprobante = post_num_fact
            pago.cliente_id = post_cliente_id
            pago.importe_recibido = post_importe_recibido
            pago.importe = post_importe
            ## pago.valor_retenido = 0
            pago.referencia = 'Venta'
            pago.save()

            return HttpResponse(
                json.dumps({"success": True}),
                content_type="application/json"
            )
