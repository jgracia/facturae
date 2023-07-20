# -*- coding: utf-8 -*-

# @mail infojavo@gmail.com
# @version 1.0
try:
    from lxml import etree
    from lxml.etree import fromstring
except ImportError:
    raise Exception('Instalar libreria lxml')
from os import path

import xmlsig
from .xades import XAdESContext, template, utils

BASE_DIR = path.dirname(__file__)


def parse_path(name):
    return path.join(BASE_DIR, name)


def parse_xml(name):
    name = name.encode('utf-8')
    parser = etree.XMLParser(ns_clean=True, recover=True, encoding='utf-8')
    xml_firma = fromstring(name, parser=parser)
    return xml_firma


class CheckDigit(object):

    # Definicion modulo 11
    _MODULO_11 = {
        'BASE': 11,
        'FACTOR': 2,
        'RETORNO11': 0,
        'RETORNO10': 1,
        'PESO': 2,
        'MAX_WEIGHT': 7
    }

    @classmethod
    def _eval_mod11(self, modulo):
        if modulo == self._MODULO_11['BASE']:
            return self._MODULO_11['RETORNO11']
        elif modulo == self._MODULO_11['BASE'] - 1:
            return self._MODULO_11['RETORNO10']
        else:
            return modulo

    @classmethod
    def compute_mod11(self, dato):
        """
        Calculo mod 11
        return int
        """
        total = 0
        weight = self._MODULO_11['PESO']

        for item in reversed(dato):
            total += int(item) * weight
            weight += 1
            if weight > self._MODULO_11['MAX_WEIGHT']:
                weight = self._MODULO_11['PESO']
        mod = 11 - total % self._MODULO_11['BASE']

        mod = self._eval_mod11(mod)
        return mod


class Xades(object):
    def sign_python(self, xml_document, file_pk12, password):
        try:
            root = parse_xml(xml_document)

            from .xades.template import create_signature
            signature = create_signature(
                xmlsig.constants.TransformInclC14N,
                xmlsig.constants.TransformRsaSha1,
                "Signature"
            )

            from .xades.constants import EtsiNS
            nsmap = signature.nsmap
            nsmap['etsi'] = EtsiNS
            #print(nsmap)

            #print signature
            #signature..set("xmlns:etsi", "http://uri.etsi.org/01903/v1.3.2#")
            signature_id = utils.get_unique_id()
            refEtsi = xmlsig.template.add_reference(
                signature, xmlsig.constants.TransformSha1, uri="#" + signature_id, name="SignedPropertiesID"
            )
            refEtsi.set("Type", "http://uri.etsi.org/01903#SignedProperties")
            xmlsig.template.add_reference(
                signature, xmlsig.constants.TransformSha1, uri="#KI"
            )
            ref = xmlsig.template.add_reference(
                signature, xmlsig.constants.TransformSha1, uri="#comprobante", name="REF"
            )
            xmlsig.template.add_transform(ref, xmlsig.constants.TransformEnveloped)

            ki = xmlsig.template.ensure_key_info(signature, name='KI')
            data = xmlsig.template.add_x509_data(ki)
            xmlsig.template.x509_data_add_certificate(data)
            serial = xmlsig.template.x509_data_add_issuer_serial(data)
            xmlsig.template.x509_issuer_serial_add_issuer_name(serial)
            xmlsig.template.x509_issuer_serial_add_serial_number(serial)
            xmlsig.template.add_key_value(ki)
            qualifying = template.create_qualifying_properties(
                signature, name=utils.get_unique_id()
            )
            props = template.create_signed_properties(
                qualifying, name=signature_id
            )
            signed_do = template.ensure_signed_data_object_properties(props)
            template.add_data_object_format(
                signed_do,
                "#RKI",
                description="Documento Electronico",
                mime_type="text/xml",
                encoding='UTF-8'
            )
            root.append(signature)
            ctx = XAdESContext()
            #with open(path.join(BASE_DIR, file_pk12), "rb") as key_file:
            #    ctx.load_p12(key_file.read(),password)
            #with open(path.join(BASE_DIR, file_pk12), "rb") as key_file:
            ctx.load_pem(file_pk12, password)
            ctx.sign(signature)
            extra = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
            return (extra.encode('utf-8')+etree.tostring(root))
        except:
            return -1
