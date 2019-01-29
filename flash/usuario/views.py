from django.db import transaction
from django.shortcuts import render, get_object_or_404
from django.views.generic.base import View
from django.contrib.auth.models import User
from comum.models import Perfil
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login as auth_login
from django.http import HttpResponseRedirect
from comum.forms import CriarPerfilForm
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import check_password

# def logar(request):
#     username = request.POST['username']
#     password = request.POST['password']
#     user = authenticate(request, username=username, password=password)
#     if user is not None:
#         # usuario = User.objects.get(username=username)
#         # usuario.is_active = True
#         # usuario.save()
#         login(request, user)
#         redirect('/index/')
#     else:
#         messages.error(request, 'username or password not correct')
#         return redirect('login')

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
                auth_login(request, user)
                return redirect('/')


    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def change_password(request):
    return HttpResponseRedirect('/account/password-reset')

def add_user(request):
    return render(request,'flash_add_user.html')



class CadastraPerfilView(View):

    def get(self, request):
        return render(request, 'flash_add_user.html' )

    @transaction.atomic()
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

class EditaPerfilView(View):

    def get(self, request):
        usuario_logado = User.objects.get(pk=request.user.id)
        return render(request, 'flash_edit_perfil.html', {'usuario': usuario_logado})

    @transaction.atomic()
    def post(self,request):
        perfil_logado = Perfil.objects.get(pk = request.user.id)
        if request.method == "POST":
            form = CriarPerfilForm(request.POST, instance=perfil_logado)
            if(form.is_valid()):
                dados = form.data
                senha = make_password("%s"%dados['password'])
                foto_perfil = 'imagens/2019/default_foto.png'
                foto_capa = 'imagens/2019/default_capa.jpg'
                if dados['foto_perfil'] !=  None:
                    foto_perfil =dados['foto_perfil']
                if dados ['foto_capa'] != None:
                    foto_capa = dados['foto_capa']

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
                            foto_perfil= foto_perfil,
                            capa= foto_capa,
                            usuario_id= usuario.id)

                perfil.save()
                return redirect('/about/%s' % perfil_logado.id)
        else:
            form = CriarPerfilForm(instance=perfil_logado)

        return render(request, 'flash_edit_perfil.html',{'form':form})
