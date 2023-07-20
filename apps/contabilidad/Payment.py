import json  # soporte Json
import datetime
from decimal import Decimal

from apps.administracion import utils
from apps.administracion.models import EntidadFinanciera, TarjetaBancaria
from apps.sri.models import SriFormaPago, SriTipoMoneda

from .models import Turno, Pago, FormaPago, EstadoPago, \
    PagoTransferencia, PagoCheque, EstadoCheque, PagoTarjeta, PagoCredito, \
    EstadoCredito, AsientoContable, AsientoAutomatico

# Create your views here.


class Payment():

    def procesar(self):
        turno_obj = Turno.objects.filter(usuario_creador=self.usuario, activo=True)[0]

        # JSON to Dict
        json_data = json.loads(self.tabla)

        ptr_pago_credito = Pago()

        # buscar Retención
        total_valor_retenido = 0
        for key in json_data:
            if key["ptype"] == "RT":
                total_valor_retenido = total_valor_retenido + Decimal(key["valor_retenido"])

        for key in json_data:
            if key["ptype"] != "RT":
                app_forma_pago_obj = FormaPago.objects.filter(codigo=key["ptype"])[0]
                sri_forma_pago_obj = SriFormaPago.objects.filter(
                    codigo=app_forma_pago_obj.sri_codigo)[0]
                sri_tipo_moneda_obj = SriTipoMoneda.objects.filter(codigo='DOLAR')[0]
                estado_pago_obj = EstadoPago.objects.filter(situacion='Confirmado')[0]

                if self.tipo_flujo == 'DEBE':
                    pto_establecimiento = self.orden.secuencia.punto_establecimiento
                    pto_emision = self.orden.secuencia.punto_emision
                    sec_formateado = self.orden.get_numero_secuencia_formateado()
                    numero_comprobante = "%s-%s-%s" % (pto_establecimiento,
                                                       pto_emision, sec_formateado)
                else:
                    numero_comprobante = self.orden.numero_comprobante

                if key["ptype"] == "CC":
                    if key["record"] == 'T':
                        pago = Pago()
                        pago.turno = turno_obj
                        pago.usuario = self.usuario
                        pago.app_forma_pago = app_forma_pago_obj
                        pago.sri_forma_pago = sri_forma_pago_obj
                        pago.sri_tipo_moneda = sri_tipo_moneda_obj
                        pago.referencia = self.referencia
                        pago.estado = estado_pago_obj
                        pago.tipo_flujo = utils.flow_dictionary[self.tipo_flujo]

                        pago.orden_id = self.orden.pk
                        pago.numero_comprobante = numero_comprobante

                        if (self.referencia == "Compra"):
                            pago.proveedor = self.orden.proveedor
                        elif (self.referencia == "Venta") or (self.referencia == "Nota Entrega"):
                            pago.cliente = self.orden.cliente

                        '''if (self.referencia == "Compra"):
                            pago.compra_id = self.orden.pk
                        elif (self.referencia == "Venta"):
                            pago.venta_id = self.orden.pk
                        elif (self.referencia == "Proforma"):
                            pago.proforma_id = self.orden.pk'''

                        pago.importe = key["monto"]
                        pago.valor_retenido = total_valor_retenido
                        pago.empresa = self.orden.empresa
                        pago.save()

                        # guardar en tabla crédito
                        ptr_pago_credito = pago
                        self.registrarCredito(ptr_pago_credito, key)
                    else:
                        # guardar en tabla crédito
                        self.registrarCredito(ptr_pago_credito, key)

                else:
                    pago = Pago()
                    pago.turno = turno_obj
                    pago.usuario = self.usuario
                    pago.app_forma_pago = app_forma_pago_obj
                    pago.sri_forma_pago = sri_forma_pago_obj
                    pago.sri_tipo_moneda = sri_tipo_moneda_obj
                    pago.estado = estado_pago_obj
                    pago.tipo_flujo = utils.flow_dictionary[self.tipo_flujo]

                    pago.orden_id = self.orden.pk
                    pago.numero_comprobante = numero_comprobante

                    if (self.referencia == "Compra" or self.referencia == "Cuentas por pagar"):
                        pago.proveedor = self.orden.proveedor
                    elif (self.referencia == "Venta") or (self.referencia == "Nota Entrega") or (self.referencia == "Cuentas por cobrar"):
                        pago.cliente = self.orden.cliente

                    '''if (self.referencia == "Compra" or self.referencia == "Cuentas por pagar"):
                        pago.compra_id = self.orden.pk
                    elif (self.referencia == "Venta" or self.referencia == "Cuentas por cobrar"):
                        pago.venta_id = self.orden.pk
                    elif (self.referencia == "Proforma" or self.referencia == "Cuentas por cobrar proforma"):
                        pago.proforma_id == self.orden.pk'''

                    pago.importe = key["monto"]
                    pago.valor_retenido = total_valor_retenido
                    pago.referencia = self.referencia
                    pago.empresa = self.orden.empresa
                    pago.save()

                    if key["ptype"] == "TB":
                        self.registrarTransferencia(pago, key)
                    elif key["ptype"] == "CH":
                        self.registrarCheque(pago, key)
                    elif key["ptype"] == "TD":
                        self.registrarTarjeta(pago, key, "TD")
                    elif key["ptype"] == "TC":
                        self.registrarTarjeta(pago, key, "TC")

        return True

    def registrarTransferencia(self, pago, key):
        banco_origen_obj = EntidadFinanciera.objects.filter(nombre=key["banco_origen"])[0]
        banco_destino_obj = EntidadFinanciera.objects.filter(nombre=key["banco_destino"])[0]

        transf = PagoTransferencia()
        transf.pago = pago
        transf.banco_origen = banco_origen_obj
        transf.cta_origen = key["cta_origen"]
        #transf.titular = key["titular"]
        transf.banco_destino = banco_destino_obj
        transf.cta_destino = key["cta_destino"]
        transf.fecha_transf = key["fecha_transf"]
        transf.monto = key["monto"]
        transf.save()

        return True

    def registrarCheque(self, pago, key):
        banco_obj = EntidadFinanciera.objects.filter(nombre=key["banco"])[0]
        if (self.referencia == "Compra" or self.referencia == "Cuentas por pagar"):
            situacion_obj = EstadoCheque.objects.get(pk=utils.situation_dictionary["GIRADO"])
        elif (self.referencia == "Venta" or self.referencia == "Cuentas por cobrar"):
            situacion_obj = EstadoCheque.objects.get(pk=utils.situation_dictionary["CARTERA"])

        cheq = PagoCheque()
        cheq.pago = pago
        cheq.banco = banco_obj
        cheq.cuenta_nro = key["cuenta_nro"]
        cheq.cheque_nro = key["cheque_nro"]
        #cheq.titular = key["titular"]
        cheq.fecha_cheq = key["fecha_cheq"]
        cheq.estado = situacion_obj
        cheq.monto = key["monto"]
        cheq.save()

        return True

    def registrarTarjeta(self, pago, key, type):
        tarjeta_obj = TarjetaBancaria.objects.filter(nombre=key["tarjeta"])[0]

        tarjeta = PagoTarjeta()
        tarjeta.pago = pago
        tarjeta.tarjeta = tarjeta_obj
        tarjeta.tipo_tarjeta = key["tipo_tarjeta"]
        #tarjeta.titular = key["titular"]
        tarjeta.tarjeta_nro = key["tarjeta_nro"]
        #tarjeta.expira = key["expira"]
        #tarjeta.modalidad = key["modalidad"]
        #tarjeta.plazo = key["plazo"]
        tarjeta.vaucher = key["vaucher_nro"]
        tarjeta.monto = key["monto"]
        tarjeta.save()

        return True

    def registrarCredito(self, pago, key):
        estado_credito_obj = EstadoCredito.objects.filter(situacion='Vigente')[0]

        #num_cuotas = int(key["num_cuotas"])
        #plazo = int(key["plazo"])
        #intervalo_cuotas = plazo / num_cuotas

        # crea fecha de corte
        fecha_corte = key["corte"]
        # date_str = fecha_corte  # The date - 24-Mar-2019
        # format_str = '%d-%b-%Y'  # The format 31-Sep-2029

        date_str = fecha_corte  # The date - 2020-03-13
        format_str = '%Y-%m-%d'  # The format 2020-03-13
        datetime_obj = datetime.datetime.strptime(date_str, format_str)

        """for i in range(0, num_cuotas):
            if (i > 0):
                if utils.time_dictionary[key["unidad_tiempo"]] == "D":
                    # Add n days
                    vence = datetime_obj + timedelta(days=(intervalo_cuotas * i))
                elif utils.time_dictionary[key["unidad_tiempo"]] == "M":
                    vence = datetime_obj + timedelta(days=(30 * i))
                else:
                    vence = vence = datetime_obj + timedelta(days=(365 * i))
            else:
                vence = fecha_corte

            credito = Credito()
            credito.pago = pago
            credito.valor_credito = key["monto"]
            credito.plazo = plazo
            credito.unidad_tiempo = utils.time_dictionary[key["unidad_tiempo"]]
            credito.num_cuotas = num_cuotas
            credito.tasa_interes = key["tasa_interes"]
            credito.cuota_nro = i + 1
            credito.vence = vence
            credito.estado = estado_credito_obj
            credito.valor_cuota = key["cuota"]
            credito.abono = 0
            credito.saldo = key["cuota"]
            credito.save()"""

        credito = PagoCredito()
        credito.pago = pago
        credito.valor_credito = key["monto"]
        credito.plazo = key["plazo"]
        credito.unidad_tiempo = utils.time_dictionary[key["unidad_tiempo"]]
        credito.num_cuotas = key["num_cuotas"]
        credito.tasa_interes = key["tasa_interes"]
        credito.cuota_nro = key["nro"]
        credito.vence = datetime_obj
        credito.estado = estado_credito_obj
        credito.valor_cuota = key["cuota"]
        valor_retenido = 0
        if (int(key["nro"]) == 1):  # Retención en la primera cuota
            credito.valor_retenido = pago.valor_retenido
            valor_retenido = pago.valor_retenido
        else:
            valor_retenido = 0
        credito.abono = 0
        credito.saldo = Decimal(key["cuota"]) - valor_retenido
        credito.empresa = self.orden.empresa
        credito.save()

        return True

    def __init__(self, current_user, tipo_flujo, referencia, tabla, orden):
        self.usuario = current_user
        self.tipo_flujo = tipo_flujo
        self.referencia = referencia
        self.tabla = tabla
        self.orden = orden
