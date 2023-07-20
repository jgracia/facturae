from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.db.models import Sum, Q
from django.urls import reverse_lazy

from django.http import JsonResponse
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView, DeleteView

from bootstrap_modal_forms.generic import (BSModalCreateView,
                                           BSModalUpdateView,
                                           BSModalReadView,
                                           BSModalDeleteView)

from apps.administracion import utils
from apps.sri.models import SriFormaPago, SriTipoMoneda
from apps.usuario.models import Turno
from apps.compra.models import OrdenCompra
from apps.venta.models import Factura
from apps.retencion.models import ComprobanteRetencion, ComprobanteRetencionDetalle
from .models import Pago, PagoCheque, \
    FormaPago, EstadoPago, PagoCredito, PeriodoContable, PlanCuenta, \
    AsientoContable, AsientoDebeDetalle, AsientoHaberDetalle, \
    AsientoAutomatico, AsientoParcialDetalle, BalanceComprobacion
from .forms import PeriodoContableForm, CrearTurnoForm, PlanCuentaForm, \
    AsientoAutomaticoForm
from .Payment import Payment

import os
import datetime
from datetime import timedelta
from enum import Enum
from decimal import Decimal

# imprimir escpos
# from escpos import *
from escpos import printer
from escpos.printer import Usb

from django.core import serializers
from django.http import HttpResponse
import json
from django.db.models import Max
from django.db.models.functions import Coalesce

from django.shortcuts import render, get_object_or_404, redirect
# from apps.contabilidad.forms import SelectionForm
# from apps.contabilidad.models import Selection

# raw sql
from django.db import connection
from django.http import HttpResponseRedirect
from django.db import transaction

# read excel
import xlrd
from os import path

# librerias para PDF
from apps.administracion.models import Empresa
from apps.administracion.render import render_to_pdf
from django.views.generic import View
from django.utils import timezone

# export data
import xlwt  # libreria para exportar a excel


# Create your views here.

"""class ListadoTurnos(ListView):
    template_name = 'contabilidad/turnos/listado_turnos.html'

    def get_queryset(self):
        return Turno.objects.none()"""


def message_view(request):
    turno_obj = Turno.objects.filter(usuario_creador=request.user, activo=True)
    if turno_obj.exists():
        return render(request, 'contabilidad/mensajes/message.html', {'activo': True})
    else:
        return render(request, 'contabilidad/mensajes/message.html', {'activo': False})


class ListadoTurnos(ListView):
    model = Turno
    template_name = 'contabilidad/turnos/listado_turnos.html'

    def get_queryset(self):
        query = self.request.GET.get("range")

        current_company_id = self.request.session['company_id']
        # empresa_obj = Empresa.objects.get(pk=current_company_id)

        if query:
            from_date = query[0:10] + ' 00:00:00'
            to_date = query[13:23] + ' 23:59:59'
            # format_str = '%d/%m/%Y'
            format_str = '%d/%m/%Y %H:%M:%S'

            start_date = datetime.datetime.strptime(from_date, format_str)
            end_date = datetime.datetime.strptime(to_date, format_str)

            object_list = Turno.objects.filter(created_at__date__range=(
                start_date, end_date), empresa_id=current_company_id).order_by('-created_at')
        else:
            index_end_date = datetime.date.today()
            # index_start_date = datetime.date.today() - timedelta(30)
            index_start_date = datetime.date.today()

            object_list = Turno.objects.filter(created_at__date__range=(
                index_start_date, index_end_date), empresa_id=current_company_id).order_by('-created_at',)

        return object_list


'''
def ajax_listado_turnos(request):
    from_date = request.POST.get("startDate")
    to_date = request.POST.get("endDate")
    format_str = '%Y-%m-%d'
    start_date = datetime.datetime.strptime(from_date, format_str)
    end_date = datetime.datetime.strptime(to_date, format_str)

    turnos = Turno.objects.raw("""
                select *
                from usuario_turno
                where date(created_at) >= '%s' and date(created_at) <= '%s'
                order by activo, created_at desc
                """ % (start_date, end_date))

    result = []
    for t in turnos:
        result.append({
            'turno_id': t.turno_id,
            'fecha': str(t.created_at),
            'usuario': t.usuario_creador.username,
            'estado': 'ABIERTO' if t.activo else 'CERRADO',
            'importe_apertura': str(t.importe_apertura),
            'importe_cierre': str(t.importe_cierre),
        })
    data = json.dumps(result)
    return HttpResponse(data, content_type='application/json')
'''

"""def crear_turno_view(request):
    if request.method == 'POST':
        form = CrearTurnoForm(request.POST)
        if form.is_valid:
            current_user = request.user
            turno_obj = form.save(commit=False)
            turno_obj.usuario = current_user
            turno_obj.save()

            # self.object = newturno

            # guardar monto en pagos
            sri_forma_obj = SriFormaPago.objects.filter(codigo='01')[0]
            sri_tipo_moneda_obj = SriTipoMoneda.objects.filter(codigo='DOLAR')[0]
            app_forma_pago_obj = FormaPago.objects.filter(codigo='ENT_FAC')[0]
            estado_pago_obj = EstadoPago.objects.filter(situacion='Confirmado')[0]

            p = Pago()
            p.turno = turno_obj
            p.usuario = current_user
            p.app_forma_pago = app_forma_pago_obj
            p.sri_forma_pago = sri_forma_obj
            p.sri_tipo_moneda = sri_tipo_moneda_obj
            p.tipo_flujo = FlowTypes.debe.value
            p.orden_id = 0
            p.importe = turno_obj.importe_apertura
            p.referencia = 'Apertura caja'
            p.estado = estado_pago_obj

            p.save()

            '''libro = LibroDiario()
            libro.asiento =
            libro.turno = turno_obj
            libro.usuario_creador = current_user
            libro.cuenta = cuenta_obj
            libro.movimiento = FlowTypes.debe.value
            '''

        return redirect('contabilidad:listado_turnos')
    else:
        turno_obj = Turno.objects.filter(usuario=request.user, activo=True)
        if turno_obj.exists():
            # return redirect('pago:mensaje_vista',  1)
            # return redirect('pago:mensaje_vista')
            return render(request, 'contabilidad/message.html', {'activo': True})
        else:
            form = CrearTurnoForm()

    return render(request, 'contabilidad/crear_turno_modal.html', {'form': form})"""

"""class CrearTurno(BSModalCreateView):
    template_name = 'contabilidad/turnos/crear_turno_modal.html'
    form_class = CrearTurnoForm
    success_message = 'Success: El Turno fue creado.'
    success_url = reverse_lazy('contabilidad:listado_turnos')

    def form_valid(self, form):
        form.instance.usuario_creador = self.request.user
        form.instance.empresa_id = self.request.session['company_id']
        return super(CrearTurno, self).form_valid(form)"""


class CrearTurno(BSModalCreateView):
    info_shift_active = False
    template_name = 'contabilidad/turnos/crear_turno_modal.html'
    form_class = CrearTurnoForm
    success_message = 'Success: El Turno fue creado.'
    success_url = reverse_lazy('contabilidad:listado_turnos')

    # def form_valid(self, form):
    # form.instance.usuario_creador = self.request.user
    # form.instance.empresa_id = self.request.session['company_id']
    # return super(CrearTurno, self).form_valid(form)

    def form_valid(self, form):
        form.instance.usuario_creador = self.request.user
        form.instance.empresa_id = self.request.session['company_id']
        self.object = form.save()

        if self.object.pk:
            # guardar monto en pagos
            '''sri_forma_obj = SriFormaPago.objects.filter(codigo='01')[0]
            sri_tipo_moneda_obj = SriTipoMoneda.objects.filter(codigo='DOLAR')[0]
            app_forma_pago_obj = FormaPago.objects.filter(codigo='ENT_FAC')[0]
            estado_pago_obj = EstadoPago.objects.filter(situacion='Confirmado')[0]

            trans_pagos = Pago()
            trans_pagos.turno = self.object
            trans_pagos.usuario = self.request.user
            trans_pagos.app_forma_pago = app_forma_pago_obj
            trans_pagos.sri_forma_pago = sri_forma_obj
            trans_pagos.sri_tipo_moneda = sri_tipo_moneda_obj
            trans_pagos.tipo_flujo = FlowTypes.debe.value
            trans_pagos.orden_id = 0
            trans_pagos.importe = self.object.importe_apertura
            trans_pagos.referencia = 'Apertura caja'
            trans_pagos.estado = estado_pago_obj
            trans_pagos.save()'''

            current_company_id = self.request.session['company_id']
            asiento_auto_set = AsientoAutomatico.objects.filter(
                grupo_asiento='Apertura de caja', cuenta_id__isnull=False,
                empresa_id=current_company_id).order_by('debito')

            if asiento_auto_set:
                glosa = 'Para registrar apertura de turno Nro. {0}'.format(self.object.pk)
                # fecha = self.object.created_at.strftime('%Y-%m-%d %H:%M:%S')
                fecha = self.object.created_at.strftime('%Y-%m-%d')
                comprobante = self.object.pk

                tabla_json = []
                for asiento in asiento_auto_set:
                    if asiento.debito:
                        tabla_json.append({
                            'cuenta_id': asiento.cuenta.pk,
                            'debito': str(self.object.importe_apertura),
                            'credito': '',
                        })
                    else:
                        tabla_json.append({
                            'cuenta_id': asiento.cuenta.pk,
                            'debito': '',
                            'credito': str(self.object.importe_apertura),
                        })
                data = json.dumps(tabla_json)

                crear_asiento_contable_automatico(
                    fecha, glosa, comprobante, self.request.user, current_company_id, data)

        return super(CrearTurno, self).form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super(CrearTurno, self).get_context_data(**kwargs)

        current_company_id = self.request.session['company_id']

        turno_obj = Turno.objects.filter(
            usuario_creador=self.request.user, activo=True, empresa_id=current_company_id)
        if turno_obj.exists():
            self.info_shift_active = True

        ctx['info_shift_active'] = self.info_shift_active
        return ctx


def crear_asiento_contable_automatico(fecha, glosa, comprobante, current_user, current_company_id, tabla_json):
    # mytableData = request.POST.get('pTableData', None)

    # print("fecha recibida=%s" % fecha)  # 2019-08-16 17:47:22
    # guardar asiento
    format_str = '%Y-%m-%d'  # The format
    datetime_obj = datetime.datetime.strptime(fecha, format_str)

    asiento = AsientoContable()
    asiento.fecha = datetime_obj
    # asiento.debe =
    # asiento.haber =
    asiento.glosa = glosa
    asiento.comprobante = comprobante
    asiento.usuario_creador = current_user
    asiento.empresa_id = current_company_id
    asiento.save()

    # JSON to Dict
    json_data = json.loads(tabla_json)

    for key in json_data:
        cuenta_id = int(key['cuenta_id'])
        monto_debe = float(key['debito']) if key['debito'] != '' else 0
        monto_haber = float(key['credito']) if key['credito'] != '' else 0

        if monto_debe > 0:
            debe = AsientoDebeDetalle(asiento_id=asiento.id,
                                      cuenta_id=cuenta_id, monto=monto_debe)
            debe.save()
        else:
            haber = AsientoHaberDetalle(asiento_id=asiento.id,
                                        cuenta_id=cuenta_id, monto=monto_haber)
            haber.save()

    return True


