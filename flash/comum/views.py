from django.shortcuts import render, redirect
from .forms import PostForm
from django.contrib.auth.decorators import login_required
from django.views.generic.base import View
from comum.models import User, Post, Perfil
from friendship.models import Friend, Follow, Block
from friendship.models import FriendshipRequest
from django.utils import timezone
from random import randint
from django.contrib import messages
from .forms import PostForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash


# Create your views here.

@login_required(login_url='/login')
def exibir_newsfeed(request):
    usuario_logado = request.user
    posts = Post.objects.all()
    amigos = lista_amigos(request)
    qtd_amigos = quant_amigos(request)
    usuarios_nao_amigo = nao_amigo(request)
    bloqueados = Block.objects.blocking(request.user)
    posts_amigos = []
    for post in posts:
        if post.usuario_id == request.user.id:
            posts_amigos.append(post)
        else:
            for amigo in amigos:
                for bloqueado in bloqueados:
                    if post.usuario_id == amigo.id and post.usuario.id != bloqueado.id:
                        posts_amigos.append(post)

    return render(request, "flash_newsfeed.html", {'usuario_logado': usuario_logado, 'qtd_amigos': qtd_amigos,
                                                   'usuarios_nao_amigo': usuarios_nao_amigo[:6],
                                                   'posts_amigos': posts_amigos})


@login_required(login_url='/login')
def exibir_minha_timeline(request):
    usuario = request.user
    posts_usuario = Post.objects.filter(usuario_id=request.user.id).order_by('-criado_em')

    return render(request, "flash_timeline.html", {'usuario': usuario, 'posts_usuario': posts_usuario})


class AdicionaPostView(View):

    def get(self, request):
        return render(request, 'flash_newsfeed.html')

    def post(self, request):
        form = PostForm(request.POST)

        if (form.is_valid()):
            dados = form.data

            post = Post(descricao=dados['descricao'],
                        criado_em=timezone.now(),
                        atualizado_em=timezone.now(),
                        anexo=None,
                        aplausos=randint(0, 100),
                        editado=False,
                        compartilhado=False,
                        colecao_id=None,
                        comunidade_id=None,
                        usuario_id=request.user.id)

            post.save()
            print(request)
            return redirect('/')

        return render(request, 'flash_newsfeed.html', {'form': form})


def delete_post(request, post_id):
    Post.objects.get(pk=post_id).delete()
    messages.success(request, 'Sua publicação foi excluída!')
    return redirect('/timeline')


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
    return redirect('/')


def aceitar_pedido(request, solicitacao_id):
    friend_request = FriendshipRequest.objects.get(pk=solicitacao_id)
    friend_request.accept()
    messages.success(request, 'Você e %s agora são amigos(a)!' % friend_request.from_user.first_name)
    return redirect('/requests')


def rejeitar_pedido(request, solicitacao_id):
    friend_request = FriendshipRequest.objects.get(pk=solicitacao_id)
    friend_request.reject()
    return render(request, 'flash_newsfeed.html')


def exibir_flash_friends(request):
    meus_amigos = lista_amigos(request)
    usuarios = todos_usuarios(request)
    amigos = lista_amigos(request)
    usuarios_nao_amigo = []
    usuario_logado = request.user
    qtd_amigos = quant_amigos(request)

    bloqueados = Block.objects.blocking(request.user)

    for usuario in usuarios:
        if usuario not in amigos and usuario != request.user:
            if len(FriendshipRequest.objects.filter(from_user_id=request.user.id, to_user_id=usuario.id)) == 0 and len(
                    FriendshipRequest.objects.filter(from_user_id=usuario.id, to_user_id=request.user.id)) == 0:
                usuarios_nao_amigo.append(usuario)
    return render(request, 'flash_friends.html',
                  {'meus_amigos': meus_amigos, 'qtd_amigos': qtd_amigos, 'usuarios_nao_amigo': usuarios_nao_amigo[:6],
                   'usuario_logado': usuario_logado, 'bloqueados': bloqueados})


