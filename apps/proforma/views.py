from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView

from django.urls import reverse_lazy
from django.http import JsonResponse

import datetime
from datetime import timedelta
from django.db.models import Sum

from .models import Proforma, ProformaEstado, ProformaDetalle
from apps.cesta.models import Cesta, Item as CestaItem, Lote as CestaLote
from apps.usuario.models import Turno
from apps.cliente.models import Cliente
from apps.cliente.forms import ClienteForm
from apps.administracion import utils
from apps.administracion.models import EntidadFinanciera, \
    TarjetaBancaria, Secuencia

from apps.sri.models import SriTarifaIVA, SriTipoComprobante
from apps.unidadmedida.models import UnidadMedida
from apps.producto.models import Producto
from apps.almacen.models import Almacen, Kardex, ProductoSaldo, ControlProducto
from apps.servicio.models import Servicio

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
    carrito = CarritoProforma.objects.filter(usuario=usuario_actual)
    # return carrito.count()
    return len(carrito)


def getSubtotalCarrito(usuario_actual):
    total = CarritoProforma.objects.filter(usuario=usuario_actual).aggregate(
        total=Sum('valor_subtotal_sin_impuesto'))['total']
    if not total:
        return 0
    return total


def getSubtotalImptoCarrito(usuario_actual):
    total = CarritoProforma.objects.filter(usuario=usuario_actual).aggregate(
        total=Sum('valor_subtotal_12'))['total']
    if not total:
        return 0
    return total


def getSubtotalZeroCarrito(usuario_actual):
    total = CarritoProforma.objects.filter(usuario=usuario_actual).aggregate(
        total=Sum('valor_subtotal_0'))['total']
    if not total:
        return 0
    return total


def getDescuentoZeroCarrito(usuario_actual):
    # Less than or equal:
    # User.objects.filter(userprofile__level__lte=0)

    # Greater than or equal
    # User.objects.filter(userprofile__level__gte=0)

    descuento = CarritoProforma.objects.filter(usuario=usuario_actual, valor_subtotal_0__level__gte=0).aggregate(
        descuento=Sum('valor_descuento'))['descuento']
    if not descuento:
        return 0
    return descuento


def getDescuentoImptoCarrito(usuario_actual):
    descuento = CarritoProforma.objects.filter(usuario=usuario_actual, valor_subtotal_12__level__gte=0).aggregate(
        descuento=Sum('valor_descuento'))['descuento']
    if not descuento:
        return 0
    return descuento


def getValorDescuentoCarrito(usuario_actual):
    total = CarritoProforma.objects.filter(usuario=usuario_actual).aggregate(
        descuento=Sum('valor_descuento'))['descuento']
    if not total:
        return 0
    return total


def getValorIvaCarrito(usuario_actual):
    total = CarritoProforma.objects.filter(
        usuario=usuario_actual).aggregate(total=Sum('valor_iva'))['total']
    if not total:
        return 0
    return total


def getValorTotalCarrito(usuario_actual):
    total = CarritoProforma.objects.filter(
        usuario=usuario_actual).aggregate(total=Sum('valor_total'))['total']
    if not total:
        return 0
    return total
'''

""" FUNCIONES CALCULO INVENTARIO """


'''
def getExistencia(producto_obj):
    saldo_obj = ProductoSaldo.objects.filter(producto=producto_obj)
    if saldo_obj.exists():
        return saldo_obj[0].existencia
    else:
        return 0

