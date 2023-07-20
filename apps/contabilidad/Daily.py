import json  # soporte Json
import datetime
from decimal import Decimal

from django.db.models import Sum
from django.db.models.functions import Coalesce

from .models import AsientoAutomatico, AsientoContable, \
    AsientoDebeDetalle, AsientoHaberDetalle
from apps.compra.models import OrdenCompraRetencion


class Daily():
    def procesar(self):
        if self.referencia == "Compra":
            # JSON to Dict
            json_data = json.loads(self.tabla)

            # buscar Retención
            total_valor_retenido = 0
            for key in json_data:
                if key["ptype"] == "RT":
                    total_valor_retenido = total_valor_retenido + Decimal(key["valor_retenido"])
                    break

            if total_valor_retenido > 0:
                # asiento con retención
                asiento_auto_set = AsientoAutomatico.objects.filter(
                    codigo_asiento='purchase_iva_rf').order_by('debito')

                if asiento_auto_set:
                    glosa = '{0} Nro. {1}'.format(
                        asiento_auto_set[0].glosa, self.orden.numero_comprobante)
                    current_company_id = self.request.session['company_id']
                    # fecha = self.object.created_at.strftime('%Y-%m-%d %H:%M:%S')
                    fecha = self.orden.created_at.strftime('%Y-%m-%d')
                    comprobante = self.orden.numero_comprobante

                    tabla_json = []
                    for asiento in asiento_auto_set:
                        if asiento.debito:
                            valor_debito = 0
                            if asiento.descripcion == "Cuenta de ingreso (Ej. Inv. Mercadería)":
                                valor_debito = self.orden.valor_subtotal_12
                            else:
                                # Cuenta de ingreso (Ej. IVA Compras)
                                valor_debito = self.orden.valor_iva

                            tabla_json.append({
                                'cuenta_id': asiento.cuenta.pk,
                                'debito': str(valor_debito),
                                'credito': '',
                            })
                        else:
                            valor_credito = 0
                            total_retefuente = OrdenCompraRetencion.objects.filter(orden=self.orden).aggregate(
                                total_sum=Coalesce(Sum('valor_subtotal'), 0))['total_sum']

                            if asiento.descripcion == "Contrapartida cuenta de ingreso (Ej. Retención en la fuente)":
                                valor_credito = total_retefuente
                            else:
                                # Contrapartida cuenta de ingreso (Ej. Caja / Proveedores)
                                valor_credito = self.orden.valor_total

                            tabla_json.append({
                                'cuenta_id': asiento.cuenta.pk,
                                'debito': '',
                                'credito': str(valor_credito),
                            })
                    data = json.dumps(tabla_json)

                    self.crear_asiento_automatico(fecha, glosa, comprobante,
                                                  self.request.user, current_company_id, data)

            elif self.orden.valor_subtotal_12 > 0:
                # asiento con iva y sin retención
                asiento_auto_set = AsientoAutomatico.objects.filter(
                    codigo_asiento='purchase_iva').order_by('debito')
                if asiento_auto_set:
                    glosa = '{0} Nro. {1}'.format(
                        asiento_auto_set[0].glosa, self.orden.numero_comprobante)
                    current_company_id = self.request.session['company_id']
                    # fecha = self.object.created_at.strftime('%Y-%m-%d %H:%M:%S')
                    fecha = self.orden.created_at.strftime('%Y-%m-%d')
                    comprobante = self.orden.numero_comprobante

                    tabla_json = []
                    for asiento in asiento_auto_set:
                        if asiento.debito:
                            valor_debito = 0
                            if asiento.descripcion == "Cuenta de ingreso (Ej. Inv. Mercadería)":
                                valor_debito = self.orden.valor_subtotal_12
                            else:
                                # Cuenta de ingreso (Ej. IVA Compras)
                                valor_debito = self.orden.valor_iva

                            tabla_json.append({
                                'cuenta_id': asiento.cuenta.pk,
                                'debito': str(valor_debito),
                                'credito': '',
                            })
                        else:
                            # Contrapartida cuenta de ingreso (Ej. Caja / Proveedores)
                            tabla_json.append({
                                'cuenta_id': asiento.cuenta.pk,
                                'debito': '',
                                'credito': str(self.orden.valor_total),
                            })
                    data = json.dumps(tabla_json)

                    self.crear_asiento_automatico(fecha, glosa, comprobante,
                                                  self.request.user, current_company_id, data)

            else:
                # asiento sin iva y sin retención
                asiento_auto_set = AsientoAutomatico.objects.filter(
                    codigo_asiento='purchase_without_iva').order_by('debito')

                if asiento_auto_set:
                    glosa = '{0} Nro. {1}'.format(
                        asiento_auto_set[0].glosa, self.orden.numero_comprobante)
                    current_company_id = self.request.session['company_id']
                    # fecha = self.object.created_at.strftime('%Y-%m-%d %H:%M:%S')
                    fecha = self.orden.created_at.strftime('%Y-%m-%d')
                    comprobante = self.orden.numero_comprobante

                    tabla_json = []
                    for asiento in asiento_auto_set:
                        if asiento.debito:
                            tabla_json.append({
                                'cuenta_id': asiento.cuenta.pk,
                                'debito': str(self.orden.valor_total),
                                'credito': '',
                            })
                        else:
                            tabla_json.append({
                                'cuenta_id': asiento.cuenta.pk,
                                'debito': '',
                                'credito': str(self.orden.valor_total),
                            })
                    data = json.dumps(tabla_json)

                    self.crear_asiento_automatico(fecha, glosa, comprobante,
                                                  self.request.user, current_company_id, data)

        else:
            print("Venta")

        # asiento_auto_set = AsientoAutomatico.objects.filter(
        #    codigo_asiento='shift_start').order_by('debito')

        """if asiento_auto_set:
            glosa = '{0} Nro. {1}'.format(
                asiento_auto_set[0].glosa, self.orden.numero_comprobante)
            current_company_id = self.request.session['company_id']
            # fecha = self.object.created_at.strftime('%Y-%m-%d %H:%M:%S')
            fecha = self.orden.created_at.strftime('%Y-%m-%d')
            comprobante = self.orden.numero_comprobante

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

            crear_asiento_contable(fecha, glosa, comprobante,
                                   self.request.user, current_company_id, data)"""

        return True

    def crear_asiento_automatico(fecha, glosa, comprobante, current_user, current_company_id, tabla_json):
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

    def __init__(self, current_user, tipo_flujo, referencia, tabla, orden):
        self.usuario = current_user
        self.tipo_flujo = tipo_flujo
        self.referencia = referencia
        self.tabla = tabla
        self.orden = orden
