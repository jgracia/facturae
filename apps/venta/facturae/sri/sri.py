# -*- coding: utf-8 -*-

# @mail ep_niebla@hotmail.com, ep.niebla@gmail.com
# @version 1.0
import os
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import base64
import logging

try:
    from lxml import etree
    from lxml.etree import fromstring, DocumentInvalid
except ImportError:
    raise Exception('Instalar libreria lxml')

try:
    from suds.client import Client
except ImportError:
    raise Exception('Instalar libreria suds-jurko')

from . import utils

from .firmado import CheckDigit
SCHEMAS_PATH = 'schemas'

SCHEMAS = {
    'factura': 'schemas/factura.xsd',
    'notaCredito': 'schemas/nota_credito.xsd',
    'comprobanteRetencion': 'schemas/retencion.xsd',
    'guiaRemision': 'schemas/guia_remision.xsd',
    'notaDebito': 'schemas/nota_debito.xsd'
}


class DocumentXML(object):
    _schema = False
    _version_doc = False
    document = False
    SriServiceObj = False

    @classmethod
    def __init__(self, document):
        """
        document: XML representation
        type: determinate schema
        """
        #document=document.encode('utf-8')
        parser = etree.XMLParser(ns_clean=True, recover=True, encoding='utf-8')
        self.document = fromstring(document, parser=parser)
        self.type_document = self.document.tag
        self._schema = self.type_document.upper()
        self._version_doc = (self.document.attrib['version']).replace(".", "_")
        self.signed_document = False
        self.SriServiceObj = SriService()
        children = self.document.getchildren()
        children = children[0].getchildren()
        self.set_active_env(children[0].text)

    @classmethod
    def save(self, access_key):
        OPT_PATH = 'opt/facturas/'
        name = '%s%s_G.xml' % (OPT_PATH, access_key)
        tree = etree.ElementTree(self.document)
        #tree.write(name, pretty_print=True, xml_declaration=True, encoding='utf-8', method="xml")
        #xml = etree.tostring(self.invoice_element, pretty_print = True, encoding='UTF-8')
        #xml = '<?xml version=\"1.0\" encoding=\"utf-8\"?>\n' + xml
        tree.write(name, pretty_print=True, xml_declaration=False, encoding='utf-8', method="xml", standalone=False)

    @classmethod
    def validate_xml(self):
        """
        Validar esquema XML
        """
        file_path = os.path.join(os.path.dirname(__file__), SCHEMAS_PATH,self._version_doc,self._schema+"_V_"+self._version_doc+".xsd")
        schema_file = open(file_path)
        xmlschema_doc = etree.parse(schema_file)
        xmlschema = etree.XMLSchema(xmlschema_doc)
        try:
            xmlschema.assertValid(self.document)
            return True
        except DocumentInvalid:
            return False

    @classmethod
    def send_receipt(self, document):
        """
        Metodo que envia el XML al WS
        """
        """buf = StringIO()
        buf.write(document)"""
        buf = StringIO()
        buf.write(document)
        #print("veras")
        buffer_xml = base64.b64encode(buf.getvalue().encode('utf-8'))
        #print(buffer_xml.decode('utf-8'))

        #parser = etree.XMLParser(ns_clean=True, recover=True, encoding='utf-8')
        #documento = fromstring(base64.b64decode(buffer_xml), parser=parser)

        if not utils.check_service('prueba'):
            # TODO: implementar modo offline
            raise Exception('Error SRI', 'Servicio SRI no disponible.')

        client = Client(self.SriServiceObj.get_active_ws()[0])
        result = client.service.validarComprobante(buffer_xml.decode('utf-8'))
        #print(result)
        errores = []
        error_code=0
        if result.estado == 'RECIBIDA':
            return True, errores, 0
        else:
            for comp in result.comprobantes:
                for m in comp[1][0].mensajes:
                    rs = [m[1][0].tipo, m[1][0].mensaje]
                    rs.append(getattr(m[1][0], 'informacionAdicional', ''))
                    errores.append(' '.join(rs))
                    error_code+=int(m[1][0].identificador)
            #if error_code!=43:
            #    self.logger.error(errores)
            return False, ', '.join(errores), error_code

    def request_authorization(self, access_key):
        messages = []
        client = Client(self.SriServiceObj.get_active_ws()[1])
        result = client.service.autorizacionComprobante(access_key)
        #print(result)
        autorizacion = result.autorizaciones[0][0]
        mensajes = autorizacion.mensajes and autorizacion.mensajes[0] or []
        for m in mensajes:

            messages.append([m.identificador, m.mensaje,
                             m.tipo, m.informacionAdicional])
        if not autorizacion.estado == 'AUTORIZADO':
            return False, messages
        if 	messages==[]:
            messages.append(["",autorizacion.estado,""])
        return autorizacion, messages

    def render_authorized_einvoice(self, autorizacion):
        xml='<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        xml+='<autorizacion>'
        xml+='<estado>'+autorizacion.estado+'</estado>'
        xml+='<numeroAutorizacion>'+autorizacion.numeroAutorizacion+'</numeroAutorizacion>'
        xml+='<fechaAutorizacion>'+(str(autorizacion.fechaAutorizacion.strftime("%d/%m/%Y %H:%M:%S")))+'</fechaAutorizacion>'
        xml+='<comprobante><![CDATA['+autorizacion.comprobante+']]></comprobante>'
        xml+='</autorizacion>'
        parser = etree.XMLParser(ns_clean=True, recover=True, encoding='utf-8', strip_cdata=False)
        xml_auth = fromstring(xml.encode('utf-8'), parser=parser)
        return etree.tostring(xml_auth, pretty_print=True, xml_declaration=True, encoding="utf-8")

    def make_unicode(self, input):
        if type(input) != unicode:
            input =  input.decode('utf-8')
            return input
        else:
            return input

    @classmethod
    def set_active_env(self, env_service):
        self.SriServiceObj.set_active_env(env_service)
    @classmethod
    def create_access_key(self, values):
        self.SriServiceObj.create_access_key(values)
    """
    def get_access_key(self, name):
        if name == 'account.invoice':
            auth = self.company_id.partner_id.get_authorisation('out_invoice')
            ld = self.date_invoice.split('-')
            numero = getattr(self, 'invoice_number')
        elif name == 'account.retention':
            auth = self.company_id.partner_id.get_authorisation('ret_in_invoice')  # noqa
            ld = self.date.split('-')
            numero = getattr(self, 'name')
            numero = numero[6:15]
        ld.reverse()
        fecha = ''.join(ld)
        tcomp = utils.tipoDocumento[auth.type_id.code]
        ruc = self.company_id.partner_id.identifier
        codigo_numero = self.get_code()
        tipo_emision = self.company_id.emission_code
        access_key = (
            [fecha, tcomp, ruc],
            [numero, codigo_numero, tipo_emision]
            )
        return access_key

    @api.multi
    def _get_codes(self, name='account.invoice'):
        ak_temp = self.get_access_key(name)
        self.SriServiceObj.set_active_env(self.env.user.company_id.env_service)
        access_key = self.SriServiceObj.create_access_key(ak_temp)
        emission_code = self.company_id.emission_code
        return access_key, emission_code
	"""
