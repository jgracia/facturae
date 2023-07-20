"""factel URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

from django.contrib.auth.views import LoginView, LogoutView, \
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, \
    PasswordResetCompleteView, PasswordChangeView, PasswordChangeDoneView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('apps.dashboard.urls')),
    path('iniciar-sesion/', LoginView.as_view(template_name='registration/login-register.html'), name='login'),
    path('cerrar-sesion/', LogoutView.as_view(template_name='registration/login-register.html'), name='logout'),
    #path('registrarse/', signup, name='signup'),

    path('password_reset/', PasswordResetView.as_view(template_name='registration/password_reset_form.html'),
         name='password_reset'),
    path('password_reset/done/', PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'), name='password_reset_complete'),

    path('password_change/', PasswordChangeView.as_view(
        template_name='registration/password_change_form.html'), name='password_change'),
    path('password_change/done/', PasswordChangeDoneView.as_view(
        template_name='registration/password_change_done.html'), name='password_change_done'),


    path('sri/', include('apps.sri.urls', namespace='sri')),
    path('administracion/', include('apps.administracion.urls', namespace='administracion')),
    path('usuario/', include('apps.usuario.urls', namespace='usuario')),
    path('unidadmedida/', include('apps.unidadmedida.urls', namespace='unidadmedida')),
    path('proveedor/', include('apps.proveedor.urls', namespace='proveedor')),
    path('cliente/', include('apps.cliente.urls', namespace='cliente')),
    path('almacen/', include('apps.almacen.urls', namespace='almacen')),
    path('producto/', include('apps.producto.urls', namespace='producto')),
    path('servicio/', include('apps.servicio.urls', namespace='servicio')),
    path('cesta/', include('apps.cesta.urls', namespace='cesta')),
    path('contabilidad/', include('apps.contabilidad.urls', namespace='contabilidad')),
    path('retencion/', include('apps.retencion.urls', namespace='retencion')),
    path('compra/', include('apps.compra.urls', namespace='compra')),
    path('venta/', include('apps.venta.urls', namespace='venta')),
    path('notaentrega/', include('apps.notaentrega.urls', namespace='notaentrega')),
    path('proforma/', include('apps.proforma.urls', namespace='proforma')),
    path('notadebito/', include('apps.notadebito.urls', namespace='notadebito')),
    path('notacredito/', include('apps.notacredito.urls', namespace='notacredito')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
