from simple_history.models import HistoricalRecords


# define su manejador de señal / devolución de llamada en cualquier lugar fuera de models.py


def add_history_kardex(sender, **kwargs):
    history_instance = kwargs['history_instance']
    # thread.request para usar solo cuando el middleware simple_history está activado y habilitado
    history_instance.kardex = HistoricalRecords.thread.request.META['REMOTE_ADDR']
