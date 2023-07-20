from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse

from django.contrib.auth.decorators import login_required


from apps.administracion.models import Empresa
from apps.contabilidad.models import Pago
from apps.notaentrega.models import NotaEntrega
from apps.notadebito.models import NotaDebito
from apps.notacredito.models import NotaCredito
from apps.contabilidad.models import AsientoContable

# estadisticas
import calendar
import datetime
from django.db.models import Count, Sum
from django.db.models.functions import Coalesce

# raw sql
from django.db import connection

# gráfico
from django.http import JsonResponse

# Create your views here.


def index(request):
    context = {}
    if request.user.is_authenticated:
        # Do something for authenticated users.
        try:
            c = Empresa.objects.order_by('empresa_id')[0]
            request.session['company_id'] = c.empresa_id
            request.session['company_name'] = c.nombre_comercial
        except IndexError:
            # c = None
            request.session['company_id'] = 0

        current_company_id = request.session['company_id']
        # mejores vendedores
        try:
            query = """
                select u.id, u.username, concat(u.first_name, ' ', u.last_name) as fullname, sum(f.valor_total) as total_ventas, count(f.factura_id) as numero_ventas
                from auth_user u
                inner join venta_factura f on f.usuario_creador_id = u.id
                where f.empresa_id = '%s'
                group by u.id, u.username
                order by total_ventas desc
                limit 5
            """ % (current_company_id)
        except ValueError:
            # ningún almacén seleccionado
            id_aux = 0
            query = """
                select u.id, u.username, concat(u.first_name, ' ', u.last_name) as fullname, sum(f.valor_total) as total_ventas, count(f.factura_id) as numero_ventas
                from auth_user u
                inner join venta_factura f on f.usuario_creador_id = u.id
                where f.empresa_id = '%s'
                group by u.id, u.username
                order by total_ventas desc
                limit 5
            """ % (id_aux)

        with connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            top_employees = []
            columns = (
                'id', 'username', 'fullname', 'total_ventas', 'numero_ventas'
            )
            for row in rows:
                top_employees.append(dict(zip(columns, row)))

        context['top_employees'] = top_employees

        today = datetime.date.today()
        context['total_sales_today'] = Pago.objects.filter(
            created_at__date=today,
            referencia='Venta').aggregate(
            total=Coalesce(Sum('importe'), 0))['total']

        start_week = today - datetime.timedelta(today.weekday())
        end_week = start_week + datetime.timedelta(7)
        context['total_sales_week'] = Pago.objects.filter(
            created_at__date__range=[start_week, end_week],
            referencia='Venta').aggregate(
            total=Coalesce(Sum('importe'), 0))['total']

        #start_of_month = datetime.date.today().replace(day=1)
        #last_day_of_month = calendar.monthrange(today.year, today.month)[1]
        #end_of_month = datetime.date.today().replace(day=last_day_of_month)

        current_month = today.month
        current_year = today.year
        context['total_sales_month'] = Pago.objects.filter(
            created_at__month=current_month, created_at__year=current_year).aggregate(
            total=Coalesce(Sum('importe'), 0))['total']

        template = loader.get_template('dashboard/home.html')
        return HttpResponse(template.render(context, request))
    else:
        template = loader.get_template('dashboard/index.html')
        return HttpResponse(template.render(context, request))


"""
@login_required
def home(request):
    context = {}
    template = loader.get_template('dashboard/home.html')
    return HttpResponse(template.render(context, request))
"""


def contact_us(request):
    context = {}
    template = loader.get_template('dashboard/contact_us.html')
    return HttpResponse(template.render(context, request))


def about_us(request):
    context = {}
    template = loader.get_template('dashboard/about_us.html')
    return HttpResponse(template.render(context, request))


def portfolio(request):
    context = {}
    template = loader.get_template('dashboard/portfolio.html')
    return HttpResponse(template.render(context, request))


def services(request):
    context = {}
    template = loader.get_template('dashboard/services.html')
    return HttpResponse(template.render(context, request))


def get_grafico_dashboard(request):
    if request.method == 'GET':
        from_date = request.GET.get("startDate")  # 2019-07-28
        to_date = request.GET.get("endDate")  # 2019-08-26
        #format_str = '%Y-%m-%d'
        try:
            query = """
                select TO_CHAR(created_at::date, 'TMMon DD') AS fecha,
                       round(sum(case when referencia = 'Venta' then importe else 0 end), 2) AS venta,
                       round(sum(case when referencia = 'Compra' then importe else 0 end), 2) AS compra
                from contabilidad_Pago
                where date(created_at) >= '%s' and date(created_at) <= '%s'
                group by created_at::date;
            """ % (from_date, to_date)
        except ValueError:
            # ningún almacén seleccionado
            query = """
                select TO_CHAR(created_at::date, 'TMMon DD') AS start_date,
                       created_at::date + 1 AS end_date,
                       sum(case when referencia = 'Venta' then importe else 0 end) AS venta,
                       sum(case when referencia = 'Compra' then importe else 0 end) AS compra,
                       sum(importe) AS revenue
                from contabilidad_Pago
                where date(created_at) >= '%s' and date(created_at) <= '%s'
                group by created_at::date;
            """ % (from_date, to_date)

        with connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            results = []
            columns = (
                'fecha', 'venta', 'compra'
            )
            for row in rows:
                results.append(dict(zip(columns, row)))

        total_purchases = Pago.objects.filter(
            referencia='Compra',
            created_at__date__range=(from_date, to_date)).aggregate(
            total=Coalesce(Count('id'), 0))['total']

        total_sales = Pago.objects.filter(
            referencia='Venta',
            created_at__date__range=(from_date, to_date)).aggregate(
            total=Coalesce(Count('id'), 0))['total']

        total_delivery_notes = NotaEntrega.objects.filter(
            created_at__date__range=(from_date, to_date)).aggregate(
            total=Coalesce(Count('nota_entrega_id'), 0))['total']

        total_debit_notes = NotaDebito.objects.filter(
            created_at__date__range=(from_date, to_date)).aggregate(
            total=Coalesce(Count('nota_debito_id'), 0))['total']

        total_credit_notes = NotaCredito.objects.filter(
            created_at__date__range=(from_date, to_date)).aggregate(
            total=Coalesce(Count('nota_credito_id'), 0))['total']

        total_accounting_entry = AsientoContable.objects.filter(
            fecha__range=(from_date, to_date)).aggregate(
            total=Coalesce(Count('id'), 0))['total']

        # return JsonResponse(results, safe=False)
        return JsonResponse({
            'success': True,
            'results': results,
            'total_purchases': total_purchases,
            'total_sales': total_sales,
            'total_delivery_notes': total_delivery_notes,
            'total_debit_notes': total_debit_notes,
            'total_credit_notes': total_credit_notes,
            'total_accounting_entry': total_accounting_entry
        })