class SriService(object):

    __AMBIENTE_PRUEBA = '1'
    __AMBIENTE_PROD = '2'
    __ACTIVE_ENV = '1'
    # revisar el utils
    __WS_TEST_RECEIV = 'https://celcer.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl'  # noqa
    __WS_TEST_AUTH = 'https://celcer.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl'  # noqa
    __WS_RECEIV = 'https://cel.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl'  # noqa
    __WS_AUTH = 'https://cel.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl'  # noqa

    __WS_TESTING = (__WS_TEST_RECEIV, __WS_TEST_AUTH)
    __WS_PROD = (__WS_RECEIV, __WS_AUTH)

    _WSDL = {
        __AMBIENTE_PRUEBA: __WS_TESTING,
        __AMBIENTE_PROD: __WS_PROD
    }
    __WS_ACTIVE = __WS_TESTING

    @classmethod
    def set_active_env(self, env_service):
        if env_service == self.__AMBIENTE_PRUEBA:
            self.__ACTIVE_ENV = self.__AMBIENTE_PRUEBA
        else:
            self.__ACTIVE_ENV = self.__AMBIENTE_PROD
        self.__WS_ACTIVE = self._WSDL[self.__ACTIVE_ENV]

    @classmethod
    def get_active_env(self):
        return self.__ACTIVE_ENV

    @classmethod
    def get_env_test(self):
        return self.__AMBIENTE_PRUEBA

    @classmethod
    def get_env_prod(self):
        return self.__AMBIENTE_PROD

    @classmethod
    def get_ws_test(self):
        return self.__WS_TEST_RECEIV, self.__WS_TEST_AUTH

    @classmethod
    def get_ws_prod(self):
        return self.__WS_RECEIV, self.__WS_AUTH

    @classmethod
    def get_active_ws(self):
        return self.__WS_ACTIVE

    @classmethod
    def create_access_key(self, values):
        """
        values: tuple ([], [])
        """
        env = self.get_active_env()
        dato = ''.join(values[0] + [env] + values[1])
        modulo = CheckDigit.compute_mod11(dato)
        access_key = ''.join([dato, str(modulo)])
        return access_key