"""class DetalleTurno(DetailView):
    model = Turno
    template_name = 'contabilidad/detalle_turno_modal.html'"""


class ModificarTurno(BSModalUpdateView):
    model = Turno
    template_name = 'contabilidad/turnos/modificar_turno_modal.html'
    form_class = CrearTurnoForm
    success_message = 'Success:El turno fue actualizado.'
    success_url = reverse_lazy('contabilidad:listado_turnos')


class DetalleTurno(BSModalReadView):
    model = Turno
    template_name = 'contabilidad/turnos/detalle_turno_modal.html'


class EliminarTurno(BSModalDeleteView):
    model = Turno
    template_name = 'contabilidad/turnos/eliminar_turno_modal.html'
    success_message = 'Success: El turno fue eliminado.'
    success_url = reverse_lazy('contabilidad:listado_turnos')


class CerrarTurnoModal(BSModalReadView):
    model = Turno
    template_name = 'contabilidad/turnos/cerrar_turno_modal.html'

    def get_context_data(self, **kwargs):
        context = super(CerrarTurnoModal, self).get_context_data(**kwargs)

        turno_obj = Turno.objects.get(pk=self.kwargs.get('pk'))

        if turno_obj.activo:
            today = datetime.date.today()
            context['fecha_actual'] = today
            context['hora_actual'] = datetime.datetime.now()

            # calculo ventas efectivo
            cash = Pago.objects.filter(
                tipo_flujo=utils.flow_dictionary["DEBE"], sri_forma_pago_id=1, turno=turno_obj, referencia='Venta').aggregate(total=Sum('importe'))['total']
            if cash is None:
                cash = 0
            context['ventas_efectivo'] = cash

            # calculo ventas tarjeta débito
            debit_card = Pago.objects.filter(
                tipo_flujo=utils.flow_dictionary["DEBE"], sri_forma_pago_id=3, turno=turno_obj).aggregate(total=Sum('importe'))['total']
            if debit_card is None:
                debit_card = 0
            context['ventas_tarjeta_debito'] = debit_card

            # calculo ventas tarjeta crédito
            credit_card = Pago.objects.filter(
                tipo_flujo=utils.flow_dictionary["DEBE"], sri_forma_pago_id=6, turno=turno_obj).aggregate(total=Sum('importe'))['total']
            if credit_card is None:
                credit_card = 0
            context['ventas_tarjeta_credito'] = credit_card

            # calculo ventas con cheque ==> OTRO CON UTILIZACIÓN DEL SISTEMA FINANCIERO
            sale_check = Pago.objects.filter(
                tipo_flujo=utils.flow_dictionary["DEBE"], app_forma_pago_id=2, turno=turno_obj).aggregate(total=Sum('importe'))['total']
            if sale_check is None:
                sale_check = 0
            context['ventas_cheque'] = sale_check

            # calculo ventas con transferencia ==> OTRO CON UTILIZACIÓN DEL SISTEMA FINANCIERO
            sale_transfer = Pago.objects.filter(
                tipo_flujo=utils.flow_dictionary["DEBE"], app_forma_pago_id=6, turno=turno_obj).aggregate(total=Sum('importe'))['total']
            if sale_transfer is None:
                sale_transfer = 0
            context['ventas_transferencia'] = sale_transfer

            # calculo ventas sistema financiero
            finance_system = Pago.objects.filter(
                tipo_flujo=utils.flow_dictionary["DEBE"], sri_forma_pago_id=7, turno=turno_obj).aggregate(total=Sum('importe'))['total']
            if finance_system is None:
                finance_system = 0
            context['ventas_sistema_financiero'] = finance_system

            # cobros ventas a credito
            # PENDIENTES....
            cuenta_cobrar_efectivo = Pago.objects.filter(
                tipo_flujo=utils.flow_dictionary["DEBE"], sri_forma_pago_id=1, turno=turno_obj, referencia='Cuentas por cobrar').aggregate(total=Sum('importe'))['total']
            if cuenta_cobrar_efectivo is None:
                cuenta_cobrar_efectivo = 0
            context['cobro_ventas_credito'] = cuenta_cobrar_efectivo

            # calculo compras efectivo (HABER)
            buy_cash = Pago.objects.filter(
                tipo_flujo=utils.flow_dictionary["HABER"], sri_forma_pago_id=1, turno=turno_obj).aggregate(total=Sum('importe'))['total']
            if buy_cash is None:
                buy_cash = 0
            context['compras_efectivo'] = buy_cash

            balance = turno_obj.importe_apertura + cash + sale_transfer + sale_check + \
                credit_card + debit_card + cuenta_cobrar_efectivo - buy_cash
            context['balance'] = balance

            return context


def terminar_cierre_caja(request):
    if request.method == 'POST':
        if request.is_ajax():
            balance = request.POST.get('balance', 0)
            observaciones = request.POST.get('observaciones', None)
            current_user = request.user

            turno = Turno.objects.filter(usuario_creador=current_user, activo=True)[0]
            turno.importe_cierre = balance
            turno.concepto_cierre = observaciones
            turno.activo = False
            turno.save()

            asiento_auto_set = AsientoAutomatico.objects.filter(
                grupo_asiento='Cierre de caja').order_by('debito')

            if asiento_auto_set:
                glosa = 'Para registrar cierre de turno Nro. {0}'.format(turno.pk)
                current_company_id = request.session['company_id']

                today = datetime.date.today()
                fecha = format(today, '%Y-%m-%d')
                comprobante = turno.pk

                tabla_json = []
                for asiento in asiento_auto_set:
                    if asiento.debito:
                        tabla_json.append({
                            'cuenta_id': asiento.cuenta.pk,
                            'debito': str(turno.importe_cierre),
                            'credito': '',
                        })
                    else:
                        tabla_json.append({
                            'cuenta_id': asiento.cuenta.pk,
                            'debito': '',
                            'credito': str(turno.importe_cierre),
                        })
                data = json.dumps(tabla_json)

                crear_asiento_contable_automatico(
                    fecha, glosa, comprobante, request.user, current_company_id, data)

            return JsonResponse({
                'success': True,
                # 'redirect': '../view/' + str(turno.turno_id)
                'redirect': '../listado_turnos/'
            })


'''class FlujoCajaEfectivo(ListView):
    template_name = 'contabilidad/flujo_caja_efectivo.html'
    context_object_name = 'all_pagos'
    paginate_by = 10

    def get_queryset(self):
        return Pago.objects.all().order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super(FlujoCajaEfectivo, self).get_context_data(**kwargs)
        context['usuarios'] = User.objects.filter(is_staff=False)

        # turno_obj = Turno.objects.filter(usuario=self.request.user, activo=True)[0]
        # context['turno_id'] = turno_obj.turno_id

        return context'''


class FlowTypes(Enum):
    debe = 'D'  # Débito
    haber = 'H'  # Crédito


'''def apertura_caja_view(request):
    if request.method == 'POST':
        form = CrearTurnoForm(request.POST)
        if form.is_valid:
            current_user = request.user
            turno_obj = form.save(commit=False)
            turno_obj.usuario = current_user
            turno_obj.save()

            # self.object = newturno

            # guardar monto en pagos
            sri_forma_obj = SriFormaPago.objects.filter(codigo='01')[0]
            sri_tipo_moneda_obj = SriTipoMoneda.objects.filter(codigo='DOLAR')[0]
            app_forma_pago_obj = FormaPago.objects.filter(codigo='ENT_FAC')[0]
            estado_pago_obj = EstadoPago.objects.filter(situacion='Confirmado')[0]

            p = Pago()
            p.turno = turno_obj
            p.usuario = current_user
            p.app_forma_pago = app_forma_pago_obj
            p.sri_forma_pago = sri_forma_obj
            p.sri_tipo_moneda = sri_tipo_moneda_obj
            p.tipo_flujo = FlowTypes.debe.value
            p.orden_id = 0
            p.importe = turno_obj.importe_apertura
            p.referencia = 'Apertura caja'
            p.estado = estado_pago_obj

            p.save()

            """libro = LibroDiario()
            libro.asiento =
            libro.turno = turno_obj
            libro.usuario_creador = current_user
            libro.cuenta = cuenta_obj
            libro.movimiento = FlowTypes.debe.value
            """

        return redirect('contabilidad:view', pk=turno_obj.pk)
    else:
        turno_obj = Turno.objects.filter(usuario=request.user, activo=True)
        if turno_obj.exists():
            # return redirect('pago:mensaje_vista',  1)
            # return redirect('pago:mensaje_vista')
            return render(request, 'contabilidad/message.html', {'activo': True})
        else:
            form = CrearTurnoForm()

    return render(request, 'contabilidad/apertura_caja.html', {'form': form})'''


def arqueo_caja_list(request, turno_id):
    # model = Turno
    # template_name = 'pago/arqueo_caja.html'
    # context_object_name = 'turnos'

    # turno_obj = Turno.objects.get(pk=turno_id)
    # context = RequestContext(request, {'turno': turno_obj})
    # return render_to_response('pago/arqueo_caja.html', context)

    # turno_obj = Turno.objects.get(pk=turno_id)
    # context = {"turno_obj": turno_obj}
    # return render(request, "pago/arqueo_caja.html", context=context)

    turno_obj = Turno.objects.get(pk=turno_id)

    if request.method == 'GET':
        # turno_obj = Turno.objects.filter(usuario=request.user, activo=True)
        if turno_obj.activo:
            # turno_obj = Turno.objects.get(pk=turno_obj[0].turno_id)
            context = {"turno_obj": turno_obj}

            today = datetime.date.today()
            context['fecha_actual'] = today
            context['hora_actual'] = datetime.datetime.now()

            # calculo ventas efectivo
            cash = Pago.objects.filter(
                tipo_flujo=utils.flow_dictionary["DEBE"], sri_forma_pago_id=1, turno=turno_obj, referencia='Venta').aggregate(total=Sum('importe'))['total']
            if cash is None:
                cash = 0
            context['ventas_efectivo'] = cash

            # calculo ventas tarjeta débito
            debit_card = Pago.objects.filter(
                tipo_flujo=utils.flow_dictionary["DEBE"], sri_forma_pago_id=3, turno=turno_obj).aggregate(total=Sum('importe'))['total']
            if debit_card is None:
                debit_card = 0
            context['ventas_tarjeta_debito'] = debit_card

            # calculo ventas tarjeta crédito
            credit_card = Pago.objects.filter(
                tipo_flujo=utils.flow_dictionary["DEBE"], sri_forma_pago_id=6, turno=turno_obj).aggregate(total=Sum('importe'))['total']
            if credit_card is None:
                credit_card = 0
            context['ventas_tarjeta_credito'] = credit_card

            # calculo ventas con cheque ==> OTRO CON UTILIZACIÓN DEL SISTEMA FINANCIERO
            sale_check = Pago.objects.filter(
                tipo_flujo=utils.flow_dictionary["DEBE"], app_forma_pago_id=2, turno=turno_obj).aggregate(total=Sum('importe'))['total']
            if sale_check is None:
                sale_check = 0
            context['ventas_cheque'] = sale_check

            # calculo ventas con transferencia ==> OTRO CON UTILIZACIÓN DEL SISTEMA FINANCIERO
            sale_transfer = Pago.objects.filter(
                tipo_flujo=utils.flow_dictionary["DEBE"], app_forma_pago_id=6, turno=turno_obj).aggregate(total=Sum('importe'))['total']
            if sale_transfer is None:
                sale_transfer = 0
            context['ventas_transferencia'] = sale_transfer

            # calculo ventas sistema financiero
            finance_system = Pago.objects.filter(
                tipo_flujo=utils.flow_dictionary["DEBE"], sri_forma_pago_id=7, turno=turno_obj).aggregate(total=Sum('importe'))['total']
            if finance_system is None:
                finance_system = 0
            context['ventas_sistema_financiero'] = finance_system

            # cobros ventas a credito
            # PENDIENTES....
            cuenta_cobrar_efectivo = Pago.objects.filter(
                tipo_flujo=utils.flow_dictionary["DEBE"], sri_forma_pago_id=1, turno=turno_obj, referencia='Cuentas por cobrar').aggregate(total=Sum('importe'))['total']
            if cuenta_cobrar_efectivo is None:
                cuenta_cobrar_efectivo = 0
            context['cobro_ventas_credito'] = cuenta_cobrar_efectivo

            # calculo compras efectivo (HABER)
            buy_cash = Pago.objects.filter(
                tipo_flujo=utils.flow_dictionary["HABER"], sri_forma_pago_id=1, turno=turno_obj).aggregate(total=Sum('importe'))['total']
            if buy_cash is None:
                buy_cash = 0
            context['compras_efectivo'] = buy_cash

            balance = turno_obj.importe_apertura + cash + sale_transfer + sale_check + \
                credit_card + debit_card + cuenta_cobrar_efectivo - buy_cash
            context['balance'] = balance

            return render(request, "contabilidad/turnos/arqueo_caja.html", context=context)
        else:
            return render(request, 'contabilidad/mensajes/message.html', {'activo': False})


