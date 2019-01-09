from django.shortcuts import render
from django.views.generic.base import View
from django.contrib.auth.models import User
from comum.models import Perfil
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from comum.forms import CriarPerfilForm
from django.utils import timezone
from django.contrib.auth.hashers import make_password



def logar(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        redirect('/index/')

def change_password(request):
    return HttpResponseRedirect('/account/password-reset')

def add_user(request):
    return render(request,'flash_add_user.html')

class CadastraPerfilView(View):

    def get(self, request):
        return render(request, 'flash_add_user.html')

    def post(self,request):
        form = CriarPerfilForm(request.POST)
        print(form)
        if(form.is_valid()):
            dados = form.data
            senha = make_password("%s"%dados['password'])

            usuario = User(username = dados['username'],
                        first_name = dados['first_name'],
                        last_name = dados['last_name'],
                        email = dados['email'],
                        password=senha,
                        last_login = timezone.now(),
                        is_superuser = False,
                        is_staff = True,
                        is_active = True,
                        date_joined = timezone.now())

            usuario.save()

            perfil = Perfil(data_nasc=timezone.now(),
                        criado_em=timezone.now(),
                        atualizado_em=timezone.now(),
                        sexo='F',
                        telefone='32194422',
                        foto_perfil='imagens/2019/default_foto.png',
                        capa='imagens/2019/default_capa.jpg',
                        usuario_id= usuario.id)

            perfil.save()
            return redirect('/login/')

        return render(request, 'login.html',{'form':form})