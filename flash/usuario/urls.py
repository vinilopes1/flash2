from django.urls import path, include
from django.contrib.auth.views import login, logout_then_login, password_reset,\
    password_reset_done, password_reset_confirm, password_reset_complete
from usuario import views as views_usuario
from comum import views
from django.views.generic import RedirectView,TemplateView

urlpatterns = [
    ##Usuario##
    path('login/', login, {'template_name': 'login.html'}, name='login'  ),
    path('logout/', logout_then_login, {'login_url': 'login'},name= 'logout'),
    path('reset-password', views_usuario.change_password ,name='reset-password'),
    path('account/password-reset/', password_reset , name='password_reset' ),
    path('account/password-reset/done/', password_reset_done,name='password_reset_done'),
    path('account/password-reset/confirm/<uidb64>/<token>/',password_reset_confirm , name='password_reset_confirm'),
    path('account/password-reset/complete/', password_reset_complete, name='password_reset_complete'),

]