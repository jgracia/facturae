from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'notadebito'
urlpatterns = [
    path('', login_required(views.IndexView.as_view()), name='listado_notasdebito'),
    path('ajax_listado_notasdebito/', login_required(views.ajax_listado_notasdebito),
         name='ajax_listado_notasdebito'),

]
