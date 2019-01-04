from django.shortcuts import render, redirect
from .forms import PostForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from comum.models import User,Post
from friendship.models import Friend, Follow, Block
from friendship.models import FriendshipRequest

# Create your views here.

@login_required(login_url='/login')
def exibir_newsfeed(request):
    usuario_logado = request.user
    usuarios = todos_usuarios(request)
    posts = Post.objects.all()
    amigos = lista_amigos(request)
    usuarios_nao_amigo, posts_amigos = [],[]
    for post in posts:
        for amigo in amigos:
            if post.usuario_id == amigo.id:
                posts_amigos.append(post)

    for usuario in usuarios:
        if usuario not in amigos and usuario != request.user:
            usuarios_nao_amigo.append(usuario)

    print(usuarios_nao_amigo)
    return render(request, "newsfeed.html", {'usuario_logado': usuario_logado, 'usuarios_nao_amigo': usuarios_nao_amigo, 'posts_amigos': posts_amigos})

@login_required(login_url='/login')
def exibir_minha_timeline(request):
    usuario_logado = request.user
    meus_posts = Post.objects.filter(usuario_id=request.user.id).order_by('-criado_em')
    return render(request, "timeline.html", {'usuario_logado': usuario_logado, 'meus_posts': meus_posts})

def index(request):
    form = PostForm()
    return render(request, 'index.html',{'form':form})

def novo_post(request):

    if request.method == "POST":
        print('Post')
        form = PostForm(request.POST)
        if form.is_valid():
            print('Valido')
            post = form.save(commit=False)
            post.usuario = request.user
            post.criado_em = timezone.now()
            post.save()
            return redirect('index.html')
    else:
        form = PostForm()

    return render(request, 'edit_post.html', {'form':form})

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
    return render(request,'newsfeed.html')

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
    return render(request, 'flash_friends.html', {'meus_amigos': meus_amigos})

def exibir_friend_requests(request):
    solicitacoes = FriendshipRequest.objects.filter(to_user=request.user)
    print(solicitacoes)
    minhas_solicitacoes = []
    for solicitacao in solicitacoes:
        if solicitacao.rejected == None:
            minhas_solicitacoes.append(solicitacao)

    return render(request, 'friend_requests.html',{'minhas_solicitacoes': minhas_solicitacoes})