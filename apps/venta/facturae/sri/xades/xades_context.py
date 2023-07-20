# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# @mail ep_niebla@hotmail.com, ep.niebla@gmail.com
# @version 1.0
from datetime import datetime
from os import path

import pytz
from lxml import etree

from base64 import b64encode, b64decode
from xmlsig.utils import long_to_bytes
from xmlsig import SignatureContext, constants
from .constants import NS_MAP
from .policy import ImpliedPolicy
from OpenSSL import crypto
import re

class XAdESContext(SignatureContext):
    def __init__(self, policy=None):
        """
        Declaration
        :param policy: Policy class
        :type policy: xades.Policy
        """
        self.policy = policy
        self.policies = {None: ImpliedPolicy()}
        if policy is None:
            self.policy = ImpliedPolicy()
        else:
            self.policies[policy.identifier] = policy
        super(XAdESContext, self).__init__()

    def sign(self, node):
        """
        Signs a node
        :param node: Signature node
        :type node: lxml.etree.Element
        :return: None
        """
        signed_properties = node.find(
            "ds:Object/etsi:QualifyingProperties["
            "@Target='#{}']/etsi:SignedProperties".format(
                node.get('Id')),
            namespaces=NS_MAP)
        assert signed_properties is not None
        self.calculate_signed_properties(signed_properties, node, True)
        unsigned_properties = node.find(
            "ds:Object/etsi:QualifyingProperties["
            "@Target='#{}']/etsi:UnsignedProperties".format(
                node.get('Id')),
            namespaces=NS_MAP)
        if unsigned_properties is not None:
            self.calculate_unsigned_properties(unsigned_properties, node, True)
        self.policy.sign(node)
        res = super(XAdESContext, self).sign(node)
        return res

    def verify(self, node):
        """
        verifies a signature
        :param node: Signature node
        :type node: lxml.etree.Element
        :return:
        """
        schema = etree.XMLSchema(etree.parse(path.join(
            path.dirname(__file__), "data/XAdES.xsd"
        )))
        schema.assertValid(node)
        signed_properties = node.find(
            "ds:Object/etsi:QualifyingProperties["
            "@Target='#{}']/etsi:SignedProperties".format(
                node.get('Id')),
            namespaces=NS_MAP)
        assert signed_properties is not None
        self.calculate_signed_properties(signed_properties, node, False)
        unsigned_properties = node.find(
            "ds:Object/etsi:QualifyingProperties["
            "@Target='#{}']/etsi:UnSignedProperties".format(
                node.get('Id')),
            namespaces=NS_MAP)
        if unsigned_properties is not None:
            self.calculate_unsigned_properties(signed_properties, node, False)
        policy_id = signed_properties.find(
            'etsi:SignedSignatureProperties/etsi:SignaturePolicyIdentifier/'
            'etsi:SignaturePolicyId/etsi:SigPolicyId/etsi:Identifier',
            namespaces=NS_MAP
        )
        policy = self.policies[None]
        if policy_id is not None:
            if policy_id.text in self.policies:
                policy = self.policies[policy_id.text]
        policy.validate(node)
        res = super(XAdESContext, self).verify(node)
        return res

    def calculate_signed_properties(self, signed_properties, node, sign=False):
        signature_properties = signed_properties.find(
            'etsi:SignedSignatureProperties', namespaces=NS_MAP
        )
        assert signature_properties is not None
        self.calculate_signature_properties(signature_properties, node, sign)
        data_object_properties = signed_properties.find(
            'etsi:SignedDataObjectProperties', namespaces=NS_MAP
        )
        if data_object_properties is not None:
            self.calculate_data_object_properties(
                data_object_properties, node, sign
            )
        return

    def calculate_signature_properties(
            self, signature_properties, node, sign=False):
        signing_time = signature_properties.find(
            'etsi:SigningTime', namespaces=NS_MAP
        )
        assert signing_time is not None
        if sign and signing_time.text is None:
            now = datetime.now().replace(
                microsecond=0, tzinfo=pytz.utc
            )
            signing_time.text = now.isoformat()
        certificate_list = signature_properties.find(
            'etsi:SigningCertificate', namespaces=NS_MAP
        )
        assert certificate_list is not None
        if sign:
            self.policy.calculate_certificates(certificate_list, self.x509)
        else:
            self.policy.validate_certificate(certificate_list, node)
        policy = signature_properties.find(
            'etsi:SignaturePolicyIdentifier', namespaces=NS_MAP
        )
        if sign:
            assert policy is not None
        self.policy.calculate_policy_node(policy, sign)

    def calculate_data_object_properties(
            self, data_object_properties, node, sign=False):
        """
        To be improved with EPES, T...
        :param data_object_properties: DataObjectProperties node
        :param node: Signature node
        :param sign:
        :return:
        """
        return

    def calculate_unsigned_properties(
            self, unsigned_properties, node, sign=False):
        """
                To be improved with EPES, T...
                :param unsigned_properties: UnsignedProperties node
                :param node: Signature node
                :param sign:
                :return:
                """
        return

    def load_p12(self, key_file, password):
        """
        This function fills the context public_key, private_key and x509 from
        PKCS12 Object
        :param key: the PKCS12 Object
        :type key: OpenSSL.crypto.PKCS12
        :return: None
        """
        key = crypto.load_pkcs12(key_file, password)
        self.x509 = key.get_certificate().to_cryptography()
        self.public_key = key.get_certificate().to_cryptography().public_key()
        self.private_key = key.get_privatekey().to_cryptography_key()

    def load_pem(self, key_file, password):
        """
        This function fills the context public_key, private_key and x509 from
        PKCS12 Object
        :param key: the PKCS12 Object
        :type key: OpenSSL.crypto.PKCS12
        :return: None
        """
        #print key

        certs = key_file.decode().split("Bag Attributes")
        modulus = None

        for c in certs:
            if c.strip()!="":
                regex = r"(-----BEGIN CERTIFICATE-----.*-----END CERTIFICATE-----)"
                m = re.search(regex, c, re.MULTILINE | re.DOTALL)
                if m != None:
                    cAux=crypto.load_certificate(crypto.FILETYPE_PEM, m.group(0))

                    if not cAux.has_expired():
                        pub = cAux.get_pubkey()
                        self.x509=cAux.to_cryptography()
                        self.public_key=cAux.to_cryptography().public_key()
                        #print(cAux.to_cryptography().extensions)
                        b=False
                        for ext in cAux.to_cryptography().extensions:

                            if ext.oid.dotted_string.endswith(".11"):
                                b=True
                                #print(ext.oid.dotted_string.endswith(".11"))
                                break


                        if b:
                            print(self.public_key)
                            modulus = b64encode(long_to_bytes( self.public_key.public_numbers().n ))
                            #print cAux.to_cryptography().public_key()
                            break

        for c in certs:
            if c.strip()!="":
                regex = r"(-----BEGIN ENCRYPTED PRIVATE KEY-----.*-----END ENCRYPTED PRIVATE KEY-----)"
                m = re.search(regex, c, re.MULTILINE | re.DOTALL)

                if m!=None:

                    cAux=crypto.load_privatekey(crypto.FILETYPE_PEM, m.group(0),password.encode('ascii'))

                    pub = cAux.to_cryptography_key()
                    modulusPKEY = b64encode(long_to_bytes( pub.public_key().public_numbers().n ))

                    if  modulus==modulusPKEY:
                        self.private_key = pub

                        #print cAux.to_cryptography()
                        break

                #print cAux.get_notAfter()
        #print self.x509
        #print self.public_key
        #print self.private_key
        #self.x509 = key.get_certificate().to_cryptography()
        #self.public_key = key.get_certificate().to_cryptography().public_key()
        #self.private_key = key.get_privatekey().to_cryptography_key()
