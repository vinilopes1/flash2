from django.shortcuts import render, redirect
from .forms import PostForm
from django.contrib.auth.decorators import login_required
from django.views.generic.base import View
from comum.models import User,Post,Perfil
from friendship.models import Friend, Follow, Block
from friendship.models import FriendshipRequest
from django.utils import timezone
from random import randint
from django.contrib import messages

# Create your views here.

@login_required(login_url='/login')
def exibir_newsfeed(request):
    usuario_logado = request.user
    usuarios = todos_usuarios(request)
    posts = Post.objects.all()
    amigos = lista_amigos(request)
    qtd_amigos = quant_amigos(request)
    usuarios_nao_amigo, posts_amigos = [],[]
    for post in posts:
        for amigo in amigos:
            if post.usuario_id == amigo.id :
                posts_amigos.append(post)
        if post.usuario_id == request.user.id:
            posts_amigos.append(post)

    for usuario in usuarios:
        if usuario not in amigos and usuario != request.user:
            if len(FriendshipRequest.objects.filter(from_user_id=request.user.id,to_user_id=usuario.id)) == 0 and len(FriendshipRequest.objects.filter(from_user_id=usuario.id,to_user_id=request.user.id)) == 0:
                usuarios_nao_amigo.append(usuario)

    return render(request, "newsfeed.html", {'usuario_logado': usuario_logado, 'qtd_amigos':qtd_amigos, 'usuarios_nao_amigo': usuarios_nao_amigo, 'posts_amigos': posts_amigos})

@login_required(login_url='/login')
def exibir_minha_timeline(request):
    usuario_logado = request.user
    meus_posts = Post.objects.filter(usuario_id=request.user.id).order_by('-criado_em')

    return render(request, "timeline.html", {'usuario_logado': usuario_logado, 'meus_posts': meus_posts})

def index(request):
    form = PostForm()
    return render(request, 'index.html',{'form':form})

class AdicionaPostView(View):

    def get(self, request):
        return render(request, 'newsfeed.html')

    def post(self,request):
        form = PostForm(request.POST)

        if(form.is_valid()):
            dados = form.data

            post = Post(descricao=dados['descricao'],
                        criado_em=timezone.now(),
                        atualizado_em=timezone.now(),
                        anexo=None,
                        aplausos=randint(0,100),
                        editado=False,
                        compartilhado=False,
                        colecao_id=None,
                        comunidade_id=None,
                        usuario_id= request.user.id)
            post.save()
            return redirect('/newsfeed')

        return render(request, 'newsfeed.html',{'form':form})

def lista_amigos(request):
    friends = Friend.objects.friends(request.user)
    return friends

def todos_usuarios(request):
    usuarios = User.objects.all()
    return usuarios

def enviar_pedido(request, usuario_id):
    other_user = User.objects.get(pk=usuario_id)
    Friend.objects.add_friend(
        request.user,  # The sender
        other_user,  # The recipient
        message='Olá! Eu gostaria que você fosse meu Flash Friend')
    messages.success(request, 'Sua solicitação de amizade foi enviada!')
    return redirect('/newsfeed')

def aceitar_pedido(request, solicitacao_id):
    friend_request = FriendshipRequest.objects.get(pk=solicitacao_id)
    friend_request.accept()
    return render(request,'newsfeed.html')


def rejeitar_pedido(request, solicitacao_id):
    friend_request = FriendshipRequest.objects.get(pk=solicitacao_id)
    friend_request.reject()
    return render(request,'newsfeed.html')

def exibir_flash_friends(request):
    meus_amigos = lista_amigos(request)
    usuarios = todos_usuarios(request)
    amigos = lista_amigos(request)
    usuarios_nao_amigo = []
    usuario_logado = request.user
    qtd_amigos = quant_amigos(request)


    for usuario in usuarios:
        if usuario not in amigos and usuario != request.user:
            if len(FriendshipRequest.objects.filter(from_user_id=request.user.id,to_user_id=usuario.id)) == 0 and len(FriendshipRequest.objects.filter(from_user_id=usuario.id,to_user_id=request.user.id)) == 0:
                usuarios_nao_amigo.append(usuario)
    return render(request, 'flash_friends.html', {'meus_amigos': meus_amigos,'qtd_amigos':qtd_amigos, 'usuarios_nao_amigo': usuarios_nao_amigo, 'usuario_logado': usuario_logado})

def exibir_friend_requests(request):
    solicitacoes = FriendshipRequest.objects.filter(to_user=request.user)
    print(solicitacoes)
    minhas_solicitacoes = []
    for solicitacao in solicitacoes:
        if solicitacao.rejected == None:
            minhas_solicitacoes.append(solicitacao)

    return render(request, 'friend_requests.html',{'minhas_solicitacoes': minhas_solicitacoes})

def quant_amigos(request):
    amizades = Friend.objects.all()
    qtd_amigos = 0
    for amizade in amizades:
        if amizade.to_user_id == request.user.id:
            qtd_amigos+= 1
    return qtd_amigos
