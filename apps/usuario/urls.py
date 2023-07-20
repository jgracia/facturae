from django.contrib.auth.decorators import login_required
from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static

app_name = 'usuario'
urlpatterns = [
    #path('registrar/', login_required(views.RegistroUsuario.as_view()), name='registrar'),
    #path('profiles/new/', views.NewUserProfileView.as_view(), name="new_user_profile"),
    #path('users/<int:pk>', views.EditUserProfileView.as_view(), name="edit_user_profile"),
    #path('add_user/', login_required(views.add_user), name='add_user'),

    path('edit_user/<int:pk>', views.edit_user, name="edit_user"),
    path('detail_user/<int:pk>', login_required(views.DetailUser.as_view()), name='detail_user'),
    path('delete_user/<int:pk>', login_required(views.DeleteUser.as_view()), name='delete_user'),

    path('change_company_list/', login_required(views.ChangeCompanyList.as_view()),
         name='change_company_list'),
    path('change_company_ajax/', login_required(views.ChangeCompanyAjax), name='change_company_ajax'),
    path('secret/', login_required(views.SecretPage.as_view()), name='secret'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
