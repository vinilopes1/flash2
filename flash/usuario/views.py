from django.shortcuts import render
from django.views.generic.base import View
from django.contrib.auth.models import User
from comum.models import Perfil
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login


def logar(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        redirect('/index/')
    else:
        print("Não deu certo!")