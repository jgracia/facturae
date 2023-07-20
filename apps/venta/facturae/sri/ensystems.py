# -*- coding: utf-8 -*-

import os
import base64

try:
    from suds.xsd.doctor import Import
    from suds.xsd.doctor import ImportDoctor
    from suds.client import Client
except ImportError:
    raise Exception('Instalar libreria suds-jurko')

#import utils
#import logging


class EnSystems(object):
    
    @classmethod
    def __init__(self):
        """
        Clase para creacion de RIDEs y muchas otras cosas
        """

    def get_ride(self, document, path_logo='', logo=''):
        """
        Metodo que envia el XML al WS
        """
        try:
            urlRides="https://ensystems-sri-xades.herokuapp.com/WS/rideSri.wsdl"
            #buf = StringIO()
            #buf.write(document)
            buffer_xml = base64.encodestring(document.encode('utf-8'))
            buffer_logo=''
            logExt=''
            if logo!='' and path_logo!='':    
                #bufLog = StringIO()        
                #bufLog.write(logo)
                buffer_logo = base64.encodestring(logo)
                fileName, logExt = os.path.splitext(path_logo)
                logExt=logExt.replace('.','')
            #if not utils.check_web_service(urlRides):
            #    # TODO: implementar modo offline
            #    raise Exception('Error SRI', 'Servicio RIDEs no disponible.')

            client = Client(urlRides)
            result = client.service.getRide(buffer_xml.decode('utf-8'),buffer_logo.decode('utf-8'),logExt) 
            
            return result.success, result.message, base64.decodestring(result.pdf.encode('utf-8'))
        except Exception as e:     
            return False, "Error al Tratar de Comvertir el Archivo XML a PDF", ""
        
    def validate_signature(self, document):
        """
        Metodo que envia el XML al WS a validar
        """
        try:
            urlRides="https://ensystems-sri-xades.herokuapp.com/WS/validaXadesBes.wsdl?x=2"
            #buf = StringIO()
            #buf.write(document)
            buffer_xml = base64.encodestring(document.encode('utf-8'))

            #if not utils.check_web_service(urlRides):
            #    # TODO: implementar modo offline
            #    raise Exception('Error SRI', 'Servicio RIDEs no disponible.')

            client = Client(urlRides)
            result = client.service.validateSignature(buffer_xml.decode('utf-8')) 

            return result.success, result.message
        except Exception as e:     
            return False, "Error al Tratar de Validar el XML"
            
    def sign_xml(self, document, key, password=''):

            urlRides="https://ensystems-sri-xades.herokuapp.com/WS/firmaXadesBes.wsdl?x=2"
            #buf = StringIO()
            #buf.write(document)
            buffer_xml = base64.encodestring(document.encode('utf-8'))
            
            #buf2 = StringIO()
            #buf2.write(key)
            buffer_key = base64.encodestring(key)
            #if not utils.check_web_service(urlRides):
            #    # TODO: implementar modo offline
            #    raise Exception('Error SRI', 'Servicio RIDEs no disponible.')

            client = Client(urlRides)
            result = client.service.getFileSigned(buffer_xml.decode('utf-8'), buffer_key.decode('utf-8'), base64.encodestring(password.encode('utf-8')).decode('utf-8')) 

            return result.success, result.message, result.xml

            
    def p12_to_pem(self, key, password=''):
        """
        Metodo que envia el XML al WS a validar
        """
        try:

            urlRides="https://ensystems-sri-xades.herokuapp.com/WS/P12toPEM.wsdl"
            #buf = StringIO()
            #buf.write(key.decode())
            buffer_key = base64.encodestring(key)
            #if not utils.check_web_service(urlRides):
            #    # TODO: implementar modo offline
            #    raise Exception('Error SRI', 'Servicio RIDEs no disponible.')

            client = Client(urlRides)
            result = client.service.getFilePEM(buffer_key.decode('utf-8'), base64.encodestring(password.encode('utf-8')).decode('utf-8')) 
            
            return result.success, result.message, base64.decodestring(result.pem.encode('utf-8'))    
        except Exception as e:     
            return False, "Error al Tratar de Convertir P12 a PEM", ""