from django.apps import AppConfig

# from simple_history.signals import (
#    pre_create_historical_record,
# )
# from apps.almacen.history_signal import add_history_kardex


class AlmacenConfig(AppConfig):
    name = 'almacen'

    '''
    # agregar señal del campo extra al modelo
    def ready(self):
        from apps.almacen.models \
            import ControlProductoLote

        pre_create_historical_record.connect(
            add_history_kardex,
            sender=ControlProductoLote
        )
    '''