'''
""" FUNCIONES PROFORMAS """


"""class ListadoProformas(ListView):
    #model = Proforma

    template_name = 'proforma/listado_proformas.html'
    context_object_name = 'all_proformas'

    def get_queryset(self):
        queryset_list = Proforma.objects.only('fecha_emision', 'cliente', 'secuencia', 'estado', 'valor_total').order_by('-fecha_emision')
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

        return queryset_list"""


class ListadoProformas(ListView):
    template_name = 'proforma/listado_proformas.html'

    def get_queryset(self):
        return Proforma.objects.none()


def ajax_listado_proformas(request):
    from_date = request.POST.get("startDate")
    to_date = request.POST.get("endDate")
    format_str = '%Y-%m-%d'
    start_date = datetime.datetime.strptime(from_date, format_str)
    end_date = datetime.datetime.strptime(to_date, format_str) + datetime.timedelta(days=1)

    try:
        query = """
            select proforma_id, fecha_emision, c.nombre as cliente, sec.punto_establecimiento || '-' || sec.punto_emision || '-' || LPAD(numero_secuencia::text, 9, '0') as numero_comprobante, pe.nombre as estado, valor_total
            from proforma_proforma p
            inner join cliente_cliente c on p.cliente_id = c.cliente_id
            inner join proforma_proformaestado pe on p.estado_id = pe.proforma_estado_id
            inner join administracion_secuencia sec on sec.secuencia_id = p.secuencia_id
            where date(p.fecha_emision) between '%s' and '%s'
            order by p.fecha_emision desc
        """ % (start_date, end_date)
    except ValueError:
        # ningún almacén seleccionado
        id_aux = 0
        query = """
            select proforma_id, fecha_emision, c.nombre as cliente, sec.punto_establecimiento || '-' || sec.punto_emision || '-' || LPAD(numero_secuencia::text, 9, '0') as numero_comprobante, pe.nombre as estado, valor_total
            from proforma_proforma p
            inner join cliente_cliente c on p.cliente_id = c.cliente_id
            inner join proforma_proformaestado pe on p.estado_id = pe.proforma_estado_id
            inner join administracion_secuencia sec on sec.secuencia_id = p.secuencia_id
            where p.proforma_id = %s
        """ % (id_aux)

    print(query)
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = (
            'proforma_id', 'fecha_emision', 'cliente', 'numero_comprobante', 'estado', 'valor_total'
        )

        results = []
        for row in rows:
            results.append(dict(zip(columns, row)))
    return JsonResponse(results, safe=False)


class CrearProforma(ListView):
    context_object_name = 'proforma'
    template_name = 'proforma/proforma.html'
    success_url = reverse_lazy('proforma:listado_proformas')

    def get_queryset(self):
        return Proforma.objects.none()

    # def multiply(value, arg):
    #    return value*arg

    def get(self, *args, **kwargs):
        turno_obj = Turno.objects.filter(usuario_creador=self.request.user, activo=True)
        if turno_obj.exists():
            return super(CrearProforma, self).get(*args, **kwargs)
        else:
            return redirect('contabilidad:mensaje_vista')

    def get_context_data(self, **kwargs):
        context = super(CrearProforma, self).get_context_data(**kwargs)
        context['tarifa'] = round(SriTarifaIVA.objects.filter(codigo='2')[0].porcentaje)

        today = datetime.date.today()
        context['fecha_emision'] = format(today, '%Y-%m-%d')
        context['fecha_expira'] = format(today + timedelta(days=8), '%Y-%m-%d')

        unidad_obj = UnidadMedida.objects.all()
        context['unidades'] = unidad_obj

        unidad_servicio_obj = UnidadMedida.objects.values('abreviatura')
        context['unidades_servicio'] = unidad_servicio_obj

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
        usuario=request.user, clave_apli='CART-PROFORMA', empresa_id=empresa_id)

    # verifica items por factura
    filasEnCarrito = user_basket.obtener_total_filas()

    #filasPorFactura = current_user.perfil.empresa.factura_total_filas
    company_id = request.session['company_id']
    secuencia_obj = Secuencia.objects.filter(
        empresa_id=company_id, sri_tipo_comprobante__codigo='102')[0]
    if not secuencia_obj:
        return JsonResponse({
            'success': False,
            'message': "Secuencia incorrecta.",
        })
    filasPorProforma = secuencia_obj.comprobante_total_filas

    if (filasEnCarrito < filasPorProforma):
        # verifica codigo (bien o servicio)
        cadena_buscada = 'SRV-'
        # Si la sub-cadena no está presente el programa imprimirá el valor -1
        posicion_coincidencia = dataId.find(cadena_buscada)

        if (posicion_coincidencia == -1):
            # agregar productos
            productoId = dataId

            producto_obj = Producto.objects.get(pk=productoId)
            # new code
            almacen_obj = Almacen.objects.filter(es_principal=True, empresa_id=company_id)[0]
            control_producto = ControlProducto.objects.filter(
                producto=producto_obj, almacen=almacen_obj)
            if control_producto.exists():
                existencia = control_producto[0].stock
            else:
                existencia = 0

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

                #Post.objects.create(author=me, title='Sample title', text='Test')
                markup = "<tr>" \
                    "<td style='display:none;'>" + str(cesta_item.pk) + "</td>" \
                    "<td data-title='Descripción'><a href=/inventario/detalle_producto/" + str(productoId) + " target='_blank'>" + producto_obj.nombre + "</a></td>" \
                    "<td data-title='Cantidad' class='numeric'>" + str(locale.format('%.2f', cantidad)) + "</td>" \
                    "<td data-title='Und'>" + producto_obj.unidad_principal.abreviatura + "</td>" \
                    "<td data-title='Precio' class='numeric'>" + str(locale.currency(precio)) + "</td>" \
                    "<td data-title='Total' class='numeric'>" + str(locale.currency(cantidad * precio)) + "</td>" \
                    "<td data-title='Acciones' class='text-center'>" \
                    "<div class='btn-group btn-group-sm'>" \
                    "<button type='button' data-id=" + str(cesta_item.pk) + " class='btn btn-primary editButton'><i class='fas fa-edit'></i></button>" \
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
                "<td data-title='Und'>" + servicio_obj.unidad_medida.abreviatura + "</td>" \
                "<td data-title='Precio' class='numeric'>" + str(locale.currency(precio)) + "</td>" \
                "<td data-title='Total' class='numeric'>" + str(locale.currency(qty * precio)) + "</td>" \
                "<td data-title='Acciones' class='text-center'>" \
                "<div class='btn-group btn-group-sm'>" \
                "<button type='button' data-id=" + 'SRV-' + str(cesta_item.pk) + " class='btn btn-primary editButton'><i class='fas fa-edit'></button>" \
                "</div>" \
                "&nbsp;" \
                "<div class='btn-group btn-group-sm'>" \
                "<button type='button' data-id=" + 'SRV-' + str(cesta_item.pk) + " class='btn btn-warning deleteButton'><i class='fas fa-trash'></button>" \
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
            'message': "Ha superado el número de líneas por proforma.",
            'totalFilas': 0,
        })


def ajaxAgregarItemSinExistencia(request):
    productoId = request.GET.get('dataId', None)

    # verifica items por factura
    empresa_id = request.session['company_id']
    user_basket, status = Cesta.objects.get_or_create(
        usuario=request.user, clave_apli='CART-PROFORMA', empresa_id=empresa_id)

    filasEnCarrito = user_basket.obtener_total_filas()

    #filasPorFactura = current_user.perfil.empresa.factura_total_filas
    company_id = request.session['company_id']
    secuencia_obj = Secuencia.objects.filter(
        empresa_id=company_id, sri_tipo_comprobante__codigo='102')[0]
    if not secuencia_obj:
        return JsonResponse({
            'success': False,
            'message': "Secuencia incorrecta.",
        })
    filasPorProforma = secuencia_obj.comprobante_total_filas

    if (filasEnCarrito < filasPorProforma):
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
            porcentaje_descuento = producto_obj.descuento_tres
        else:
            precio = producto_obj.precio_cuatro
            porcentaje_descuento = producto_obj.descuento_cuatro

        # calculos item
        subtotal_linea = float(cantidad * precio)
        valor_descuento_linea = round((subtotal_linea * float(porcentaje_descuento)) / 100, 5)

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
            "<td data-title='Descripción'><a href=/inventario/detalle_producto/" + str(productoId) + " target='_blank'>" + producto_obj.nombre + "</a></td>" \
            "<td data-title='Cantidad' class='numeric'>" + str(locale.format('%.2f', cantidad)) + "</td>" \
            "<td data-title='Und'>" + producto_obj.unidad_principal.abreviatura + "</td>" \
            "<td data-title='Precio' class='numeric'>" + str(locale.currency(precio)) + "</td>" \
            "<td data-title='Total' class='numeric'>" + str(locale.currency(cantidad * precio)) + "</td>" \
            "<td data-title='Acciones' class='text-center'>" \
            "<div class='btn-group btn-group-sm'>" \
            "<button type='button' data-id=" + str(cesta_item.pk) + " class='btn btn-primary editButton'><i class='fas fa-edit'></i></button>" \
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
        cantidad = locale.atof(data.get('qty', 1))
        unidad = data.get('unit')
        precio = locale.atof(data.get('price', 0))
        porcentaje_descuento = locale.atof(data.get('discount', 0))

        empresa_id = request.session['company_id']
        user_basket = Cesta.objects.filter(
            usuario=request.user, clave_apli='CART-PROFORMA', empresa_id=empresa_id)[0]

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

            if (existencia > 0) and (cantidad <= existencia):

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
            unit_service_obj = UnidadMedida.objects.filter(abreviatura=unidad)[0]
            cesta_item = CestaItem.objects.get(pk=item_id)

            # calculos
            subtotal_linea = float(cantidad) * float(precio)
            valor_descuento_linea = round((subtotal_linea * float(porcentaje_descuento)) / 100, 5)

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
            porcentaje_descuento = float(request.POST.get('exchange_discount_percent', 0))

            # buscar registro en Carrito
            unit_obj = UnidadMedida.objects.filter(abreviatura=unidad)[0]
            cesta_item = CestaItem.objects.get(pk=itemID)

            # calculos linea
            subtotal_linea = float(cantidad) * float(precio)
            valor_descuento_linea = round((subtotal_linea * float(porcentaje_descuento)) / 100, 5)

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
            cesta_item.unidad = unit_obj
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
                usuario=request.user, clave_apli='CART-PROFORMA', empresa_id=empresa_id)[0]

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
                usuario=request.user, clave_apli='CART-PROFORMA', empresa_id=empresa_id)[0]
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


def guardarProforma(request):
    if request.method == 'POST':
        # recibe datos del formulario modal 'paymentForm'
        data = request.POST.copy()
        cliente_id = data.get('cliente_id', default=None)
        fecha_emision = data.get('fecha_emision', default=None)
        fecha_vencimiento = data.get('fecha_vencimiento', default=None)

        #today = datetime.date.today()
        current_user = request.user
        #empresa_obj = current_user.perfil.empresa
        cliente_obj = Cliente.objects.get(pk=cliente_id)

        # obtener codigo de secuencia
        tipo_comprobante_obj = SriTipoComprobante.objects.filter(codigo='102')[0]
        company_id = request.session['company_id']
        secuencia_obj = Secuencia.objects.filter(
            empresa_id=company_id, sri_tipo_comprobante=tipo_comprobante_obj)[0]
        ultima_secuencia = secuencia_obj.ultima_secuencia
        secuencia_obj.ultima_secuencia += 1
        secuencia_obj.save()

        estado_obj = ProformaEstado.objects.filter(nombre='EMITIDA')[0]

        # calculo resumen
        empresa_id = request.session['company_id']
        user_basket = Cesta.objects.filter(
            usuario=request.user, clave_apli='CART-PROFORMA', empresa_id=empresa_id)[0]

        subtotal = user_basket.obtener_sub_total()
        valor_descuento = user_basket.obtener_total_descuento()
        valor_base_imponible = user_basket.obtener_base_imponible()
        valor_tarifa_cero = user_basket.obtener_total_tarifa_cero()
        valor_iva = user_basket.obtener_total_iva()
        valor_total = user_basket.obtener_gran_total()

        # guardar proforma
        prof = Proforma()
        prof.empresa_id = company_id
        prof.cliente = cliente_obj
        prof.usuario_creador = current_user
        prof.estado = estado_obj
        prof.secuencia = secuencia_obj
        prof.sri_tipo_comprobante = tipo_comprobante_obj
        currentDT = datetime.datetime.now()
        prof.fecha_emision = fecha_emision + ' ' + currentDT.strftime("%H:%M:%S")
        prof.fecha_validez = fecha_vencimiento
        prof.numero_secuencia = ultima_secuencia
        prof.valor_descuento = valor_descuento
        prof.valor_subtotal_sin_impuesto = subtotal
        prof.valor_subtotal_12 = valor_base_imponible
        prof.valor_subtotal_0 = valor_tarifa_cero
        #fact.valor_subtotal_no_objeto_iva = 0
        #fact.valor_subtotal_exento = 0
        #fact.valor_base_imponible_ibrpnr = 0
        #fact.valor_subtotal_ibrpnr = 0
        prof.valor_ice = 0
        prof.valor_iva = valor_iva
        #fact.valor_propina = 0
        prof.valor_total = valor_total
        prof.save()

        guardarOrdenDetalle(prof, user_basket)

        # vaciar cesta de proformas
        user_basket.vaciar_cesta()

        return JsonResponse({
            'success': True,
            'proformaId': prof.pk,
        })


def guardarOrdenDetalle(prof, user_basket):
    # guardar carrito en detalle de facturas
    items = user_basket.obtener_items()

    for item in items:
        prof_det = ProformaDetalle()
        prof_det.proforma = prof
        if item.tipo == 'PROD':  # producto
            prof_det.tipo = 'P'
            prof_det.producto = item.producto
        else:
            prof_det.tipo = 'S'
            prof_det.servicio = item.servicio
        prof_det.cantidad = item.cantidad
        prof_det.unidad = item.unidad_medida
        prof_det.precio_venta = item.precio
        prof_det.porcentaje_descuento = item.porcentaje_descuento
        prof_det.valor_descuento = item.valor_descuento
        prof_det.valor_subtotal_sin_impuesto = item.valor_subtotal_sin_impuesto
        prof_det.valor_subtotal_12 = item.valor_subtotal_12
        prof_det.valor_subtotal_0 = item.valor_subtotal_0
        prof_det.valor_subtotal_no_objeto_iva = item.valor_subtotal_no_objeto_iva
        prof_det.valor_subtotal_exento = item.valor_subtotal_exento
        prof_det.valor_base_imponible_ibrpnr = item.valor_base_imponible_ibrpnr
        prof_det.valor_subtotal_ibrpnr = item.valor_subtotal_ibrpnr
        prof_det.valor_ice = item.valor_ice
        prof_det.valor_iva = item.valor_iva
        prof_det.valor_total = item.valor_total
        prof_det.save()

    return True


""" FORMULARIO MODAL CLIENTE """


class CrearClienteModal(CreateView):
    template_name = 'frontend/modals/cliente_modal.html'
    form_class = ClienteForm
    success_url = reverse_lazy('proforma:crear_proforma')

    def form_valid(self, form):
        cliente = form.save(commit=False)
        cliente.usuario_creador = self.request.user
        cliente.save()
        return super(CrearClienteModal, self).form_valid(form)


class EliminarProforma(DeleteView):
    model = Proforma
    template_name = 'proforma/eliminar_proforma.html'
    success_url = reverse_lazy('proforma:listado_proformas')


class GeneratePDF(View):
    def get(self, request, *args, **kwargs):
        proforma_id = request.GET.get('data', None)
        if proforma_id is None:
            proforma_id = kwargs.get("pk")

        proforma_obj = Proforma.objects.get(pk=proforma_id)
        items = ProformaDetalle.objects.filter(proforma_id=proforma_id)

        ruta = '/media/pixmaps/%s_proforma.jpg' % (proforma_obj.empresa.ruc)
        url_filigrana = "{0}://{1}{2}".format(request.scheme, request.get_host(), ruta)

        params = {
            'tipo_comprobante': "PROFORMA",
            'proforma': proforma_obj,
            'items': items,
            'plantilla_url': url_filigrana
        }

        pdf = render_to_pdf('pdf/proforma.html', params)
        ruta_destination = 'templates/pdf/%s_proforma.html' % (proforma_obj.empresa.ruc)
        destination = os.path.join(os.path.dirname(__file__), ruta_destination)

        if os.path.isfile(destination):
            pdf = render_to_pdf('pdf/%s_proforma.html' % (proforma_obj.empresa.ruc), params)

        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "proforma_%s.pdf" % (proforma_id)
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


class PlantillaProforma(DetailView):
    model = Proforma
    template_name = 'impresion/prueba.html'
