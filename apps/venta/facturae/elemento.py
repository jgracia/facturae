import time
from datetime import datetime
from lxml import etree

from apps.venta.models import FacturaDetalle

codigoImpuesto = {
    'iva': '2',
    'ice': '3',
    'irbpnr': '5'
}

tarifaImpuesto = {
    'iva0': '0',
    'iva12': '2',
    'iva14': '3',
    'noiva': '6',
    'exento': '7',
}

tarifaPorcenaje = {
    'iva': '12',
}

class ElementoXML:

    def _obtener_infoTributaria(self, factura_obj, access_key, emission_code):
        """
        """
        infoTributaria = etree.Element('infoTributaria')
        etree.SubElement(infoTributaria, 'ambiente').text = str(factura_obj.empresa.tipo_ambiente)
        etree.SubElement(infoTributaria, 'tipoEmision').text = emission_code
        etree.SubElement(infoTributaria, 'razonSocial').text = factura_obj.empresa.razon_social
        etree.SubElement(infoTributaria, 'nombreComercial').text = factura_obj.empresa.nombre_comercial
        etree.SubElement(infoTributaria, 'ruc').text = factura_obj.empresa.ruc  # número de ruc del contribuyente [13] digitos
        etree.SubElement(infoTributaria, 'claveAcceso').text = access_key
        etree.SubElement(infoTributaria, 'codDoc').text = factura_obj.sri_tipo_comprobante.codigo = '01' # conforme manual tabla 3
        etree.SubElement(infoTributaria, 'estab').text = factura_obj.secuencia.punto_establecimiento
        etree.SubElement(infoTributaria, 'ptoEmi').text = factura_obj.secuencia.punto_emision
        etree.SubElement(infoTributaria, 'secuencial').text = str(factura_obj.numero_secuencia).zfill(9) # número del comprabante (secuencial) [9] digitos
        etree.SubElement(infoTributaria, 'dirMatriz').text = factura_obj.empresa.direccion_matriz
        return infoTributaria

    def _obtener_infoFactura(self, factura_obj):
        """
        """
        infoFactura = etree.Element('infoFactura')
        #etree.SubElement(infoFactura, 'fechaEmision').text = time.strftime('%d/%m/%Y',time.strptime(factura_obj.fecha_emision, '%Y-%m-%d %H:%M:%S'))
        etree.SubElement(infoFactura, 'fechaEmision').text = datetime.strftime(factura_obj.fecha_emision, "%d/%m/%Y")
        etree.SubElement(infoFactura, 'dirEstablecimiento').text = factura_obj.secuencia.direccion_establecimiento
        if (factura_obj.empresa.codigo_contribuyente_especial):
            etree.SubElement(infoFactura, 'contribuyenteEspecial').text = factura_obj.empresa.codigo_contribuyente_especial
        if (factura_obj.empresa.obligado_llevar_contabilidad):
            etree.SubElement(infoFactura, 'obligadoContabilidad').text = 'SI'
        else:
            etree.SubElement(infoFactura, 'obligadoContabilidad').text = 'NO'
        etree.SubElement(infoFactura, 'tipoIdentificacionComprador').text = factura_obj.cliente.identificacion_tipo.codigo
        etree.SubElement(infoFactura, 'razonSocialComprador').text = factura_obj.cliente.nombre
        etree.SubElement(infoFactura, 'identificacionComprador').text = factura_obj.cliente.identificacion
        if (factura_obj.cliente.direccion):
            etree.SubElement(infoFactura, 'direccionComprador').text = factura_obj.cliente.direccion
        etree.SubElement(infoFactura, 'totalSinImpuestos').text = str(round(factura_obj.valor_subtotal_sin_impuesto, 2))
        etree.SubElement(infoFactura, 'totalDescuento').text = str(round(factura_obj.valor_descuento, 2))

        #totalConImpuestos
        #totalConImpuestos = etree.Element('totalConImpuestos')
        #for tax in factura_obj.tax_line:

        #    if tax.tax_group in ['iva', 'ice', 'irbpnr']:
        #        totalImpuesto = etree.Element('totalImpuesto')
        #        etree.SubElement(totalImpuesto, 'codigo').text = codigoImpuesto[tax.tax_group] # conforme manual tabla 16
        #        etree.SubElement(totalImpuesto, 'codigoPorcentaje').text = tarifaImpuesto[tax.tax_group] # conforme manual tabla 17
        #        etree.SubElement(totalImpuesto, 'baseImponible').text = str(round(factura.valor_subtotal_12, 2))
        #        etree.SubElement(totalImpuesto, 'valor').text = '{:.2f}'.format(factura.valor_iva)
        #        totalConImpuestos.append(totalImpuesto)

        #infoFactura.append(totalConImpuestos)

        totalConImpuestos = etree.Element('totalConImpuestos')
        totalImpuesto = etree.Element('totalImpuesto')
        etree.SubElement(totalImpuesto, 'codigo').text = codigoImpuesto['iva'] # conforme manual tabla 16
        etree.SubElement(totalImpuesto, 'codigoPorcentaje').text = tarifaImpuesto['iva12'] # conforme manual tabla 17
        etree.SubElement(totalImpuesto, 'baseImponible').text = str(round(factura_obj.valor_subtotal_12, 2))
        etree.SubElement(totalImpuesto, 'tarifa').text = tarifaPorcenaje['iva']
        etree.SubElement(totalImpuesto, 'valor').text = '{:.2f}'.format(factura_obj.valor_iva)

        totalConImpuestos.append(totalImpuesto)
        infoFactura.append(totalConImpuestos)

        etree.SubElement(infoFactura, 'propina').text = '0.00'
        etree.SubElement(infoFactura, 'importeTotal').text = str(round(factura_obj.valor_total, 2))
        print("==> FASE 2.2")
        etree.SubElement(infoFactura, 'moneda').text = factura_obj.sri_tipo_moneda.codigo

        pagos = etree.Element('pagos')
        pago = etree.Element('pago')
        etree.SubElement(pago, 'formaPago').text = factura_obj.sri_forma_pago.codigo
        etree.SubElement(pago, 'total').text = str(round(factura_obj.valor_total, 2))

        pagos.append(pago)
        infoFactura.append(pagos)

        return infoFactura

    def _obtener_detalles(self, factura_obj):
        """
        """
        detalles = etree.Element('detalles')
        producto_set = FacturaDetalle.objects.filter(factura=factura_obj)
        for item in producto_set:
            detalle = etree.Element('detalle')
            etree.SubElement(detalle, 'codigoPrincipal').text = item.producto.codigo_principal
            if item.producto.codigo_auxiliar:
                etree.SubElement(detalle, 'codigoAuxiliar').text = item.producto.codigo_auxiliar
            etree.SubElement(detalle, 'descripcion').text = item.producto.descripcion
            etree.SubElement(detalle, 'cantidad').text = str(round(item.cantidad, 2))
            etree.SubElement(detalle, 'precioUnitario').text = str(round(item.precio_venta, 2))
            etree.SubElement(detalle, 'descuento').text = str(round(item.valor_descuento, 2))
            etree.SubElement(detalle, 'precioTotalSinImpuesto').text = str(round(item.valor_subtotal_sin_impuesto, 2))
            impuestos = etree.Element('impuestos')
            #for tax_line in line.invoice_line_tax_id:
            #    if tax_line.tax_group in ['valor_subtotal_12', 'valor_iva']:
            #        impuesto = etree.Element('impuesto')
            #        etree.SubElement(impuesto, 'codigo').text = codigoImpuesto[tax_line.tax_group]
            #        etree.SubElement(impuesto, 'codigoPorcentaje').text = tarifaImpuesto[tax_line.tax_group]
            #        etree.SubElement(impuesto, 'tarifa').text = '%.2f' % (tax_line.amount * 100)
            #        etree.SubElement(impuesto, 'baseImponible').text = '%.2f' % (line.price_subtotal)
            #        etree.SubElement(impuesto, 'valor').text = '%.2f' % (line.amount_tax)
            #        impuestos.append(impuesto)
            impuesto = etree.Element('impuesto')
            etree.SubElement(impuesto, 'codigo').text = codigoImpuesto['iva']
            etree.SubElement(impuesto, 'codigoPorcentaje').text = tarifaImpuesto['iva12']
            etree.SubElement(impuesto, 'tarifa').text = tarifaPorcenaje['iva']
            etree.SubElement(impuesto, 'baseImponible').text = str(round(item.valor_subtotal_12, 2))
            etree.SubElement(impuesto, 'valor').text = str(round(item.valor_iva, 2))
            impuestos.append(impuesto)

            detalle.append(impuestos)
            detalles.append(detalle)
        return detalles

    def _obtener_infoAdicional(self, factura_obj):
        """
        """
        infoAdicional = etree.Element('infoAdicional')
        attrib = {'nombre': 'Dirección'}
        etree.SubElement(infoAdicional, 'campoAdicional', attrib).text = factura_obj.cliente.direccion

        attrib = {'nombre': 'Teléfono'}
        if (factura_obj.cliente.telefono and factura_obj.cliente.celular):
            etree.SubElement(infoAdicional, 'campoAdicional', attrib).text = factura_obj.cliente.telefono + ' / ' + factura_obj.cliente.celular
        else:
            if (factura_obj.cliente.telefono):
                etree.SubElement(infoAdicional, 'campoAdicional', attrib).text=factura_obj.cliente.telefono
            else:
                etree.SubElement(infoAdicional, 'campoAdicional', attrib).text=factura_obj.cliente.celular

        if (factura_obj.cliente.email):
            attrib = {'nombre': 'Email'}
            etree.SubElement(infoAdicional, 'campoAdicional', attrib).text=factura_obj.cliente.email

        return infoAdicional

    def _generar_factura_xml(self, factura_obj, access_key):
        """
        """
        emission_code = '1' #Para el método de autorización offline, solo existe el tipo de emisión normal. Tabla 2
        factura = etree.Element('factura')
        factura.set("id", "comprobante")
        #factura.set("version", "1.1.0")
        factura.set("version", "1.0.0")

        # generar infoTributaria
        infoTributaria = self._obtener_infoTributaria(factura_obj, access_key, emission_code)
        factura.append(infoTributaria)

        # generar infoFactura
        infoFactura = self._obtener_infoFactura(factura_obj)
        factura.append(infoFactura)

        #generar detalles
        detalles = self._obtener_detalles(factura_obj)
        factura.append(detalles)

        #generar infoAdicional
        infoAdicional = self._obtener_infoAdicional(factura_obj)
        factura.append(infoAdicional)
        return factura

    def get_clave_acceso(self, fecha, factura_obj):
        tcomp = factura_obj.sri_tipo_comprobante.codigo
        ruc = factura_obj.empresa.ruc  # número de ruc del contribuyente [13] digitos
        serie = '{0}{1}'.format(factura_obj.secuencia.punto_establecimiento, factura_obj.secuencia.punto_emision)
        numero = str(factura_obj.numero_secuencia).zfill(9) # número del comprabante (secuencial) [9] digitos
        codigo_numero = '12345678' # codigo numerico [8] digitos
        tipo_emision = '1' #Para el método de autorización offline, solo existe el tipo de emisión normal
        access_key = (
            [fecha, tcomp, ruc],
            [serie, numero, codigo_numero, tipo_emision]
            )
        return access_key