def exibir_friends_requests(request):
    solicitacoes = FriendshipRequest.objects.filter(to_user=request.user)
    qtd_amigos = quant_amigos(request)
    minhas_solicitacoes = []
    usuarios_nao_amigo = nao_amigo(request)
    for solicitacao in solicitacoes:
        if solicitacao.rejected == None:
            minhas_solicitacoes.append(solicitacao)

    return render(request, 'flash_friends_requests.html',
                  {'minhas_solicitacoes': minhas_solicitacoes, 'qtd_amigos': qtd_amigos,
                   'usuarios_nao_amigo': usuarios_nao_amigo[:6]})


def quant_amigos(request):
    amizades = Friend.objects.all()
    qtd_amigos = 0
    for amizade in amizades:
        if amizade.to_user_id == request.user.id:
            qtd_amigos += 1
    return qtd_amigos


def exibir_usuario(request, usuario_id):
    usuario = User.objects.get(id=usuario_id)
    posts_usuario = Post.objects.filter(usuario_id=usuario_id).order_by('-criado_em')
    eh_amigo = False
    estou_bloqueado = False
    bloqueado = False
    if Friend.objects.are_friends(request.user, usuario):
        eh_amigo = True

    if Block.objects.is_blocked(usuario, request.user):
        estou_bloqueado = True

    if Block.objects.is_blocked(request.user, usuario):
        bloqueado = True

    if estou_bloqueado:
        messages.error(request, 'Você não tem permissão para acessar este usuário.')
        return redirect('/')

    if eh_amigo:
        return render(request, "flash_timeline.html",
                      {'usuario': usuario, 'posts_usuario': posts_usuario, 'eh_amigo': eh_amigo,
                       'bloqueado': bloqueado})
    else:
        posts_usuario = []
        return render(request, "flash_timeline.html",
                      {'usuario': usuario, 'posts_usuario': posts_usuario, 'eh_amigo': eh_amigo,
                       'bloqueado': bloqueado})


def exibir_about(request):
    return render(request, 'sobre.html')


def alterar_senha(request):
    return render(request, 'alterar_senha.html')


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {
        'form': form
    })


def nao_amigo(request):
    usuarios = todos_usuarios(request)
    amigos = lista_amigos(request)
    usuarios_nao_amigo = []

    for usuario in usuarios:
        if usuario not in amigos and usuario != request.user:
            if len(FriendshipRequest.objects.filter(from_user_id=request.user.id, to_user_id=usuario.id)) == 0 and len(
                    FriendshipRequest.objects.filter(from_user_id=usuario.id, to_user_id=request.user.id)) == 0:
                usuarios_nao_amigo.append(usuario)

    return usuarios_nao_amigo


def desfazer_amizade(request, usuario_id):
    usuario = User.objects.get(pk=usuario_id)
    Friend.objects.remove_friend(request.user, usuario)
    return redirect('/usuario/%s' % usuario_id)


def bloquear_usuario(request, usuario_id):
    usuario = User.objects.get(pk=usuario_id)
    Block.objects.add_block(request.user, usuario)
    return redirect('/usuario/%s' % usuario_id)


def desbloquear_usuario(request, usuario_id):
    usuario = User.objects.get(pk=usuario_id)
    Block.objects.remove_block(request.user, usuario)
    return redirect('/usuario/%s' % usuario_id)


def buscar_usuario(request):
    form = PostForm(request.POST)
    dados = form.data
    pesquisa = dados['busca_usuario']
    usuarios = todos_usuarios(request)
    resultados = []
    bloqueados = Block.objects.blocking(request.user)
    usuario_logado = request.user
    qtd_amigos = quant_amigos(request)

    for usuario in usuarios:
        if usuario.first_name.__contains__(pesquisa) or usuario.last_name.__contains__(
                pesquisa) or usuario.username.__contains__(pesquisa):
            resultados.append(usuario)

    print(resultados)
    return render(request, 'flash_friends_search.html',
                  {'resultados': resultados, 'bloqueados': bloqueados, 'usuario_logado': usuario_logado,
                   'qtd_amigos': qtd_amigos, 'qtd_result':len(resultados)})
