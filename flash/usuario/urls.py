from django.urls import path
from django.contrib.auth.views import login, logout_then_login
from usuario import views
from comum import views
from django.views.generic import RedirectView

urlpatterns = [
    ##Usuario##
    path('login/', login, {'template_name': 'login.html'}, name='login'  ),
    path('logout/', logout_then_login, {'login_url': 'login'},name= 'logout'),
]