def getTotalX(turno_id, tipo_flujo, forma_pago_id):
    # turno_obj = Turno.objects.get(pk=turno_id)

    # calculo monto
    monto = Pago.objects.filter(
        turno_id=turno_id,
        tipo_flujo=tipo_flujo,
        app_forma_pago_id=forma_pago_id
    ).aggregate(total=Sum('importe'))['total']
    if monto is None:
        monto = 0
    return round(monto, 2)


def ajaxImprimirRecibo(request):
    if request.method == 'GET':
        if request.is_ajax():
            current_user = request.user

            turno_obj = Turno.objects.filter(usuario_creador=current_user, activo=True)[0]
            company = turno_obj.usuario_creador.perfil.empresa.nombre_comercial

            impresora = turno_obj.usuario_creador.perfil.empresa.impresora_nombre

            if not impresora:
                return JsonResponse({
                    'success': False,
                })

            # verificar ip
            if is_valid_ip(impresora):
                Epson = printer.Network(impresora)
            else:
                Epson = Usb(0x0416, 0x5011, profile="POS-5890")

            # pip install python-escpos
            # Epson = printer.Network("192.168.100.20")
            Epson.set(font='a', height=2, align='center', text_type='bold')
            Epson.text(company + "\n")
            Epson.text("Recibo de Arqueo de Caja\n")

            Epson.set(align='left', font='None')
            Epson.text("Arqueo Nro: %s\n" % turno_obj.turno_id)

            import locale
            locale.setlocale(locale.LC_TIME, '')

            dt_obj = datetime.datetime.now()
            # dt = dt_obj.strftime("%a, %d. %b %Y %I:%M%p")
            dt = dt_obj.strftime("%d/%m/%Y %I:%M%p")
            Epson.set(align='left')
            Epson.text("Fecha actual: " + dt + "\n")
            Epson.text("Apertura: " + turno_obj.created_at.strftime("%d/%m/%Y %I:%M%p") + "\n")
            Epson.text("Cajero(a): " + turno_obj.usuario_creador.username + "\n\n")

            Epson.set(font='b')
            Epson.text("+ Saldo inicial de caja\n")
            Epson.set(align='right')
            importe_apertura = turno_obj.importe_apertura
            Epson.text("%.2f\n" % importe_apertura)

            Epson.set(align='left')
            Epson.text("+ Importe de ventas en efectivo\n")
            Epson.set(align='right')
            venta_efectivo = getTotalX(
                turno_obj.turno_id, utils.flow_dictionary["DEBE"], utils.payment_dictionary["EFECTIVO"])
            Epson.text("%.2f\n" % venta_efectivo)

            Epson.set(align='left')
            Epson.text("+ Importe de ventas con tarjeta débito\n")
            Epson.set(align='right')
            venta_tarjeta_debito = getTotalX(
                turno_obj.turno_id, utils.flow_dictionary["DEBE"], utils.payment_dictionary["TARJETA_DEBITO"])
            Epson.text("%.2f\n" % venta_tarjeta_debito)

            Epson.set(align='left')
            Epson.text("+ Importe de ventas con tarjeta crédito\n")
            Epson.set(align='right')
            venta_tarjeta_credito = getTotalX(
                turno_obj.turno_id, utils.flow_dictionary["DEBE"], utils.payment_dictionary["TARJETA_CREDITO"])
            Epson.text("%.2f\n" % venta_tarjeta_credito)

            Epson.set(align='left')
            Epson.text("+ Importe de ventas con cheque\n")
            Epson.set(align='right')
            venta_cheque = getTotalX(
                turno_obj.turno_id, utils.flow_dictionary["DEBE"], utils.payment_dictionary["CHEQUE"])
            Epson.text("%.2f\n" % venta_cheque)

            Epson.set(align='left')
            Epson.text("+ Importe de ventas con transferencia\n")
            Epson.set(align='right')
            venta_transferencia = getTotalX(
                turno_obj.turno_id, utils.flow_dictionary["DEBE"], utils.payment_dictionary["TRANSFERENCIA"])
            Epson.text("%.2f\n" % venta_transferencia)

            Epson.set(align='left')
            Epson.text("+ Cobro de ventas a crédito (efectivo)\n")
            Epson.set(align='right')
            Epson.text("%.2f\n" % 0.00)

            Epson.set(align='left')
            Epson.text("+ Importe salida efectivo\n")
            Epson.set(align='right')
            compras_efectivo = getTotalX(
                turno_obj.turno_id, utils.flow_dictionary["HABER"], utils.payment_dictionary["EFECTIVO"])
            Epson.text("%.2f\n" % compras_efectivo)

            balance = importe_apertura + venta_efectivo + venta_transferencia
            +venta_tarjeta_debito + venta_tarjeta_credito + venta_cheque
            -compras_efectivo

            Epson.set(align='left', font='b', text_type='bold', width=2)
            Epson.text("= Saldo de caja\n")
            Epson.set(align='right', font='b', text_type='bold', width=2)
            Epson.text("%.2f\n\n\n" % balance)

            # Epson.set(align='left', text_type='bold', width=2)
            Epson.set(font='a', height=2, align='center', text_type='bold', width=2)
            Epson.text("Muchas gracias\n\n\n")

            # Cut paper
            Epson.cut()
            Epson.control("LF")

            return JsonResponse({
                'success': True,
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


"""
Cheques Girados
"""


class ListadoChequesRecibidos(ListView):
    model = PagoCheque
    template_name = 'contabilidad/bancos/lista_cheques_recibidos.html'
    context_object_name = 'cheques'  # Default: object_list
    paginate_by = 10

    # queryset = Pago.objects.filter(credito__saldo__gte=0)
    # queryset = Credito.objects.all()

    # If you don't need the model instance, go for:
    # queryset = Credito.objects.values('pago', 'vence', 'valor_cuota', 'abono', 'saldo', 'estado')

    # If you still need to access some instance methods, go for:
    # queryset = Credito.objects.only('pago', 'vence', 'valor_cuota', 'abono', 'saldo', 'estado')
    # queryset = Cheque.objects.only('pago', 'fecha_cheq', 'monto', 'estado')
    queryset = PagoCheque.objects.filter(pago__tipo_flujo='D').only(
        'pago', 'fecha_cheq', 'monto', 'estado')


class ListadoChequesEntregados(ListView):
    model = PagoCheque
    template_name = 'contabilidad/bancos/lista_cheques_entregados.html'
    context_object_name = 'cheques'  # Default: object_list
    paginate_by = 10

    # queryset = Pago.objects.filter(credito__saldo__gte=0)
    # queryset = Credito.objects.all()

    # If you don't need the model instance, go for:
    # queryset = Credito.objects.values('pago', 'vence', 'valor_cuota', 'abono', 'saldo', 'estado')

    # If you still need to access some instance methods, go for:
    # queryset = Credito.objects.only('pago', 'vence', 'valor_cuota', 'abono', 'saldo', 'estado')
    queryset = PagoCheque.objects.filter(pago__tipo_flujo='H').only(
        'pago', 'fecha_cheq', 'monto', 'estado')


"""class PlanCuenta(ListView):
    model = PlanCuenta
    template_name = 'contabilidad/plan_cuenta.html'
    context_object_name = 'all_accounts'"""

# def show_genres(request):
#    return render(request, "contabilidad/genres.html", {'genres': Genre.objects.all()})


class CuentasPagarIndexView(ListView):
    template_name = 'contabilidad/cuentas_por_pagar.html'
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


def ajaxAbonoCtaPagar(request):
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

        orden_id = credito.pago.orden_id
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
        })


class CuentasCobrarIndexView(ListView):
    template_name = 'contabilidad/cuentas_por_cobrar.html'
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


def ajaxAbonoCtaCobrar(request):
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

        factura_id = credito.pago.orden_id
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


class ListadoPeriodos(ListView):
    # model = PeriodoContable
    # context_object_name = 'periods'
    template_name = 'contabilidad/periodos/listado_periodos.html'

    def get_queryset(self):
        empresa_id = self.request.session['company_id']
        return PeriodoContable.objects.filter(empresa_id=empresa_id)


class CrearPeriodo(CreateView):
    template_name = 'contabilidad/periodos/periodo.html'
    form_class = PeriodoContableForm
    success_url = reverse_lazy('contabilidad:listado_periodos')

    def get(self, *args, **kwargs):
        current_company_id = self.request.session['company_id']
        periodo_obj = PeriodoContable.objects.filter(
            empresa_id=current_company_id, activo=True)

        if not periodo_obj.exists():
            return super(CrearPeriodo, self).get(*args, **kwargs)
        else:
            return render(self.request, 'contabilidad/mensajes/message_period.html', {'activo': True})

    def form_valid(self, form):
        f = form.save(commit=False)
        f.empresa_id = self.request.session['company_id']
        f.usuario_creador = self.request.user
        f.save()
        return super(CrearPeriodo, self).form_valid(form)


class EditarPeriodo(UpdateView):
    model = PeriodoContable
    template_name = 'contabilidad/periodos/periodo.html'
    form_class = PeriodoContableForm
    success_url = reverse_lazy('contabilidad:listado_periodos')


class DetallePeriodo(DetailView):
    model = PeriodoContable
    template_name = 'contabilidad/periodos/detalle_periodo.html'


class EliminarPeriodo(DeleteView):
    model = PeriodoContable
    template_name = 'contabilidad/periodos/eliminar_periodo.html'
    success_url = reverse_lazy('contabilidad:listado_periodos')


