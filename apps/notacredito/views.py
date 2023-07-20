from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView, DeleteView

from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Sum, F, Q, Func

import datetime
from .models import NotaCredito

# raw sql
from django.db import connection

# Create your views here.


class IndexView(ListView):
    template_name = 'notacredito/index.html'

    def get_queryset(self):
        return NotaCredito.objects.none()


def ajax_listado_notascredito(request):
    from_date = request.POST.get("startDate")
    to_date = request.POST.get("endDate")
    format_str = '%Y-%m-%d'
    start_date = datetime.datetime.strptime(from_date, format_str)
    end_date = datetime.datetime.strptime(to_date, format_str)

    try:
        query = """
            select nota_credito_id, fecha_emision, c.nombre as cliente, sec.punto_establecimiento || '-' || sec.punto_emision || '-' || LPAD(numero_secuencia::text, 9, '0') as numero_comprobante, nce.nombre as estado, valor_total
            from notacredito_notacredito nc
            inner join cliente_cliente c on nc.cliente_id = c.cliente_id
            inner join notacredito_notacreditoestado nce on nc.estado_id = nce.notacredito_estado_id
            inner join administracion_secuencia sec on nc.secuencia_id = sec.secuencia_id
            where date(fecha_emision) >= '%s' and date(fecha_emision) <= '%s'
            order by fecha_emision desc
        """ % (start_date, end_date)
    except ValueError:
        # ningún almacén seleccionado
        id_aux = 0
        query = """
            select nota_credito_id, fecha_emision, c.nombre as cliente, sec.punto_establecimiento || '-' || sec.punto_emision || '-' || LPAD(numero_secuencia::text, 9, '0') as numero_comprobante, nce.nombre as estado, valor_total
            from notacredito_notacredito nc
            inner join cliente_cliente c on nc.cliente_id = c.cliente_id
            inner join notacredito_notacreditoestado nce on nc.estado_id = nce.notacredito_estado_id
            inner join administracion_secuencia sec on nc.secuencia_id = sec.secuencia_id
            where venta_factura.factura_id = %s
        """ % (id_aux)

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        results = []
        columns = (
            'nota_credito_id', 'fecha_emision', 'proveedor', 'numero_comprobante', 'periodo', 'anio', 'estado', 'valor_total'
        )
        for row in rows:
            results.append(dict(zip(columns, row)))
    return JsonResponse(results, safe=False)
