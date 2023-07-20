from django.contrib.auth.models import User

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView

from django.urls import reverse_lazy

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


from .models import Perfil
from .forms import SignUpForm, UserProfileForm

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.template import RequestContext
from django.shortcuts import redirect

# librerias para cambiar de empresa
import json
from django.http import HttpResponse

# Create your views here.


from django.forms.models import inlineformset_factory
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render_to_response
from apps.administracion.models import Empresa
from django.conf import settings

from urllib.parse import urlparse
from django.template.context_processors import csrf
from django.views import View
from django.contrib import auth
from .special_func import get_next_url


class ChangeCompanyList(ListView):
    template_name = 'usuario/change_company.html'

    def get_queryset(self):
        return Empresa.objects.all()


def ChangeCompanyAjax(request):
    if request.method == 'POST':
        post_company = request.POST.get('the_post')
        post_company_name = request.POST.get('the_post_company')

        response_data = {}
        if post_company != '':
            request.session['company_id'] = post_company
            request.session['company_name'] = post_company_name

            response_data['result'] = True
            response_data['text'] = 'Company change post successful!'
        else:
            response_data['result'] = False
            response_data['text'] = 'Company change post fail!'

        response_data['author'] = request.user.username

        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )
    else:
        return HttpResponse(
            json.dumps({"nothing to see": "this isn't happening"}),
            content_type="application/json"
        )


class SecretPage(LoginRequiredMixin, TemplateView):
    template_name = 'usuario/secret_page.html'

    def get(self, request):
        current_company_id = self.request.session['company_id']
        if current_company_id != 0:
            empresa_obj = Empresa.objects.get(pk=current_company_id)
            company_name = empresa_obj.nombre_comercial
        else:
            company_name = ' -*- NINGUNA -*-'
        return render(request, self.template_name, {
            'company_name': company_name,
        })


"""class CustomLoginView(LoginView):

    form_class = LoginForm
    template_name = 'login.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated and self.request.user.is_staff and has_2fa(self.request):
            return redirect('{}'.format(self.request.GET.get('next', '/')))

        return super(CustomLoginView, self).get(request, *args, **kwargs)

    def form_valid(self, form):

        if self.request.user.is_staff and not has_2fa(self.request):
            logger.info('is staff but does not have 2FA, redirecting to Authy account creator')
            auth_login(self.request, form.get_user(), backend='django.contrib.auth.backends.ModelBackend')
            return redirect('2fa_register')

        return super(CustomLoginView, self).form_valid(form)"""


class HLoginView(View):

    def get(self, request):
        # if the user is logged in, then do a redirect to the home page
        if auth.get_user(request).is_authenticated:
            return redirect('/')
        else:
            # Otherwise, form a context with the authorization form
            # and we return to this page context.
            # It works, for url - /admin/login/ and for /accounts/login/
            context = create_context_username_csrf(request)

            companies = Empresa.objects.all()
            context['companies'] = companies

            return render_to_response('registration/login-register.html', context=context)

    def post(self, request):
        # having received the authorization request

        if "company" in request.POST:
            selected_value = request.POST["company"]
        else:
            selected_value = None

        form = AuthenticationForm(request, data=request.POST)

        # check the correct form, that there is a user and he entered the correct password
        if form.is_valid() and selected_value:
            # if successful authorizing user
            auth.login(request, form.get_user())
            # get previous url
            next = urlparse(get_next_url(request)).path
            # and if the user of the number of staff and went through url /admin/login/
            # then redirect the user to the admin panel
            if next == '/admin/login/' and request.user.is_staff:
                return redirect('/admin/')
            # otherwise do a redirect to the previous page,
            # in the case of a / accounts / login / will happen is another redirect to the home page
            # in the case of any other url, will return the user to the url

            # Set a session value
            #print('COMPANY_ID=%s' % (selected_value))
            request.session['company_id'] = selected_value
            #user_settings.COMPANY_SESSION_KEY = selected_value

            return redirect(next)

        # If not true, then the user will appear on the login page
        # and see an error message
        context = create_context_username_csrf(request)
        context['form'] = form

        companies = Empresa.objects.all()
        context['companies'] = companies

        return render_to_response('registration/login-register.html', context=context)

