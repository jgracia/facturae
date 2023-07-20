from django.urls import path

from . import views

app_name = 'dashboard'
urlpatterns = [
    # The home page
    path('', views.index, name='home'),
    path('contacto/', views.contact_us, name='contact_us'),
    path('nosotros/', views.about_us, name='about_us'),
    path('portafolio/', views.portfolio, name='portfolio'),
    path('servicios/', views.services, name='services'),

    # Datos gráfico
    path('ajax/get_grafico_dashboard/',
         views.get_grafico_dashboard, name='get_grafico_dashboard'),
]
