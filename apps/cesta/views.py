from django.http import JsonResponse

from .models import Cesta

# Create your views here.


def vaciar_cesta_ajax(request):
    if request.method == "GET":

        clave_apli = request.GET.get('key', None)
        user_basket = Cesta.objects.filter(usuario=request.user,
                                           clave_apli=clave_apli)[0]

        # user_basket.items.clear()  # Disassociates Item from Cesta.

        # METODO 1
        #items = user_basket.items.all()
        #pks_list = items.values('id')
        # CestaItem.objects.filter(pk__in=pks_list).delete()

        # METODO 2
        # for item in items:
        #    CestaItem.objects.filter(pk=item.id).delete()

        user_basket.vaciar_cesta()

        return JsonResponse({'success': True})


def total_filas_cesta(request):

    if request.method == "GET":
        clave_apli = request.GET.get('key', None)
        user_basket = Cesta.objects.filter(usuario=request.user,
                                           clave_apli=clave_apli)[0]

        return JsonResponse({
            'success': True,
            'total_filas': user_basket.obtener_total_filas()
        })
