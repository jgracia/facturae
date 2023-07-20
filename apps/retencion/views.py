from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView, DeleteView
from django.db.models import Q
import json  # soporte Json

from .models import ComprobanteRetencion, ComprobanteRetencionDetalle
from apps.administracion.models import Secuencia
from apps.administracion.render import render_to_pdf
from apps.proveedor.models import Proveedor
from apps.sri.models import SriTipoImpuesto, SriTipoDocumento, \
    SriTipoComprobante, SriTipoMoneda
from apps.usuario.models import Turno
from apps.compra.models import OrdenCompra

from django.http import JsonResponse

import datetime
from pytz import timezone

# librerias para PDF
from django.http import HttpResponse
#from django.views.generic import View
from django.views import View

from django.conf import settings
import os

# raw sql
from django.db import connection

# Create your views here.


class RetencionesIndexView(ListView):
    template_name = 'retencion/listado_retenciones.html'

    def get_queryset(self):
        return ComprobanteRetencion.objects.none()


def ajax_listado_retenciones(request):
    from_date = request.POST.get("startDate")
    to_date = request.POST.get("endDate")
    format_str = '%Y-%m-%d'
    start_date = datetime.datetime.strptime(from_date, format_str)
    end_date = datetime.datetime.strptime(to_date, format_str)

    try:
        query = """
            select r.comprobante_retencion_id, fecha_emision, p.nombre as proveedor, sec.punto_establecimiento || '-' || sec.punto_emision || '-' || LPAD(numero_secuencia::text, 9, '0') as numero_comprobante, periodo, anio, re.nombre as estado, valor_total
            from retencion_comprobanteretencion r
            inner join proveedor_proveedor p on r.proveedor_id = p.proveedor_id
            inner join retencion_retencionestado re on r.estado_id = re.retencion_estado_id
            inner join administracion_secuencia sec on r.secuencia_id = sec.secuencia_id
            where date(fecha_emision) >= '%s' and date(fecha_emision) <= '%s'
            order by fecha_emision desc
        """ % (start_date, end_date)
    except ValueError:
        # ningún almacén seleccionado
        id_aux = 0
        query = """
            select r.comprobante_retencion_id, fecha_emision, p.nombre as proveedor, sec.punto_establecimiento || '-' || sec.punto_emision || '-' || LPAD(numero_secuencia::text, 9, '0') as numero_comprobante, periodo, anio, re.nombre as estado, valor_total
            from retencion_comprobanteretencion r
            inner join proveedor_proveedor p on r.proveedor_id = p.proveedor_id
            inner join retencion_retencionestado re on r.estado_id = re.retencion_estado_id
            inner join administracion_secuencia sec on r.secuencia_id = sec.secuencia_id
            where venta_factura.factura_id = %s
        """ % (id_aux)

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        results = []
        columns = (
            'comprobante_retencion_id', 'fecha_emision', 'proveedor', 'numero_comprobante', 'periodo', 'anio', 'estado', 'valor_total'
        )
        for row in rows:
            results.append(dict(zip(columns, row)))
    return JsonResponse(results, safe=False)


class CrearRetencion(ListView):
    context_object_name = 'retencion'
    template_name = 'retencion/retencion.html'
    success_url = reverse_lazy('retencion:listado_retenciones')

    def get_queryset(self):
        return ComprobanteRetencion.objects.filter(usuario_creador=self.request.user).order_by('pk')

    def get(self, *args, **kwargs):
        turno_obj = Turno.objects.filter(usuario_creador=self.request.user, activo=True)
        if turno_obj.exists():
            return super(CrearRetencion, self).get(*args, **kwargs)
        else:
            return redirect('contabilidad:mensaje_vista')

    def get_context_data(self, **kwargs):
        context = super(CrearRetencion, self).get_context_data(**kwargs)

        today = datetime.date.today()
        context['fecha_emision'] = format(today, '%Y-%m-%d')
        context['fecha_expira'] = format(today, '%Y-%m')

        proveedor_obj = Proveedor.objects.filter(activo=True).values(
            'proveedor_id', 'nombre').order_by('nombre')
        context['proveedores'] = proveedor_obj

        tipo_documento_obj = SriTipoDocumento.objects.all().values('codigo', 'descripcion')
        context['tipo_documentos'] = tipo_documento_obj

        return context


