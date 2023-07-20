from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'notacredito'
urlpatterns = [
    path('', login_required(views.IndexView.as_view()), name='listado_notascredito'),
    path('ajax_listado_notascredito/', login_required(views.ajax_listado_notascredito),
         name='ajax_listado_notascredito'),

]
