from django.conf import settings

CESTA_TEMPLATE_TAG_NAME = getattr(settings, 'CESTA_TEMPLATE_TAG_NAME', 'get_cesta')