def guardar_retencion(request):
    if request.method == 'POST':
        data = request.POST.copy()
        proveedor_id = data.get('proveedor_id', default=None)
        compra_id = data.get('compra_id', default=0)
        fecha_emision = data.get('fecha_emision', default=None)
        mes = data.get('mes', default=None)
        anio = data.get('anio', default=None)
        total_retencion = data.get("total_retencion", default=None)
        tabla = data.get('pTableData', default=None)

        current_user = request.user
        company_id = request.session['company_id']
        #empresa_obj = current_user.perfil.empresa
        proveedor_obj = Proveedor.objects.get(pk=proveedor_id)

        # obtener codigo de secuencia
        sri_tipo_moneda_obj = SriTipoMoneda.objects.filter(codigo='DOLAR')[0]
        tipo_comprobante_obj = SriTipoComprobante.objects.filter(codigo='07')[0]
        secuencia_obj = Secuencia.objects.filter(
            empresa_id=company_id, sri_tipo_comprobante=tipo_comprobante_obj)[0]
        ultima_secuencia = secuencia_obj.ultima_secuencia
        secuencia_obj.ultima_secuencia += 1
        secuencia_obj.save()

        comprobante = ComprobanteRetencion()
        comprobante.empresa_id = company_id
        comprobante.proveedor = proveedor_obj
        comprobante.compra_id = compra_id
        comprobante.secuencia = secuencia_obj
        comprobante.sri_tipo_comprobante = tipo_comprobante_obj
        comprobante.sri_tipo_moneda = sri_tipo_moneda_obj
        comprobante.usuario_creador = current_user
        # comprobante.created_at =
        # comprobante.update_at =
        comprobante.estado_id = '1'  # COMPROBANTE CREADO

        currentDT = datetime.datetime.now()

        #comprobante.fecha_emision = fecha_emision + ' ' + currentDT.strftime("%H:%M:%S")
        dt_obj = datetime.datetime.now()
        hora = dt_obj.strftime("%H:%M:%S")
        datetime_obj = datetime.datetime.strptime(
            '%s %s' % (fecha_emision, hora), "%Y-%m-%d %H:%M:%S")
        datetime_obj_utc = datetime_obj.replace(tzinfo=timezone('UTC'))

        comprobante.fecha_emision = datetime_obj_utc
        comprobante.numero_secuencia = ultima_secuencia
        comprobante.clave_acceso = format(datetime.datetime.now())
        # comprobante.numero_autorizacion =
        # comprobante.fecha_autorizacion =
        comprobante.periodo = mes
        comprobante.anio = anio
        comprobante.valor_total = total_retencion
        # comprobante.archivo_generado =
        # comprobante.archivo_autorizado =
        # comprobante.fecha_error =
        # comprobante.archivo_error =
        comprobante.save()

        guardarRetencionDetalle(comprobante, tabla)

        return JsonResponse({
            'success': True,
        })


def guardarRetencionDetalle(comprobante, tabla):
    # JSON to Dict
    json_data = json.loads(tabla)
    for key in json_data:
        sri_tipo_impuesto_obj = SriTipoImpuesto.objects.filter(codigo=key["cod_reten"])[0]
        sri_tipo_comprobante_modificado_obj = SriTipoComprobante.objects.filter(codigo=key["tipo_doc"])[
            0]

        ret_det = ComprobanteRetencionDetalle()
        ret_det.retencion = comprobante
        ret_det.sri_tipo_comprobante_modificado = sri_tipo_comprobante_modificado_obj
        ret_det.sri_tipo_impuesto = sri_tipo_impuesto_obj
        # ret_det.created_at =
        # ret_det.update_at =
        ret_det.fecha_emision_documento_modificado = key["fecha_comp_modifica"]
        ret_det.numero_documento_modificado = key["documento"]
        ret_det.tipo_impuesto = key["tipo_imp"]
        ret_det.valor_base_imponible = key["base_imponible"]
        ret_det.valor_total = key["valor_retenido"]
        ret_det.save()

    return True