class ListadoCuentas(ListView):
    # model = Cuenta
    # context_object_name = 'accounts'
    template_name = 'contabilidad/cuentas/listado_cuentas.html'
    # template_name = 'contabilidad/cuentas/tree_grid.html'

    def get_queryset(self):
        empresa_id = self.request.session['company_id']
        return PlanCuenta.objects.filter(empresa_id=empresa_id)


def show_genres(request):
    return render(request, "contabilidad/cuentas/genres.html", {'genres': PlanCuenta.objects.all()})


def cargar_plan_cuenta_json(request):
    if request.method == 'POST':
        # eliminar cuentas existentes
        all_accounts = PlanCuenta.objects.all()
        all_accounts.delete()
        # return render(request, "contabilidad/diario/plan_cuenta.html", {'object_list': PlanCuenta.objects.all()})

        # cargar nuevas cuentas
        # fixtures = ['plan_cuenta.json']

        # opens the json file and saves the raw contents
        # data = open('../fixtures/plan_cuenta.json').read()
        ACCOUNTSPATH = 'fixtures/plan_cuenta.json'
        accounts_path = os.path.join(os.path.dirname(__file__), ACCOUNTSPATH)

        data = open(accounts_path).read()
        data1 = json.loads(data)  # deserialises it
        # data2 = json.dumps(data1)  # json formatted string

        # print(data1[0])
        # print(data1[0]["fields"])
        # print(data1[0]["fields"]["descripcion"])
        for elem in data1:
            pk = elem["pk"]
            # print("pk=%s" % pk)
            # print(elem["fields"]["descripcion"])
            codigo = elem["fields"]["codigo"]
            nombre = elem["fields"]["nombre"]
            clasificacion = elem["fields"]["clasificacion"]
            tipo = elem["fields"]["tipo"]
            level = elem["fields"]["level"]
            parent = elem["fields"]["parent"]

            account = PlanCuenta()
            account.id = pk
            account.usuario_creador = request.user
            account.codigo = codigo
            account.nombre = nombre
            account.clasificacion = clasificacion
            account.tipo = tipo
            account.level = level
            account.parent_id = parent
            account.save()

        return redirect('contabilidad:listado_cuentas')

    # return render(request, 'contabilidad/diario/cargar_cuentas_form.html')
    return render(request, 'contabilidad/cuentas/cargar_cuentas_form.html')


def cargar_plan_cuenta_excel(request):
    if request.method == 'POST':
        company_id = request.session['company_id']
        # eliminar cuentas existentes
        all_accounts = PlanCuenta.objects.filter(empresa_id=company_id)
        all_accounts.delete()

        # Open the workbook
        xls_path = '../../opt/cuentas/plan_predef.xlsx'
        #book = xlrd.open_workbook(xls_path)
        book = xlrd.open_workbook(os.path.join(os.path.dirname(__file__), xls_path))

        sheet = book.sheets()[0]
        codigo = sheet.col_values(0, 1)
        cuenta = sheet.col_values(1, 1)
        grupo = sheet.col_values(2, 1)
        tipo = sheet.col_values(3, 1)
        nivel = sheet.col_values(4, 1)
        padre = sheet.col_values(5, 1)

        import math

        for codigo, cuenta, grupo, tipo, nivel, padre in zip(codigo, cuenta, grupo, tipo, nivel, padre):
            """if type(codigo) is float:
                parte_entera = 0.0
                parte_decimal = 0.0
                parte_decimal, parte_entera = math.modf(codigo)

                # truco codigo 1 ACTIVO devuelve 1.0 ACTIVO
                if parte_decimal == 0.0:
                    pk = str(int(codigo))
                    codigo = pk
                else:
                    pk = str(codigo)
            else:
                pk = codigo

            if type(padre) is float:
                parte_entera = 0.0
                parte_decimal = 0.0
                parte_decimal, parte_entera = math.modf(padre)

                # truco codigo 1 ACTIVO devuelve 1.0 ACTIVO
                if parte_decimal == 0.0:
                    father = str(int(padre))
                    parent = father
                else:
                    parent = str(padre)
            else:
                parent = padre

            if parent == '0':
                parent = None"""

            # print("codigo= %s pk= %s padre=%s" % (codigo, pk, parent))
            # account = Cuenta.objects.get_or_create(codigo=codigo)

            if type(codigo) is float:
                parte_entera = 0.0
                parte_decimal = 0.0
                parte_decimal, parte_entera = math.modf(codigo)

                # truco codigo 1 ACTIVO devuelve 1.0 ACTIVO
                if parte_decimal == 0.0:
                    pk = str(int(codigo))
                    codigo = pk

            if type(padre) is float:
                parte_entera = 0.0
                parte_decimal = 0.0
                parte_decimal, parte_entera = math.modf(padre)

                # truco codigo 1 ACTIVO devuelve 1.0 ACTIVO
                if parte_decimal == 0.0:
                    father = str(int(padre))
                    parent_code = father
                else:
                    parent_code = str(padre)
            else:
                parent_code = padre

            if parent_code == '0':
                parent_code = None

            # print("code=%s longitud=%s" % (parent_code, len(str(parent_code))))
            parent_obj = PlanCuenta.objects.filter(codigo=parent_code, empresa_id=company_id)
            if parent_obj.exists():
                parent_id = parent_obj[0].id
            else:
                parent_id = None

            account = PlanCuenta()
            # account.id = pk
            account.usuario_creador = request.user
            account.empresa_id = company_id
            account.codigo = codigo
            account.nombre = cuenta
            account.clasificacion = grupo
            account.tipo = tipo
            account.level = nivel
            account.parent_id = parent_id
            account.save()

        return redirect('contabilidad:listado_cuentas')

    # return render(request, 'contabilidad/diario/cargar_cuentas_form.html')
    return render(request, 'contabilidad/cuentas/cargar_cuentas_form.html')


def cargar_asiento_auto_excel(request):
    if request.method == 'POST':
        company_id = request.session['company_id']
        # eliminar cuentas existentes
        all_seats = AsientoAutomatico.objects.filter(empresa_id=company_id)
        all_seats.delete()

        # Open the workbook
        xls_path = '../../opt/cuentas/asientoauto_predef.xlsx'
        #book = xlrd.open_workbook(xls_path)
        book = xlrd.open_workbook(os.path.join(os.path.dirname(__file__), xls_path))

        sheet = book.sheets()[0]
        codigo = sheet.col_values(0, 1)
        grupo = sheet.col_values(1, 1)
        descripcion = sheet.col_values(2, 1)
        debito = sheet.col_values(3, 1)
        credito = sheet.col_values(4, 1)

        for codigo, grupo, descripcion, debito, credito in zip(codigo, grupo, descripcion, debito, credito):
            if debito == 'S':
                debito = True
                credito = False
            else:
                debito = False
                credito = True

            account = AsientoAutomatico()
            # account.id = pk
            account.usuario_creador = request.user
            account.empresa_id = company_id
            account.codigo_enlace = codigo
            account.grupo_asiento = grupo
            account.descripcion = descripcion
            account.cuenta = None
            account.debito = debito
            account.credito = credito
            account.save()

        return redirect('contabilidad:listado_asientos_automaticos')

    return render(request, 'contabilidad/asiento_automatico/cargar_asientos_form.html')


class CrearCuenta(CreateView):
    template_name = 'contabilidad/cuentas/cuenta.html'
    form_class = PlanCuentaForm
    success_url = reverse_lazy('contabilidad:listado_cuentas')

    def form_valid(self, form):
        f = form.save(commit=False)
        # codigo = self.object.codigo,
        # f.id = codigo.replace('.', '')  # PK de acuerdo al código
        f.usuario_creador = self.request.user
        f.save()
        return super(CrearCuenta, self).form_valid(form)


class EditarCuenta(UpdateView):
    model = PlanCuenta
    template_name = 'contabilidad/cuentas/cuenta.html'
    form_class = PlanCuentaForm
    success_url = reverse_lazy('contabilidad:listado_cuentas')


def load_padre(request):

    clasificacion_text = request.GET.get('clasificacion_text')
    print("CLASIFICACION=%s" % clasificacion_text)
    cuentas = PlanCuenta.objects.filter(clasificacion=clasificacion_text).values(
        'id', 'codigo', 'nombre').order_by('codigo')
    return render(request, 'contabilidad/cuentas/padre_dropdown_list_options.html', {'cuentas': cuentas})


class DetalleCuenta(DetailView):
    model = PlanCuenta
    template_name = 'contabilidad/cuentas/detalle_cuenta.html'


class EliminarCuenta(DeleteView):
    model = PlanCuenta
    template_name = 'contabilidad/cuentas/eliminar_cuenta.html'
    success_url = reverse_lazy('contabilidad:listado_cuentas')


