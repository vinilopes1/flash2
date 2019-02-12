from django.db import transaction
from django.shortcuts import render, get_object_or_404
from django.views.generic.base import View
from django.contrib.auth.models import User
from comum.models import Perfil
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login as auth_login
from django.http import HttpResponseRedirect
from comum.forms import CriarPerfilForm,EditarPerfilForm
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import check_password
from django.contrib.auth.views import logout_then_login
from rest_framework.authtoken.models import Token
import os
import requests

def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request.POST)
        username = request.POST['username']
        password = request.POST['password']
        usuario = User.objects.get(username=username)
        match_check = check_password(password,usuario.password)
        if not match_check:
            messages.error(request, 'Usuário e/ou senha incorretos')

            return redirect('login')
        else:
            if usuario.is_active == False:
                usuario.is_active = True
                messages.success(request, 'O seu perfil foi reativado com sucesso!')
                usuario.save()
            user = authenticate(username=username, password=password)
            if user is not None:
                get_token(request)
                auth_login(request, user)
                return redirect('/')
            else:
                messages.error(request, 'Usuário não existe!')
                return redirect('/login')

    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout(request):
    Token.objects.get(user_id=request.user.id).delete()
    return logout_then_login(request,login_url='/login')


def change_password(request):
    return HttpResponseRedirect('/account/password-reset')

def add_user(request):
    return render(request,'flash_add_user.html')

class CadastraPerfilView(View):

    def get(self, request):
        return render(request, 'flash_add_user.html' )

    @transaction.atomic(using=None, savepoint=True)
    def post(self,request):
        url_media = 'http://127.0.0.1:8000/media/imagens/2019/'
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
                        foto_perfil='%sdefault_foto.png'%url_media,
                        capa='%sdefault_capa.jpg'%url_media,
                        usuario_id=usuario.id)

            perfil.save()
            return redirect('/login/')

        messages.error(request,'Algo deu errado, preencha corretamente seus dados.')

        return render(request, 'flash_add_user.html',{'form':form})

class EditaPerfilView(View):

    def get(self, request):
        usuario_logado = User.objects.get(pk=request.user.id)
        return render(request, 'flash_edit_perfil.html', {'usuario': usuario_logado})

    @transaction.atomic(using=None, savepoint=True)
    def post(self,request):
        url_media = 'http://127.0.0.1:8000/media/imagens/2019/'
        url_usuario = 'http://127.0.0.1:8000/api/v1/usuarios/%s'%request.user.id
        url_perfil = 'http://127.0.0.1:8000/api/v1/perfil/%s'%request.user.id
        token = Token.objects.get(user_id=request.user.id)
        auth_token = "token %s" % token

        headers = {"Content-Type": "application/json",
                   "Authorization": auth_token}

        if request.method == "POST":
            form = EditarPerfilForm(request.POST,request.FILES)
            dados = form.data
            if(form.is_valid()):
                if request.FILES:
                    if str(request.FILES)[24] == 'p':
                        foto = {
                            'foto_perfil': "%s%s"%(url_media,(str(request.FILES['foto_perfil'])))
                        }
                        requests.patch(url_perfil,data=foto)
                        handle_uploaded_file(request.FILES['foto_perfil'], str(request.FILES['foto_perfil']))

                    elif str(request.FILES)[24] == 'c':
                        capa = {
                            'capa': "%s%s"%(url_media,(str(request.FILES['foto_capa'])))
                        }
                        requests.patch(url_perfil, data=capa)
                        handle_uploaded_file(request.FILES['foto_capa'], str(request.FILES['foto_capa']))

                usuario = {
                    'first_name' : dados['first_name'],
                    'last_name' : dados['last_name']
                }
                perfil = {
                    'telefone': dados['telefone']
                }
                print(headers)
                requests.patch(url_usuario, data=usuario).headers.update(headers)
                requests.patch(url_perfil, data=perfil).headers.update(headers)

            return redirect('/about/%s' % request.user.id)
        else:
            form = EditarPerfilForm(instance=request.user.id)

        return render(request, 'flash_edit_perfil.html',{'form':form})

def handle_uploaded_file(file, filename):
    if not os.path.exists('../media_cdn/imagens/2019/'):
        os.mkdir('../media_cdn/imagens/2019/')

    with open('../media_cdn/imagens/2019/' + filename, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

def get_token(request):

    body = {'username': request.POST['username'],
            'password': request.POST['password']}

    url = 'http://127.0.0.1:8000/api/v1/token/'

    headers = {"Content-Type": "application/json",
               "Accept-Language": "en",
               "Date": "Wed, 19 Dec 2018 19:46:12 GMT",
               "X-Api-Key": ""}

    token = requests.post(url, json=body, headers=headers).json()['token']

    return token