def load_comprobantes(request):
    proveedor_id = request.GET.get('proveedor_id', default=None)
    comprobantes = OrdenCompra.objects.filter(
        comprobanteretencion__isnull=True,
        proveedor_id=proveedor_id).values('orden_id', 'numero_comprobante', 'fecha_emision').order_by('-fecha_emision')[:5]
    return render(request, 'retencion/comprobante_dropdown_list_options.html', {'comprobantes': comprobantes})


def get_baseimponible(request):
    orden_id = request.GET.get('orden_id', default=0)
    orden_obj = OrdenCompra.objects.get(pk=orden_id)
    return JsonResponse({
        'valor_total': orden_obj.valor_total,
        'fecha_emision': orden_obj.fecha_emision
    })


def load_impuesto(request):
    tipo_impuesto_id = request.GET.get('impuesto')
    impuestos = SriTipoImpuesto.objects.filter(tipo_impuesto=tipo_impuesto_id).values(
        'codigo', 'descripcion').order_by('codigo')
    return render(request, 'retencion/impuesto_dropdown_list_options.html', {'impuestos': impuestos})


def get_porcentaje(request):
    tipo_impuesto_codigo = request.GET.get('impuesto')
    tipo_impuesto_obj = SriTipoImpuesto.objects.filter(codigo=tipo_impuesto_codigo)[0]
    if not tipo_impuesto_obj:
        porcentaje = 0
    else:
        porcentaje = round(tipo_impuesto_obj.porcentaje, 2)

    return JsonResponse({
        'porcentaje': porcentaje,
    })

    """if request.method == "GET":
        if request.is_ajax():
            tipo_impuesto_codigo = request.GET.get('impuesto', None)
            porcentaje = round(SriTipoImpuesto.objects.filter(codigo=tipo_impuesto_codigo)[0].porcentaje)
            #return JsonResponse(lista_productos, safe=False)
            return JsonResponse({
                'data': tipo_impuesto_codigo,
            })"""


class GeneratePDF(View):
    def get(self, request, *args, **kwargs):
        retencion_id = request.GET.get('data', None)
        if retencion_id is None:
            retencion_id = kwargs.get("pk")

        retencion_obj = ComprobanteRetencion.objects.get(pk=retencion_id)
        items = ComprobanteRetencionDetalle.objects.filter(retencion_id=retencion_id).only(
            'valor_base_imponible', 'tipo_impuesto', 'sri_tipo_impuesto', 'valor_total')

        #from django.contrib.sites.shortcuts import get_current_site
        #dominio = get_current_site(request).domain
        #ruta = '/media/pixmaps/%s_factura.jpg' % (factura_obj.empresa.ruc)
        #url_filigrana = 'http://{domain}{path}'.format(domain=dominio, path=ruta)

        ruta = '/media/pixmaps/%s_retencion.jpg' % (retencion_obj.empresa.ruc)
        url_filigrana = "{0}://{1}{2}".format(request.scheme, request.get_host(), ruta)

        params = {
            # 'orden_id': factura_id,
            # 'cliente_nombre': factura_obj.cliente.nombre,
            # 'cliente_direccion': factura_obj.cliente.direccion,
            # 'cliente_telefono': factura_obj.cliente.telefono,
            'tipo_comprobante': "RETENCIÓN",
            'tipo_comprobante_venta': "FACTURA",
            'retencion': retencion_obj,
            'items': items,
            'plantilla_url': url_filigrana
            # 'plantilla_url': 'media/pixmaps/%s_factura.jpg' % (factura_obj.empresa.ruc)
        }

        #html = template.render(context)
        pdf = render_to_pdf('pdf/retencion.html', params)
        destination = 'pdf/%s_retencion.html' % (retencion_obj.empresa.ruc)
        if os.path.isfile(destination):
            pdf = render_to_pdf('pdf/%s_retencion.html' % (retencion_obj.empresa.ruc), params)

        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "retencion_%s.pdf" % (retencion_id)
            content = "inline; filename=%s" % (filename)
            download = request.GET.get("download")
            if download:
                content = "attachment; filename=%s" % (filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Error Rendering PDF", status=400)


class EliminarRetencion(DeleteView):
    model = ComprobanteRetencion
    template_name = 'retencion/eliminar_retencion.html'
    success_url = reverse_lazy('retencion:listado_retenciones')
