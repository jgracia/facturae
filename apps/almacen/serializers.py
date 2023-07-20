from rest_framework.serializers import ModelSerializer
from .models import Kardex

"""
class KardexSerializer(ModelSerializer):

    class Meta:
        model = Kardex
        fields = ('created_at', 'numero_comprobante', 'almacen', 'producto', 'referencia', 'unidad')
    """


class KardexSerializer(ModelSerializer):
    #tipo = serializers.StringRelatedField(many=True)

    class Meta:
        model = Kardex
        fields = ('created_at', 'numero_comprobante', 'almacen',
                  'producto', 'referencia', 'unidad', 'tipo')