class GenerateLibroMayorAuxiliarPDF(View):

    def get(self, request, *args, **kwargs):
        from django.db.models import CharField, Value

        company_id = request.session['company_id']
        empresa_obj = Empresa.objects.get(pk=company_id)
        # daily_obj = AsientoContable.objects.filter(empresa_id=company_id)

        qs1 = AsientoDebeDetalle.objects.select_related(
            'asiento').filter(asiento__empresa_id=company_id).annotate(mycolumn=Value('D', output_field=CharField()))  # .order_by('cuenta_id', 'asiento_id')
        qs2 = AsientoHaberDetalle.objects.select_related(
            'asiento').filter(asiento__empresa_id=company_id).annotate(mycolumn=Value('H', output_field=CharField()))  # .order_by('cuenta_id', 'asiento_id')
        qs3 = qs1.union(qs2).order_by('cuenta_id', 'asiento_id')

        '''
        (SELECT "contabilidad_asientodebedetalle"."id", "contabilidad_asientodebedetalle"."asiento_id", "contabilidad_asientodebedetalle"."cuenta_id", "contabilidad_asientodebedetalle"."monto", 'D' AS "mycolumn", "contabilidad_asientocontable"."id", "contabilidad_asientocontable"."numero_asiento", "contabilidad_asientocontable"."fecha", "contabilidad_asientocontable"."glosa", "contabilidad_asientocontable"."comprobante", "contabilidad_asientocontable"."usuario_creador_id", "contabilidad_asientocontable"."empresa_id"
        FROM "contabilidad_asientodebedetalle"
        INNER JOIN "contabilidad_asientocontable" ON ("contabilidad_asientodebedetalle"."asiento_id" = "contabilidad_asientocontable"."id")
        WHERE "contabilidad_asientocontable"."empresa_id" = 1)
        UNION
        (SELECT "contabilidad_asientohaberdetalle"."id", "contabilidad_asientohaberdetalle"."asiento_id", "contabilidad_asientohaberdetalle"."cuenta_id", "contabilidad_asientohaberdetalle"."monto", 'H' AS "mycolumn", "contabilidad_asientocontable"."id", "contabilidad_asientocontable"."numero_asiento", "contabilidad_asientocontable"."fecha", "contabilidad_asientocontable"."glosa", "contabilidad_asientocontable"."comprobante", "contabilidad_asientocontable"."usuario_creador_id", "contabilidad_asientocontable"."empresa_id"
        FROM "contabilidad_asientohaberdetalle"
        INNER JOIN "contabilidad_asientocontable" ON ("contabilidad_asientohaberdetalle"."asiento_id" = "contabilidad_asientocontable"."id")
        WHERE "contabilidad_asientocontable"."empresa_id" = 1)
        ORDER BY (3) ASC, (2) ASC'''

        ctas_debe_qs = AsientoDebeDetalle.objects.select_related(
            'asiento').filter(asiento__empresa_id=company_id).values('cuenta', 'cuenta__codigo', 'cuenta__nombre')  # .distinct()
        ctas_haber_qs = AsientoHaberDetalle.objects.select_related(
            'asiento').filter(asiento__empresa_id=company_id).values('cuenta', 'cuenta__codigo', 'cuenta__nombre')  # .distinct()
        ctas_libro_mayor_qs = ctas_debe_qs.union(
            ctas_haber_qs).distinct().order_by('cuenta__nombre')

        '''(SELECT "contabilidad_asientodebedetalle"."cuenta_id", "contabilidad_plancuenta"."nombre"
        FROM "contabilidad_asientodebedetalle"
        INNER JOIN "contabilidad_asientocontable" ON ("contabilidad_asientodebedetalle"."asiento_id" = "contabilidad_asientocontable"."id")
        INNER JOIN "contabilidad_plancuenta" ON ("contabilidad_asientodebedetalle"."cuenta_id" = "contabilidad_plancuenta"."id")
        WHERE "contabilidad_asientocontable"."empresa_id" = 1)
        UNION
        (SELECT "contabilidad_asientohaberdetalle"."cuenta_id", "contabilidad_plancuenta"."nombre"
        FROM "contabilidad_asientohaberdetalle"
        INNER JOIN "contabilidad_asientocontable" ON ("contabilidad_asientohaberdetalle"."asiento_id" = "contabilidad_asientocontable"."id")
        INNER JOIN "contabilidad_plancuenta" ON ("contabilidad_asientohaberdetalle"."cuenta_id" = "contabilidad_plancuenta"."id")
        WHERE "contabilidad_asientocontable"."empresa_id" = 1) ORDER BY (2) ASC'''

        params = {
            # 'orden_id': factura_id,
            # 'cliente_nombre': factura_obj.cliente.nombre,
            # 'cliente_direccion': factura_obj.cliente.direccion,
            # 'cliente_telefono': factura_obj.cliente.telefono,
            'empresa': empresa_obj,
            'libro_mayor': ctas_libro_mayor_qs,
            'libro_diario': qs3,
        }

        pdf = render_to_pdf('jinjatemplates/contabilidad/libro_mayor_auxiliar.html', params)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "libro_mayor_auxiliar.pdf"
            content = "inline; filename=%s" % (filename)
            download = request.GET.get("download")
            if download:
                content = "attachment; filename=%s" % (filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Error Rendering PDF", status=400)


class GenerateLibroMayorPrincipalPDF(View):

    def get(self, request, *args, **kwargs):
        from django.db.models import CharField, Value

        company_id = request.session['company_id']
        empresa_obj = Empresa.objects.get(pk=company_id)
        # daily_obj = AsientoContable.objects.filter(empresa_id=company_id)

        qs1 = AsientoDebeDetalle.objects.select_related(
            'asiento').filter(asiento__empresa_id=company_id).annotate(mycolumn=Value('D', output_field=CharField()))  # .order_by('cuenta_id', 'asiento_id')
        qs2 = AsientoHaberDetalle.objects.select_related(
            'asiento').filter(asiento__empresa_id=company_id).annotate(mycolumn=Value('H', output_field=CharField()))  # .order_by('cuenta_id', 'asiento_id')
        qs3 = qs1.union(qs2).order_by('cuenta_id', 'asiento_id')

        ctas_libro_mayor_qs = PlanCuenta.objects.filter(
            tipo='CUENTA', empresa_id=company_id).values('id', 'codigo', 'nombre').order_by('codigo')

        """ctas_debe_qs = AsientoDebeDetalle.objects.select_related(
            'asiento').filter(asiento__empresa_id=company_id).values('cuenta', 'cuenta__codigo', 'cuenta__nombre')  # .distinct()
        ctas_haber_qs = AsientoHaberDetalle.objects.select_related(
            'asiento').filter(asiento__empresa_id=company_id).values('cuenta', 'cuenta__codigo', 'cuenta__nombre')  # .distinct()
        ctas_libro_mayor_qs = ctas_debe_qs.union(
            ctas_haber_qs).distinct().order_by('cuenta__nombre')"""

        params = {
            'empresa': empresa_obj,
            'libro_mayor': ctas_libro_mayor_qs,
            'libro_diario': qs3,
        }

        # pdf = render_to_pdf('jinjatemplates/contabilidad/libro_mayor_principal.html', params)
        pdf = render_to_pdf('contabilidad/informes/libro_mayor_principal.html', params)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "libro_mayor_principal.pdf"
            content = "inline; filename=%s" % (filename)
            download = request.GET.get("download")
            if download:
                content = "attachment; filename=%s" % (filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Error Rendering PDF", status=400)


class GenerateBalanceComprobacionPDF(View):

    def get(self, request, *args, **kwargs):

        company_id = request.session['company_id']
        empresa_obj = Empresa.objects.get(pk=company_id)
        balance_comprobacion_qs = BalanceComprobacion.objects.filter(empresa=empresa_obj)

        months = [
            "DESCONOCIDO",
            "ENERO",
            "FEBRERO",
            "MARZO",
            "ABROÑ",
            "MAYO",
            "JUNIO",
            "JULIO",
            "AGOSTO",
            "SEPTIEMBRE",
            "OCTUBRE",
            "NOVIEMBRE",
            "DICIEMBRE"
        ]

        params = {
            # 'orden_id': factura_id,
            # 'cliente_nombre': factura_obj.cliente.nombre,
            # 'cliente_direccion': factura_obj.cliente.direccion,
            # 'cliente_telefono': factura_obj.cliente.telefono,
            'empresa': empresa_obj,
            'balance_comprobacion': balance_comprobacion_qs,

            'current_time': "AL %s DE %s DEL AÑO %s" % (datetime.date.today().day,
                                                        months[datetime.date.today().month],
                                                        datetime.date.today().year)
        }

        pdf = render_to_pdf('jinjatemplates/contabilidad/balance_comprobacion.html', params)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "balance_comprobacion.pdf"
            content = "inline; filename=%s" % (filename)
            download = request.GET.get("download")
            if download:
                content = "attachment; filename=%s" % (filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Error Rendering PDF", status=400)


class GenerateEstadoResultadosPDF(View):

    def get(self, request, *args, **kwargs):
        periodo_id = kwargs.get("pk")
        periodo_obj = PeriodoContable.objects.get(pk=periodo_id)
        # company_id = request.session['company_id']
        company_id = periodo_obj.empresa_id
        empresa_obj = Empresa.objects.get(pk=company_id)
        balance_comprobacion_qs = BalanceComprobacion.objects.filter(empresa=empresa_obj)

        months = [
            "DESCONOCIDO",
            "ENERO",
            "FEBRERO",
            "MARZO",
            "ABROÑ",
            "MAYO",
            "JUNIO",
            "JULIO",
            "AGOSTO",
            "SEPTIEMBRE",
            "OCTUBRE",
            "NOVIEMBRE",
            "DICIEMBRE"
        ]

        if periodo_obj.activo:
            startDate = periodo_obj.fecha_inicio
            endDate = datetime.date.today()
        else:
            startDate = periodo_obj.fecha_inicio
            endDate = periodo_obj.fecha_cierre

        params = {
            'empresa': empresa_obj,
            'balance_comprobacion': balance_comprobacion_qs,
            'periodo': "DEL %s DE %s AL %s DE %s DE %s" % (startDate.day, months[startDate.month], endDate.day, months[endDate.month], endDate.year)
        }

        pdf = render_to_pdf('contabilidad/informes/estado_resultados.html', params)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "estado_resultados.pdf"
            content = "inline; filename=%s" % (filename)
            download = request.GET.get("download")
            if download:
                content = "attachment; filename=%s" % (filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Error Rendering PDF", status=400)


class GenerateBalanceGeneralPDF(View):

    def get(self, request, *args, **kwargs):
        periodo_id = kwargs.get("pk")
        periodo_obj = PeriodoContable.objects.get(pk=periodo_id)
        company_id = periodo_obj.empresa_id
        empresa_obj = Empresa.objects.get(pk=company_id)

        # company_id = request.session['company_id']
        # empresa_obj = Empresa.objects.get(pk=company_id)
        balance_comprobacion_qs = BalanceComprobacion.objects.filter(empresa=empresa_obj)

        months = [
            "DESCONOCIDO",
            "ENERO",
            "FEBRERO",
            "MARZO",
            "ABROÑ",
            "MAYO",
            "JUNIO",
            "JULIO",
            "AGOSTO",
            "SEPTIEMBRE",
            "OCTUBRE",
            "NOVIEMBRE",
            "DICIEMBRE"
        ]

        if periodo_obj.activo:
            endDate = datetime.date.today()
        else:
            endDate = periodo_obj.fecha_cierre

        params = {
            'empresa': empresa_obj,
            'balance_comprobacion': balance_comprobacion_qs,
            'current_time': "AL %s DE %s DEL AÑO %s" % (endDate.day,
                                                        months[endDate.month],
                                                        endDate.year)
        }

        pdf = render_to_pdf('contabilidad/informes/balance_general.html', params)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "balance_general.pdf"
            content = "inline; filename=%s" % (filename)
            download = request.GET.get("download")
            if download:
                content = "attachment; filename=%s" % (filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Error Rendering PDF", status=400)


class LibroDiarioView(ListView):
    # model = LibroDiario
    # context_object_name = 'seats'
    # template_name = 'contabilidad/libros_contables/libro_diario.html'

    template_name = 'contabilidad/libros_contables/libro_diario.html'

    def get_queryset(self):
        return AsientoContable.objects.none()


def ajax_listado_asientos(request):
    from_date = request.POST.get("startDate")
    to_date = request.POST.get("endDate")
    # format_str = '%Y-%m-%d'
    # start_date = datetime.datetime.strptime(from_date, format_str)
    # end_date = datetime.datetime.strptime(to_date, format_str)
    current_company_id = request.session['company_id']

    try:
        query = """
            select a.fecha, a.numero_asiento as asiento, a.glosa, c.codigo, 'D' as movimiento, c.nombre as cuenta, null as parcial, d.monto as debe, null as haber
            from contabilidad_asientocontable a
            inner join contabilidad_asientodebedetalle d on d.asiento_id = a.id
            inner join contabilidad_plancuenta c on c.id = d.cuenta_id
            where a.empresa_id='%s' and a.fecha >= '%s' and a.fecha <= '%s'
            union
            select a.fecha, a.numero_asiento as asiento, a.glosa, c.codigo, 'H' as movimiento, c.nombre as cuenta, null as parcial, null as debe, h.monto as haber
            from contabilidad_asientocontable a
            inner join contabilidad_asientohaberdetalle h on h.asiento_id = a.id
            inner join contabilidad_plancuenta c on c.id = h.cuenta_id
            where a.empresa_id='%s' and a.fecha >= '%s' and a.fecha <= '%s'
            union
            select a.fecha, a.numero_asiento as asiento, a.glosa, c.codigo, p.movimiento, c.nombre as cuenta, cast(p.monto as text) as parcial, null as debe, null as haber
            from contabilidad_asientocontable a
            inner join contabilidad_asientoparcialdetalle p on p.asiento_id = a.id
            inner join contabilidad_plancuenta c on c.id = p.cuenta_id
            where a.empresa_id='%s' and a.fecha >= '%s' and a.fecha <= '%s'
            order by asiento, movimiento, codigo
        """ % (current_company_id, from_date, to_date,
                current_company_id, from_date, to_date,
                current_company_id, from_date, to_date)

    except ValueError:
        # ningún asiento seleccionado
        id_aux = 0
        query = """
            select a.fecha, a.numero_asiento as asiento, a.glosa, c.codigo, 'D' as movimiento, c.nombre as cuenta, null as parcial, d.monto as debe, null as haber
            from contabilidad_asientocontable a
            inner join contabilidad_asientodebedetalle d on d.asiento_id = a.id
            inner join contabilidad_plancuenta c on c.id = d.cuenta_id
            where a.id = '%s'
            union
            select a.fecha, a.numero_asiento as asiento, a.glosa, c.codigo, 'H' as movimiento, c.nombre as cuenta, null as parcial, null as debe, h.monto as haber
            from contabilidad_asientocontable a
            inner join contabilidad_asientohaberdetalle h on h.asiento_id = a.id
            inner join contabilidad_plancuenta c on c.id = h.cuenta_id
            where a.id = '%s'
            union
            select a.fecha, a.numero_asiento as asiento, a.glosa, c.codigo, p.movimiento, c.nombre as cuenta, cast(p.monto as text) as parcial, null as debe, null as haber
            from contabilidad_asientocontable a
            inner join contabilidad_asientoparcialdetalle p on p.asiento_id = a.id
            inner join contabilidad_plancuenta c on c.id = p.cuenta_id
            where a.id = '%s'
            order by asiento, movimiento, codigo
        """ % (id_aux)

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        results = []
        columns = (
            'fecha', 'asiento', 'glosa', 'codigo', 'movimiento', 'cuenta', 'parcial', 'debe', 'haber'
        )
        for row in rows:
            results.append(dict(zip(columns, row)))

    return JsonResponse(results, safe=False)


"""class CrearAsiento(CreateView):
    template_name = 'contabilidad/libros_contables/asiento.html'
    form_class = AsientoForm
    success_url = reverse_lazy('contabilidad:libro_diario')

    def form_valid(self, form):
        f = form.save(commit=False)
        f.usuario_creador = self.request.user
        f.save()
        return super(CrearCuenta, self).form_valid(form)"""


class CrearAsiento(ListView):
    template_name = 'contabilidad/libros_contables/asiento.html'

    def get_queryset(self):
        return AsientoContable.objects.none()

    def get(self, *args, **kwargs):
        current_company_id = self.request.session['company_id']
        periodo_obj = PeriodoContable.objects.filter(
            empresa_id=current_company_id, activo=True)
        if periodo_obj.exists():
            return super(CrearAsiento, self).get(*args, **kwargs)
        else:
            # return redirect('contabilidad:mensaje_periodo')
            return render(self.request, 'contabilidad/mensajes/message_period.html', {'activo': False})

    def get_context_data(self, **kwargs):
        context = super(CrearAsiento, self).get_context_data(**kwargs)

        today = datetime.date.today()
        context['fecha_asiento'] = format(today, '%Y-%m-%d')

        return context


def ajax_busqueda_cuentas_typeahead(request):
    if request.method == "GET":
        if request.is_ajax():
            # cuentas = Cuenta.objects.all().values('id', 'codigo', 'nombre')
            # cuentas = Cuenta.objects.filter(tipo='CUENTA').values('id', 'codigo', 'nombre')
            # cuentas = Cuenta.objects.filter(Q(tipo='CUENTA') | Q(tipo='SUBCUENTA') | Q(
            #    tipo='AUXILIAR')).values('id', 'codigo', 'nombre').exclude(parent__level=2)

            # cuentas = Cuenta.objects.filter(Q(tipo='CUENTA') | Q(tipo='SUBCUENTA') | Q(
            #    tipo='AUXILIAR')).values('codigo', 'nombre')

            cuentas = PlanCuenta.objects.filter(children__isnull=True).values('codigo', 'nombre')
            lista_cuentas = list(cuentas)  # important: convert the QuerySet to a list object
            return JsonResponse(lista_cuentas, safe=False)


def ajax_guardar_asiento(request):
    if request.method == 'POST':
        fecha = request.POST.get('fecha', None)
        glosa = request.POST.get('glosa', None)
        comprobante = request.POST.get('comprobante', None)
        mytableData = request.POST.get('pTableData', None)
        current_company_id = request.session['company_id']

        max_numero_asiento = AsientoContable.objects.filter(empresa_id=current_company_id).aggregate(
            max_asiento=Coalesce(Max('numero_asiento'), 0))['max_asiento']

        periodo_obj = PeriodoContable.objects.filter(empresa_id=current_company_id, activo=True)[0]

        # guardar asiento
        asiento = AsientoContable()
        asiento.numero_asiento = max_numero_asiento + 1
        asiento.fecha = fecha
        # asiento.debe =
        # asiento.haber =
        asiento.glosa = glosa
        asiento.comprobante = comprobante
        asiento.usuario_creador = request.user
        asiento.empresa_id = current_company_id
        asiento.periodo_id = periodo_obj.pk
        asiento.save()

        # JSON to Dict
        json_data = json.loads(mytableData)

        for key in json_data:
            # codigo_cuenta = key['codigo']
            cuenta_obj = PlanCuenta.objects.filter(
                codigo=key['codigo'], empresa_id=current_company_id)[0]
            monto_parcial = float(key['parcial']) if key['parcial'] != '' else 0
            monto_debe = float(key['debe']) if key['debe'] != '' else 0
            monto_haber = float(key['haber']) if key['haber'] != '' else 0
            parcial_movimiento = key['parcial_movimiento']
            if monto_debe > 0:
                debe = AsientoDebeDetalle(asiento_id=asiento.id,
                                          cuenta_id=cuenta_obj.pk, monto=monto_debe)
                debe.save()
            elif monto_haber > 0:
                haber = AsientoHaberDetalle(asiento_id=asiento.id,
                                            cuenta_id=cuenta_obj.pk, monto=monto_haber)
                haber.save()
            else:
                # monto parcial
                parcial = AsientoParcialDetalle(
                    asiento_id=asiento.id, cuenta_id=cuenta_obj.pk,
                    monto=monto_parcial, movimiento=parcial_movimiento)
                parcial.save()

        return JsonResponse({
            'success': True,
        })


class EditarAsiento(DetailView):
    model = AsientoContable
    template_name = 'contabilidad/libros_contables/asiento_editar.html'

    # def get_queryset(self):
    #    return AsientoContable.objects.none()

    def get_context_data(self, **kwargs):
        context = super(EditarAsiento, self).get_context_data(**kwargs)

        # today = datetime.date.today()
        # context['fecha_asiento'] = format(today, '%Y-%m-%d')

        total_debito = AsientoDebeDetalle.objects.filter(
            asiento_id=self.kwargs.get('pk')).aggregate(total=Sum('monto'))['total']
        if not total_debito:
            total_debito = 0

        total_credito = AsientoHaberDetalle.objects.filter(
            asiento_id=self.kwargs.get('pk')).aggregate(total=Sum('monto'))['total']
        if not total_credito:
            total_credito = 0

        # context['seats'] = AsientoContable.objects.filter(pk=self.kwargs.get('pk'))
        context['debit_details'] = AsientoDebeDetalle.objects.filter(
            asiento_id=self.kwargs.get('pk'))
        context['credit_details'] = AsientoHaberDetalle.objects.filter(
            asiento_id=self.kwargs.get('pk'))
        context['total_debito'] = total_debito
        context['total_credito'] = total_credito

        return context


class EliminarAsiento(DeleteView):
    model = AsientoContable
    template_name = 'contabilidad/libros_contables/eliminar_asiento.html'
    success_url = reverse_lazy('contabilidad:libro_diario')


def asiento_agregar_cuenta(request):
    if request.method == 'GET':
        getVar = request.GET.get('id', None)

        return JsonResponse({
            'success': True,
        })
    else:  # request.method == 'POST'
        data = request.POST.copy()
        itemID = data.get('id')
        cantidad = data.get('qty')
        unidad = data.get('unit')
        precio = data.get('price')

        return JsonResponse({
            'success': False,
        })


class ResumenSRI(ListView):

    template_name = 'contabilidad/reportes/resumen_ats.html'
    #template_name = 'contabilidad/resumen_ats.html'

    def get_queryset(self):
        query = self.request.GET.get("periodo_fiscal")
        current_company_id = self.request.session['company_id']
        if query:

            # query = May,2020
            datetime_str = "1,%s" % query
            format_str = '%d,%b.,%Y'

            now = datetime.datetime.strptime(datetime_str, format_str)
            start_month = datetime.datetime(now.year, now.month, 1)

            import calendar
            end_month = datetime.datetime(now.year, now.month, 1) + \
                datetime.timedelta(days=calendar.monthrange(
                    now.year, now.month)[1] - 1)
        else:
            #start_date = datetime.date.today()
            # start_date.replace(day=1)
            now = datetime.datetime.now()
            start_month = datetime.datetime(now.year, now.month, 1)

            import calendar
            end_month = datetime.datetime(now.year, now.month, 1) + \
                datetime.timedelta(days=calendar.monthrange(
                    now.year, now.month)[1] - 1)

        from django.db.models import CharField
        from django.db.models.functions import Length
        CharField.register_lookup(Length)

        factelectr_list = Factura.objects.filter(created_at__date__range=(
            start_month, end_month), empresa_id=current_company_id,
            clave_acceso__length__gte=49).values('clave_acceso', 'valor_total').order_by('-clave_acceso')
        total_factelectr = sum(factura["valor_total"] for factura in factelectr_list)

        factfis_list = Factura.objects.filter(created_at__date__range=(
            start_month, end_month), empresa_id=current_company_id,
            clave_acceso__length__lt=49).values('factura_id', 'valor_total').order_by('-factura_id')
        total_factfis = sum(factura["valor_total"] for factura in factfis_list)

        retefuente_list = ComprobanteRetencion.objects.filter(created_at__date__range=(
            start_month, end_month), empresa_id=current_company_id,
            clave_acceso__length__lt=49).values('comprobante_retencion_id', 'valor_total').order_by('-comprobante_retencion_id')
        total_retefuente = sum(factura["valor_total"] for factura in retefuente_list)

        compras_list = OrdenCompra.objects.filter(created_at__date__range=(
            start_month, end_month), empresa_id=current_company_id).values('orden_id', 'valor_total').order_by('-orden_id')
        total_compras = sum(factura["valor_total"] for factura in compras_list)

        ventas_list = Factura.objects.filter(created_at__date__range=(
            start_month, end_month), empresa_id=current_company_id).values('factura_id', 'valor_total').order_by('-factura_id')
        total_ventas = sum(factura["valor_total"] for factura in ventas_list)

        retencion_iva_list = ComprobanteRetencionDetalle.objects.filter(retencion__fecha_emision__date__range=(
            start_month, end_month), tipo_impuesto=2, retencion__empresa_id=current_company_id)

        reteiva_set_30porc = retencion_iva_list.filter(sri_tipo_impuesto__codigo='1')
        reteiva_set_70porc = retencion_iva_list.filter(sri_tipo_impuesto__codigo='2')
        reteiva_set_100porc = retencion_iva_list.filter(sri_tipo_impuesto__codigo='3')

        sum_reteiva_30porc = sum(retencion.valor_total for retencion in reteiva_set_30porc)
        sum_reteiva_70porc = sum(retencion.valor_total for retencion in reteiva_set_70porc)
        sum_reteiva_100porc = sum(retencion.valor_total for retencion in reteiva_set_100porc)

        total_reteiva = sum_reteiva_30porc + sum_reteiva_70porc + sum_reteiva_100porc
        rete_iva_dict = {'30_PORC': sum_reteiva_30porc, '70_PORC': sum_reteiva_70porc,
                         '100_PORC': sum_reteiva_100porc, 'TOTAL': total_reteiva}

        retencion_renta_list = ComprobanteRetencionDetalle.objects.filter(retencion__fecha_emision__date__range=(
            start_month, end_month), tipo_impuesto=1, retencion__empresa_id=current_company_id)

        retefuente_set_1porc = retencion_renta_list.filter(sri_tipo_impuesto__porcentaje=1)
        retefuente_set_2porc = retencion_renta_list.filter(sri_tipo_impuesto__porcentaje=2)
        retefuente_set_5porc = retencion_renta_list.filter(sri_tipo_impuesto__porcentaje=5)
        retefuente_set_8porc = retencion_renta_list.filter(sri_tipo_impuesto__porcentaje=8)
        retefuente_set_10porc = retencion_renta_list.filter(sri_tipo_impuesto__porcentaje=10)

        sum_porc_1porc = sum(retencion.valor_total for retencion in retefuente_set_1porc)
        sum_porc_2porc = sum(retencion.valor_total for retencion in retefuente_set_2porc)
        sum_porc_5porc = sum(retencion.valor_total for retencion in retefuente_set_5porc)
        sum_porc_8porc = sum(retencion.valor_total for retencion in retefuente_set_8porc)
        sum_porc_10porc = sum(retencion.valor_total for retencion in retefuente_set_10porc)

        total_porc = sum_porc_1porc + sum_porc_2porc + sum_porc_5porc + sum_porc_8porc + sum_porc_10porc
        rete_porc_dict = {'1%': sum_porc_1porc, '2%': sum_porc_2porc, '5%': sum_porc_5porc,
                          '8%': sum_porc_8porc, '10%': sum_porc_10porc, 'TOTAL': total_porc}

        context = {
            'factelectr_list': factelectr_list,
            'total_factelectr': total_factelectr,
            'factfis_list': factfis_list,
            'total_factfis': total_factfis,
            'retefuente_list': retefuente_list,
            'total_retefuente': total_retefuente,
            'compras_list': compras_list,
            'total_compras': total_compras,
            'ventas_list': ventas_list,
            'total_ventas': total_ventas,
            'rete_iva_dict': rete_iva_dict,
            'rete_porc_dict': rete_porc_dict
        }

        return context


class ResumenAtsPdf(View):
    def get(self, request, *args, **kwargs):
        periodo_fiscal = kwargs.get("periodo_fiscal")
        company_id = request.session['company_id']
        empresa_obj = Empresa.objects.get(pk=company_id)

        # periodo_fiscal = May,2020
        datetime_str = "1,%s" % periodo_fiscal
        format_str = '%d,%b.,%Y'
        now = datetime.datetime.strptime(datetime_str, format_str)
        start_month = datetime.datetime(now.year, now.month, 1)

        import calendar
        end_month = datetime.datetime(now.year, now.month, 1) + \
            datetime.timedelta(days=calendar.monthrange(
                now.year, now.month)[1] - 1)

        today = timezone.now()
        current_company_id = self.request.session['company_id']

        compras_obj = OrdenCompra.objects.filter(fecha_emision__date__range=(
            start_month, end_month), empresa_id=current_company_id)  # .values('orden_id', 'valor_total').order_by('-orden_id')

        # retenciones_obj = ComprobanteRetencion.objects.filter(fecha_emision__date__range=(
        #    start_month, end_month), empresa_id=current_company_id,
        #    clave_acceso__length__lt=49)  # .values('comprobante_retencion_id', 'valor_total').order_by('-comprobante_retencion_id')

        '''
        retefuente_renta_obj = ComprobanteRetencionDetalle.objects.filter(retencion__fecha_emision__date__range=(
            start_month, end_month), tipo_impuesto=1, retencion__empresa_id=current_company_id)
        retefuente_iva_obj = ComprobanteRetencionDetalle.objects.filter(retencion__fecha_emision__date__range=(
            start_month, end_month), tipo_impuesto=2, retencion__empresa_id=current_company_id)
        '''

        from django.db.models import Count
        from django.db.models import F

        retefuente_renta_obj = ComprobanteRetencionDetalle.objects.filter(
            retencion__fecha_emision__date__range=(
                start_month, end_month), tipo_impuesto=1,
            retencion__empresa_id=current_company_id).values(
                'sri_tipo_impuesto__codigo').annotate(
                    descripcion=F('sri_tipo_impuesto__descripcion'),
                    nro_registros=Coalesce(Count('pk'), 0),
                    sum_base_imponible=Coalesce(Sum('valor_base_imponible'), 0),
                    sum_valor_retenido=Coalesce(Sum('valor_total'), 0)
        )

        retefuente_iva_obj = ComprobanteRetencionDetalle.objects.filter(
            retencion__fecha_emision__date__range=(
                start_month, end_month), tipo_impuesto=2,
            retencion__empresa_id=current_company_id).values(
                'sri_tipo_impuesto__descripcion'
        ).annotate(
            sum_base_imponible=Coalesce(Sum('valor_base_imponible'), 0),
            sum_valor_retenido=Coalesce(Sum('valor_total'), 0)
        )
        # group by --> annotate()
        # SELECT filed as X... --> annotate(sth_shiny=F('my_field'))
        # print("SQL QUERY")
        # print(retefuente_renta_obj.query)
        # print(retefuente_renta_obj)

        print("RETENCIONES IVA.....")
        print(retefuente_iva_obj.query)
        print(retefuente_iva_obj)

        """
        query = '''select row_number() OVER () as id,
            ti.codigo,
            ti.descripcion,
            count(retefd.sri_tipo_comprobante_modificado_id) as nro_registros,
            sum(retefd.valor_base_imponible) as base_imponible,
            sum(retefd.valor_total) as valor_retenido
            from retencion_comprobanteretenciondetalle retefd
                inner join retencion_comprobanteretencion ret on retefd.retencion_id = ret.comprobante_retencion_id
                inner join sri_sritipoimpuesto ti on retefd.sri_tipo_impuesto_id = ti.sri_tipo_impuesto_id
            where retefd.tipo_impuesto = 1
                and ret.empresa_id = %s
                and cast(ret.fecha_emision as date) between '%s' and '%s'
            group by codigo, descripcion
            ''' % (current_company_id, start_month, end_month)

        with connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            all_retef_items = []
            columns = (
                'id', 'codigo', 'descripcion', 'nro_registros', 'base_imponible', 'valor_retenido'
            )
            for row in rows:
                all_retef_items.append(dict(zip(columns, row)))
        """

        params = {
            'today': today,
            'periodo': '%s-%s' % ('{:02d}'.format(now.month), now.year),
            'empresa': empresa_obj,
            'compras_list': compras_obj,
            'retef_renta_list': retefuente_renta_obj,
            'retef_iva_list': retefuente_iva_obj,
            'request': request
        }
        return render_to_pdf('contabilidad/reportes/resumen_ats_pdf.html', params)


def resumen_sri_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="resumen sri.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Resumen SRI')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Comprobante', 'Total']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    rows = OrdenCompra.objects.all().values_list('orden_id', 'valor_total')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response


class ListadoAsientosAutomaticos(ListView):
    template_name = 'contabilidad/asiento_automatico/listado_asientos_automaticos.html'

    def get_queryset(self):
        return AsientoAutomatico.objects.none()


def ajax_asiento_automatico(request):
    if request.method == 'POST':
        if request.is_ajax():
            current_company_id = request.session['company_id']
            grupo_asiento = request.POST.get('grupo_asiento', None)
            if grupo_asiento == '0':  # Todos los asientos automáticos
                query = """
                    select a.codigo_enlace, a.grupo_asiento, a.descripcion, c.codigo, c.nombre as cuenta, a.debito, a.credito
                    from contabilidad_asientoautomatico a
                    left join contabilidad_plancuenta c on a.cuenta_id = c.id
                    where a.empresa_id = '%s'
                    order by a.grupo_asiento, a.credito, a.descripcion
                """ % (current_company_id)
            elif grupo_asiento != '':  # Filtrar por grupo
                query = """
                    select a.codigo_enlace, a.grupo_asiento, a.descripcion, c.codigo, c.nombre as cuenta, a.debito, a.credito
                    from contabilidad_asientoautomatico a
                    left join contabilidad_plancuenta c on a.cuenta_id = c.id
                    where a.empresa_id = '%s' and a.grupo_asiento = '%s'
                    order by a.grupo_asiento, a.credito, a.descripcion
                """ % (current_company_id, grupo_asiento)
            else:
                # ningún asiento seleccionado
                id_aux = 0
                query = """
                    select a.codigo_enlace, a.grupo_asiento, a.descripcion, c.codigo, c.nombre as cuenta, a.debito, a.credito
                    from contabilidad_asientoautomatico a
                    left join contabilidad_plancuenta c on a.cuenta_id = c.id
                    where a.grupo_asiento = '%s'
                    order by a.grupo_asiento, a.credito, a.descripcion
                """ % (id_aux)

            with connection.cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
                results = []
                columns = (
                    'codigo_enlace', 'grupo_asiento', 'descripcion', 'codigo', 'cuenta', 'debito', 'credito'
                )
                for row in rows:
                    results.append(dict(zip(columns, row)))
            return JsonResponse(results, safe=False)


class EditarAsientoAutomatico(UpdateView):
    model = AsientoAutomatico
    template_name = 'contabilidad/asiento_automatico/editar_asiento_automatico.html'
    form_class = AsientoAutomaticoForm
    success_url = reverse_lazy('contabilidad:listado_asientos_automaticos')


def ajax_tree_cuentas(request):
    """lista_cuentas = [
        {"title": "Books", "expanded": True, "folder": True, "children": [
            {"title": "Art of War", "type": "book", "author": "Sun Tzu",
                "year": -500, "qty": 21, "price": 5.95},
            {"title": "The Hobbit", "type": "book", "author": "J.R.R. Tolkien",
                "year": 1937, "qty": 32, "price": 8.97},
            {"title": "The Little Prince", "type": "book",
                "author": "Antoine de Saint-Exupery", "year": 1943, "qty": 2946, "price": 6.82},
            {"title": "Don Quixote", "type": "book", "author": "Miguel de Cervantes",
                "year": 1615, "qty": 932, "price": 15.99}
        ]},
        {"title": "Music", "folder": True, "children": [
            {"title": "Nevermind", "type": "music", "author": "Nirvana",
                "year": 1991, "qty": 916, "price": 15.95},
            {"title": "Autobahn", "type": "music", "author": "Kraftwerk",
                "year": 1974, "qty": 2261, "price": 23.98},
            {"title": "Kind of Blue", "type": "music", "author": "Miles Davis",
                "year": 1959, "qty": 9735, "price": 21.90},
            {"title": "Back in Black", "type": "music", "author": "AC/DC",
                "year": 1980, "qty": 3895, "price": 17.99},
            {"title": "The Dark Side of the Moon", "type": "music",
                "author": "Pink Floyd", "year": 1973, "qty": 263, "price": 17.99},
            {"title": "Sgt. Pepper's Lonely Hearts Club Band", "type": "music",
                "author": "The Beatles", "year": 1967, "qty": 521, "price": 13.98}
        ]},
        {"title": "Electronics & Computers", "expanded": True, "folder": True, "children": [
            {"title": "Cell Phones", "folder": True, "children": [
                {"title": "Moto G", "type": "phone", "author": "Motorola",
                    "year": 2014, "qty": 332, "price": 224.99},
                {"title": "Galaxy S8", "type": "phone", "author": "Samsung",
                    "year": 2016, "qty": 952, "price": 509.99},
                {"title": "iPhone SE", "type": "phone", "author": "Apple",
                    "year": 2016, "qty": 444, "price": 282.75},
                {"title": "G6", "type": "phone", "author": "LG",
                    "year": 2017, "qty": 951, "price": 309.99},
                {"title": "Lumia", "type": "phone", "author": "Microsoft",
                    "year": 2014, "qty": 32, "price": 205.95},
                {"title": "Xperia", "type": "phone", "author": "Sony",
                    "year": 2014, "qty": 77, "price": 195.95},
                {"title": "3210", "type": "phone", "author": "Nokia",
                    "year": 1999, "qty": 3, "price": 85.99}
            ]},
            {"title": "Computers", "folder": True, "children": [
                {"title": "ThinkPad", "type": "computer", "author": "IBM",
                    "year": 1992, "qty": 16, "price": 749.90},
                {"title": "C64", "type": "computer", "author": "Commodore",
                    "year": 1982, "qty": 83, "price": 595.00},
                {"title": "MacBook Pro", "type": "computer", "author": "Apple",
                    "year": 2006, "qty": 482, "price": 1949.95},
                {"title": "Sinclair ZX Spectrum", "type": "computer",
                    "author": "Sinclair Research", "year": 1982, "qty": 1, "price": 529},
                {"title": "Apple II", "type": "computer", "author": "Apple",
                    "year": 1977, "qty": 17, "price": 1298},
                {"title": "PC AT", "type": "computer", "author": "IBM",
                    "year": 1984, "qty": 3, "price": 1235.00}
            ]}
        ]},
        {"title": "More...", "folder": True, "lazy": True}
    ]
    return JsonResponse(lista_cuentas, safe=False)
    """

    """result = []
    cuentas_activo = Cuenta.objects.filter(
        clasificacion='ACTIVO', level__gt=0).values('id', 'codigo', 'nombre')
    if (len(cuentas_activo) > 0):
        children = []

        for value in cuentas_activo:
            children.append({
                'title': value["nombre"],
                'type': 'activo',
                'saldo': '0',
            })

        result.append({
            "title": "ACTIVO",
            "expanded": True,
            "folder": True,
            "children": children
        })"""

    result = []
    # root_nodes_obj = Cuenta.objects.filter(level=0).values('id', 'codigo', 'nombre')
    root_nodes_obj = PlanCuenta.objects.filter(level=0)
    if (len(root_nodes_obj) > 0):

        for level0 in root_nodes_obj:

            level1_obj = root_nodes_obj.get_descendants().filter(
                clasificacion=level0.clasificacion, level__lte=level0.level + 1)
            children_level1 = []

            for level1 in level1_obj:

                level2_obj = level1_obj.get_descendants().filter(
                    parent_id=level1.pk, level__lte=level1.level + 1)
                children_level2 = []

                for level2 in level2_obj:

                    level3_obj = level2_obj.get_descendants().filter(
                        parent_id=level2.pk, level__lte=level2.level + 1)

                    if level3_obj:

                        children_level3 = []
                        for level3 in level3_obj:
                            children_level3.append({
                                'title': level3.nombre,
                                'type': level3.parent.nombre,
                                'saldo': '0',
                            })

                        children_level2.append({
                            'title': level2.nombre,
                            "expanded": False,
                            "folder": True,
                            "children": children_level3
                        })
                    else:
                        children_level2.append({
                            'title': level2.nombre,
                            'type': level2.parent.nombre,
                            'saldo': '0',
                        })

                # children nivel 1
                children_level1.append({
                    "title": level1.nombre,
                    "expanded": False,
                    "folder": True,
                    "children": children_level2
                })

            # root
            result.append({
                "title": level0.nombre,
                "expanded": False,
                "folder": True,
                "children": children_level1
            })

    print(result)
    return JsonResponse(result, safe=False)


def ajax_listado_cuentas(request):
    """lista_cuentas = [
        {"name": "ACTIVO", "children": [
            {"name": "Suri", "children": [{"name": "Javiercito"}]},
            {"name": "Paula"}
        ]},
        {"name": "Inés", "children": [
            {"name": "Paula"},
            {"name": "Suri"}
        ]},
    ]
    print(lista_cuentas)
    return JsonResponse(lista_cuentas, safe=False)"""

    '''cuentas = Cuenta.objects.raw("""
    select *
    from contabilidad_cuenta
    where level = 0
    order by codigo
    """)

    result = []
    for t in cuentas:
        result.append({
            'codigo': t.codigo,
            'nombre': t.nombre,
            'children': ""
        })
    data = json.dumps(result)
    return HttpResponse(data, content_type='application/json')'''

    result = []
    # root_nodes_obj = Cuenta.objects.filter(level=0).values('id', 'codigo', 'nombre')
    root_nodes_obj = PlanCuenta.objects.filter(level=0)
    if (len(root_nodes_obj) > 0):

        for level_0 in root_nodes_obj:

            level1_obj = root_nodes_obj.get_descendants().filter(
                clasificacion=level_0.clasificacion, level__lte=level_0.level + 1)
            children_level1 = []

            for level_1 in level1_obj:

                level2_obj = level1_obj.get_descendants().filter(
                    parent_id=level_1.pk, level__lte=level_1.level + 1)
                children_level2 = []

                for level_2 in level2_obj:

                    level3_obj = level2_obj.get_descendants().filter(
                        parent_id=level_2.pk, level__lte=level_2.level + 1)
                    children_level3 = []

                    for level_3 in level3_obj:

                        level4_obj = level3_obj.get_descendants().filter(
                            parent_id=level_3.pk, level__lte=level_3.level + 1)

                        if level4_obj:

                            children_level4 = []
                            for level_4 in level4_obj:
                                children_level4.append({
                                    'codigo': level_4.codigo,
                                    'nombre': level_4.nombre,
                                    "children": ""
                                })

                            children_level3.append({
                                'codigo': level_3.codigo,
                                'nombre': level_3.nombre,
                                "children": children_level4
                            })
                        else:
                            children_level3.append({
                                'codigo': level_3.codigo,
                                'nombre': level_3.nombre,
                                "children": ""
                            })

                    # children level 2
                    children_level2.append({
                        "codigo": level_2.codigo,
                        "nombre": level_2.nombre,
                        "children": children_level3
                    })

                # children level 1
                children_level1.append({
                    "codigo": level_1.codigo,
                    "nombre": level_1.nombre,
                    "children": children_level2
                })

            # children level 0
            result.append({
                "codigo": level_0.codigo,
                "nombre": level_0.nombre,
                "children": children_level1
            })

    print(result)
    return JsonResponse(result, safe=False)


""""
def prueba(request):
    form = SelectionForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            selection = form.save()
            return redirect('selection', pk=selection.pk)
    selections = Selection.objects.all()
    return render(request, "contabilidad/cuentas/prueba.html", {'form': form, 'selections': selections})

def selection(request, pk):
    selection = get_object_or_404(Selection, pk=pk)
    if request.method == "POST":
        form = SelectionForm(request.POST, instance=selection)
        if form.is_valid():
            selection = form.save()
            return redirect('selection', pk=selection.pk)
    else:
        form = SelectionForm(instance=selection)
    selections = Selection.objects.all()
    return render(request, "home.html", {'form': form, 'selections': selections})
"""


def ajaxBuscarCuentaDB(request):
    if request.method == "GET":
        if request.is_ajax():
            search_string = request.GET.get('search_string', None)

            # item.creator = owner or item.moderated = False
            # cuenta_obj = Cuenta.objects.filter(
            #    Q(nombre=search_string) | Q(codigo=search_string) & (Q(tipo='CUENTA') | Q(tipo='AUXILIAR')))

            # cuenta_obj = Cuenta.objects.filter(
            #    Q(nombre=search_string) | Q(codigo=search_string), Q(tipo="CUENTA") | Q(tipo='SUBCUENTA') | Q(tipo='AUXILIAR'))

            cuenta_obj = PlanCuenta.objects.filter(
                Q(nombre=search_string) | Q(codigo=search_string) & (Q(children__isnull=True)))

            if cuenta_obj.exists():
                if cuenta_obj[0].tipo == "AUXILIAR":
                    return JsonResponse({
                        'success': True,
                        'auxiliar_codigo': cuenta_obj[0].codigo,
                        'auxiliar_nombre': cuenta_obj[0].nombre,
                        'code': cuenta_obj[0].parent.codigo,
                        'account': cuenta_obj[0].parent.nombre,
                    })
                else:
                    return JsonResponse({
                        'success': True,
                        'account': cuenta_obj[0].nombre,
                        # 'accountId': cuenta_obj[0].id,
                        'code': cuenta_obj[0].codigo,
                        'auxiliar_codigo': '',
                        'auxiliar_nombre': ''
                    })
            else:
                return JsonResponse({
                    'success': False,
                })


def ajax_actualizar_asiento(request):
    if request.method == 'POST':
        data = request.POST.copy()
        asiento_id = data.get('asiento_id')
        fecha = data.get('fecha')
        glosa = data.get('glosa')
        comprobante = data.get('comprobante')
        mytableData = data.get('pTableData')

        asiento = AsientoContable.objects.get(pk=asiento_id)
        asiento.fecha = fecha
        asiento.glosa = glosa
        asiento.comprobante = comprobante
        asiento.usuario_creador = request.user
        asiento.save()

        # eliminar detalles débito y crédito
        AsientoDebeDetalle.objects.filter(asiento_id=asiento_id).delete()
        AsientoHaberDetalle.objects.filter(asiento_id=asiento_id).delete()

        # JSON to Dict
        json_data = json.loads(mytableData)
        for key in json_data:
            cuenta_id = int(key['id'])
            monto_debe = float(key['debito']) if key['debito'] != '' else 0
            monto_haber = float(key['credito']) if key['credito'] != '' else 0

            if monto_debe > 0:
                debe = AsientoDebeDetalle(asiento_id=asiento.id,
                                          cuenta_id=cuenta_id, monto=monto_debe)
                debe.save()
            else:
                haber = AsientoHaberDetalle(asiento_id=asiento.id,
                                            cuenta_id=cuenta_id, monto=monto_haber)
                haber.save()

        return JsonResponse({
            'success': True,
            'url': '../libro_diario'
        })