# helper method to generate a context csrf_token
# and adding a login form in this context


def create_context_username_csrf(request):
    context = {}
    context.update(csrf(request))
    context['form'] = AuthenticationForm
    return context


def login_user(request):
    context = RequestContext(request)
    logout(request)
    username = password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/')
        else:
            # Return an 'invalid login' error message.
            print("invalid login details " + username + " " + password)
            return render(request, 'registration/login-register.html', {}, context)

    # the login is a  GET request, so just show the user the login form.
    companies = Empresa.objects.all()
    return render(request, 'registration/login-register.html', {"companies": companies}, context)


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            user.perfil.fecha_nacimiento = form.cleaned_data.get('fecha_nacimiento')
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


def edit_user(request, pk):
    user = User.objects.get(pk=pk)
    user_form = UserProfileForm(instance=user)

    # ProfileInlineFormset = inlineformset_factory(User, Perfil, fields=(
    #    'biografia', 'fecha_nacimiento', 'papel', 'foto'))
    #formset = ProfileInlineFormset(instance=user)

    if request.user.is_authenticated and request.user.is_staff:
        ProfileInlineFormset = inlineformset_factory(User, Perfil, fields=(
            'biografia', 'fecha_nacimiento', 'papel', 'foto'))
        formset = ProfileInlineFormset(instance=user)

        # editar perfil con superusuario
        if request.method == 'POST':
            user_form = UserProfileForm(request.POST, request.FILES, instance=user)
            formset = ProfileInlineFormset(request.POST, request.FILES, instance=user)
            if user_form.is_valid():
                created_user = user_form.save(commit=False)
                formset = ProfileInlineFormset(request.POST, request.FILES, instance=created_user)

                if formset.is_valid():
                    #print("ahora aqui...")
                    created_user.save()
                    formset.save()
                    # save_file(request.FILES['foto'])

                    return HttpResponseRedirect('/administracion/usuarios/')

        return render(request, "account/account_update.html", {
            "noodle": pk,
            "noodle_form": user_form,
            "formset": formset,
        })

    else:
        ProfileInlineFormset = inlineformset_factory(User, Perfil, fields=(
            'biografia', 'fecha_nacimiento', 'foto'))
        formset = ProfileInlineFormset(instance=user)

        # modificar perfil usuario normal
        if request.user.is_authenticated and request.user.id == user.id:
            if request.method == 'POST':
                user_form = UserProfileForm(request.POST, request.FILES, instance=user)
                formset = ProfileInlineFormset(request.POST, request.FILES, instance=user)

                if user_form.is_valid():
                    created_user = user_form.save(commit=False)
                    formset = ProfileInlineFormset(
                        request.POST, request.FILES, instance=created_user)

                    if formset.is_valid():
                        created_user.save()
                        formset.save()
                        # save_file(request.FILES['foto'])
                        return HttpResponseRedirect('/administracion/usuarios/')

            return render(request, "account/account_update.html", {
                "noodle": pk,
                "noodle_form": user_form,
                "formset": formset,
            })
        else:
            raise PermissionDenied


def save_file(file, path=''):
    filename = file._get_name()
    print("=============== IMAGEN =================")
    print('%s/avatars/%s' % (settings.MEDIA_ROOT, str(path) + str(filename)))
    fd = open('%s/avatars/%s' % (settings.MEDIA_ROOT, str(path) + str(filename)), 'wb')
    for chunk in file.chunks():
        fd.write(chunk)
    fd.close()


class ListadoUsuarios(ListView):
    model = User
    template_name = 'usuario/listado_usuarios.html'
    context_object_name = 'usuarios'


class DetailUser(DetailView):
    model = User
    template_name = 'account/account_detail.html'


class DeleteUser(DeleteView):
    model = User
    template_name = 'account/account_delete.html'
    success_url = reverse_lazy('administracion:listado_usuarios')
