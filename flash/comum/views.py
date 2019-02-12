from django.shortcuts import render, redirect

from comum.models import Comentario
from .forms import PostForm, ColecaoForm, ComentarPostForm
from django.contrib.auth.decorators import login_required
from django.views.generic.base import View
from comum.models import User, Post, Perfil, Colecao
from friendship.models import Friend, Follow, Block
from friendship.models import FriendshipRequest
from django.utils import timezone
from random import randint
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.contrib import messages
from .forms import PostForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework.authtoken.models import Token
import requests, json
import os


# Create your views here.

@login_required(login_url='/login')
def exibir_newsfeed(request):
    usuario_logado = request.user
    posts_all = Post.objects.all()
    amigos = lista_amigos(request.user)
    qtd_amigos = quant_amigos(request.user)
    usuarios_nao_amigo = nao_amigo(request.user)
    posts_amigos = []
    comentarios = Comentario.objects.all()

    for post in posts_all:
        if post.usuario_id == request.user.id:
            posts_amigos.append(post)
        else:
            for amigo in amigos:
                if post.usuario_id == amigo.id and Block.objects.is_blocked(amigo,
                                                                            request.user) == False and post.usuario.usuario.is_active == True:
                    if post.colecao == None:
                        posts_amigos.append(post)
                    elif request.user.id in Colecao.objects.get(pk=post.colecao.id).seguidores.all():
                        posts_amigos.append(post)

    for post in posts_all:
        if post.colecao is not None and post not in posts_amigos:
            colecao = Colecao.objects.get(pk=post.colecao.id)
            seguidores = colecao.seguidores.all()
            for seguidor in seguidores:
                if request.user.id == seguidor.id:
                    posts_amigos.append(post)
            # if post.colecao.seguidores:
            #     posts_amigos.append(post)

    posts_amigos = sorted(posts_amigos, key=Post.get_id, reverse=True)

    paginator = Paginator(posts_amigos, 10)

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
        posts = paginator.page(page)
    except (EmptyPage, InvalidPage):
        posts = paginator.page(paginator.num_pages)

    return render(request, "flash_newsfeed.html", {'usuario_logado': usuario_logado, 'qtd_amigos': qtd_amigos,
                                                   'usuarios_nao_amigo': usuarios_nao_amigo[:6],
                                                   'posts': posts, 'comentarios': comentarios})


def post_detail(request, post_id):
    post = Post.objects.get(pk=post_id)
    qtd_amigos = quant_amigos(request.user)
    usuarios_nao_amigo = nao_amigo(request.user)
    return render(request, "flash_post_detail.html",
                  {'post': post, 'qtd_amigos': qtd_amigos, 'usuarios_nao_amigo': usuarios_nao_amigo})


@login_required(login_url='/login')
def exibir_minha_timeline(request):
    usuario = request.user
    posts_usuario = Post.objects.filter(usuario_id=request.user.id).order_by('-criado_em')
    paginator = Paginator(posts_usuario, 10)

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
        posts = paginator.page(page)
    except (EmptyPage, InvalidPage):
        posts = paginator.page(paginator.num_pages)

    return render(request, "flash_timeline.html", {'usuario': usuario, 'posts': posts})


def handle_uploaded_file(file, filename):
    if not os.path.exists('../media_cdn/arquivos/2019/posts'):
        os.mkdir('../media_cdn/arquivos/2019/posts/')

    with open('../media_cdn/arquivos/2019/posts/' + filename, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

@login_required
def delete_post(request, string, post_id):
    Post.objects.get(pk=post_id).delete()
    messages.success(request, 'A publicação foi excluída!')
    if string == 'dt':
        return redirect('/timeline')
    elif string == 'su':
        return redirect('/settings')
    else:
        return redirect('/')


def lista_amigos(usuario):
    # friends = Friend.objects.friends(request.user)
    minhas_amizades = Friend.objects.filter(from_user=usuario)
    amigos = []
    for amizade in minhas_amizades:
        if amizade.to_user.is_active == True:
            amigos.append(amizade.to_user)
    return amigos


def todos_usuarios():
    usuarios = User.objects.all()
    return usuarios


def todos_perfis(request):
    perfis = Perfil.objects.all()
    return perfis


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

@login_required
def exibir_flash_friends(request):
    meus_amigos = lista_amigos(request.user)
    usuarios = todos_usuarios()
    amigos = lista_amigos(request.user)
    usuarios_nao_amigo = []
    usuario_logado = request.user
    qtd_amigos = quant_amigos(request.user)
    paginator = Paginator(meus_amigos, 10)
    bloqueados = Block.objects.blocking(request.user)

    for amigo in amigos:
        if Block.objects.is_blocked(amigo, request.user):
            meus_amigos.remove(amigo)

    for usuario in usuarios:
        if usuario not in amigos and usuario != request.user:
            if len(FriendshipRequest.objects.filter(from_user_id=request.user.id, to_user_id=usuario.id)) == 0 and len(
                    FriendshipRequest.objects.filter(from_user_id=usuario.id,
                                                     to_user_id=request.user.id)) == 0 and usuario.is_active == True:
                usuarios_nao_amigo.append(usuario)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
        usuarios = paginator.page(page)
    except (EmptyPage, InvalidPage):
        usuarios = paginator.page(paginator.num_pages)

    return render(request, 'flash_friends.html',
                  {'usuarios': usuarios, 'qtd_amigos': qtd_amigos, 'usuarios_nao_amigo': usuarios_nao_amigo[:6],
                   'usuario_logado': usuario_logado, 'bloqueados': bloqueados})


@login_required
def exibir_friends_requests(request):
    solicitacoes = FriendshipRequest.objects.filter(to_user=request.user)
    qtd_amigos = quant_amigos(request.user)
    minhas_solicitacoes = []
    usuarios_nao_amigo = nao_amigo(request.user)
    for solicitacao in solicitacoes:
        if solicitacao.rejected == None and solicitacao.from_user.is_active == True:
            minhas_solicitacoes.append(solicitacao)

    return render(request, 'flash_friends_requests.html',
                  {'minhas_solicitacoes': minhas_solicitacoes, 'qtd_amigos': qtd_amigos,
                   'usuarios_nao_amigo': usuarios_nao_amigo[:6]})


def quant_amigos(usuario):
    amizades = Friend.objects.all()
    qtd_amigos = 0
    for amizade in amizades:
        if amizade.to_user_id == usuario.id:
            qtd_amigos += 1
    return qtd_amigos


@login_required
def exibir_usuario(request, usuario_id):
    usuario = User.objects.get(id=usuario_id)
    posts_usuario = Post.objects.filter(usuario_id=usuario_id).order_by('-criado_em')
    eh_amigo = False
    estou_bloqueado = False
    bloqueado = False
    solicitei = False
    solicitacoes = Friend.objects.unrejected_requests(usuario)
    paginator = Paginator(posts_usuario, 10)

    if usuario.is_active == False:
        messages.error(request, 'Usuário não encontrado.')
        return redirect('/')

    for solicitacao in solicitacoes:
        if solicitacao.from_user.id == request.user.id:
            solicitei = True

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

        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1
        try:
            posts = paginator.page(page)
        except (EmptyPage, InvalidPage):
            posts = paginator.page(paginator.num_pages)

        return render(request, "flash_timeline.html",
                      {'usuario': usuario, 'posts': posts, 'eh_amigo': eh_amigo,
                       'bloqueado': bloqueado, 'solicitei': solicitei})
    else:
        posts = []

        return render(request, "flash_timeline.html",
                      {'usuario': usuario, 'posts': posts, 'eh_amigo': eh_amigo,
                       'bloqueado': bloqueado, 'solicitei': solicitei})


def exibir_about(request, usuario_id):
    usuario = User.objects.get(pk=usuario_id)
    return render(request, 'flash_sobre.html', {'usuario': usuario})


@login_required
def alterar_senha(request):
    return render(request, 'flash_alterar_senha.html')


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        form.error_messages = {'password_mismatch': "Os campos para a nova senha não coincidem.",
                               'password_incorrect': 'Sua senha antiga está incorreta. Por favor, insira novamente.'}
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Sua senha foi atualizada com sucesso!')
            return redirect('/change-password/')
        else:
            return render(request, 'flash_alterar_senha.html', {
                'form': form
            })
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'flash_alterar_senha.html', {
        'form': form
    })


def nao_amigo(user):
    usuarios = todos_usuarios()
    amigos = lista_amigos(user)
    usuarios_nao_amigo = []

    for usuario in usuarios:
        if usuario not in amigos and usuario != user:
            if len(FriendshipRequest.objects.filter(from_user_id=user.id, to_user_id=usuario.id)) == 0 and len(
                    FriendshipRequest.objects.filter(from_user_id=usuario.id,
                                                     to_user_id=user.id)) == 0 and usuario.is_active == True:
                usuarios_nao_amigo.append(usuario)

    return usuarios_nao_amigo


@login_required
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


@login_required
def buscar_usuario(request):
    form = PostForm(request.POST)
    dados = form.data
    pesquisa = dados['busca_usuario']
    usuarios = todos_usuarios()
    resultados = []
    bloqueados = Block.objects.blocking(request.user)
    usuario_logado = request.user
    qtd_amigos = quant_amigos(request.user)

    for usuario in usuarios:
        if usuario.first_name.__contains__(pesquisa) or usuario.last_name.__contains__(
                pesquisa) or usuario.username.__contains__(pesquisa):
            if Block.objects.is_blocked(usuario, request.user) == False and usuario.is_active == True:
                resultados.append(usuario)

    return render(request, 'flash_friends_search.html',
                  {'resultados': resultados, 'bloqueados': bloqueados, 'usuario_logado': usuario_logado,
                   'qtd_amigos': qtd_amigos, 'qtd_result': len(resultados)})


@login_required
def exibir_flash_settings(request):
    perfis = todos_perfis(request)
    usuarios_nao_amigo = nao_amigo(request.user)
    qtd_amigos = quant_amigos(request.user)
    return render(request, 'flash_settings.html', {'perfis': perfis, 'qtd_amigos': qtd_amigos,
                                                   'usuarios_nao_amigo': usuarios_nao_amigo[:6]})


def definir_super_usuario(request, usuario_id):
    user = User.objects.get(pk=usuario_id)
    user.is_superuser = True
    user.save()
    perfis = todos_perfis(request)
    usuarios_nao_amigo = nao_amigo(request.user)
    qtd_amigos = quant_amigos(request.user)
    return render(request, 'flash_settings.html', {'perfis': perfis, 'qtd_amigos': qtd_amigos,
                                                   'usuarios_nao_amigo': usuarios_nao_amigo[:6]})


def definir_usuario_comum(request, usuario_id):
    user = User.objects.get(pk=usuario_id)
    user.is_superuser = False
    user.save()
    perfis = todos_perfis(request)
    usuarios_nao_amigo = nao_amigo(request.user)
    qtd_amigos = quant_amigos(request.user)
    return render(request, 'flash_settings.html', {'perfis': perfis, 'qtd_amigos': qtd_amigos,
                                                   'usuarios_nao_amigo': usuarios_nao_amigo[:6]})


@login_required
def gerenciar_posts(request, usuario_id):
    usuario = User.objects.get(pk=usuario_id)
    qtd_amigos = quant_amigos(request.user)
    usuarios_nao_amigo = nao_amigo(request.user)

    posts_usuario = Post.objects.filter(usuario_id=usuario_id).order_by('-criado_em')
    return render(request, 'flash_superuser_gerenciar_posts.html', {'usuario': usuario, 'posts_usuario': posts_usuario,
                                                                    'qtd_amigos': qtd_amigos,
                                                                    'usuarios_nao_amigo': usuarios_nao_amigo})


@login_required
def gerenciar_flash_friends(request, usuario_id):
    usuario_gerenciado = User.objects.get(pk=usuario_id)
    usuarios = lista_amigos(usuario_gerenciado)
    todos_users = todos_usuarios()
    amigos = lista_amigos(usuario_gerenciado)
    usuarios_nao_amigo = nao_amigo(request.user)
    usuario_logado = request.user
    qtd_amigos = quant_amigos(request.user)

    bloqueados = Block.objects.blocking(usuario_gerenciado)

    for amigo in amigos:
        if Block.objects.is_blocked(amigo, usuario_gerenciado):
            usuarios.remove(amigo)

    for usuario in todos_users:
        if usuario not in amigos and usuario != usuario_gerenciado:
            if len(FriendshipRequest.objects.filter(from_user_id=usuario_gerenciado.id,
                                                    to_user_id=usuario.id)) == 0 and len(
                    FriendshipRequest.objects.filter(from_user_id=usuario.id,
                                                     to_user_id=usuario_gerenciado.id)) == 0 and usuario.is_active == True:
                usuarios_nao_amigo.append(usuario)

    return render(request, 'flash_gerenciar_amigos.html',
                  {'usuarios': usuarios, 'qtd_amigos': qtd_amigos, 'usuarios_nao_amigo': usuarios_nao_amigo[:6],
                   'usuario_logado': usuario_logado, 'bloqueados': bloqueados, 'usuario': usuario_gerenciado})


@login_required
def gerenciar_friends_requests(request, usuario_id):
    usuario = User.objects.get(pk=usuario_id)
    solicitacoes = FriendshipRequest.objects.filter(to_user=usuario)
    qtd_amigos = quant_amigos(request.user)
    minhas_solicitacoes = []
    usuarios_nao_amigo = nao_amigo(request.user)
    for solicitacao in solicitacoes:
        if solicitacao.rejected == None and solicitacao.from_user.is_active == True:
            minhas_solicitacoes.append(solicitacao)

    return render(request, 'flash_gerenciar_solicitacoes.html',
                  {'minhas_solicitacoes': minhas_solicitacoes, 'qtd_amigos': qtd_amigos,
                   'usuarios_nao_amigo': usuarios_nao_amigo[:6], 'usuario': usuario})


def superuser_desativar_perfil(request, usuario_id):
    usuario = User.objects.get(pk=usuario_id)
    usuario.is_active = False
    usuario.save()
    messages.success(request, 'O perfil selecionado foi desativado com sucesso!')
    return redirect('/settings')


def superuser_ativar_perfil(request, usuario_id):
    usuario = User.objects.get(pk=usuario_id)
    usuario.is_active = True
    usuario.save()
    messages.success(request, 'O perfil selecionado foi ativado com sucesso!')
    return redirect('/settings')

@transaction.atomic(using=None, savepoint=True)
def rejeitar_pedido(request, solicitacao_id):
    url = 'http://127.0.0.1:8000/api/v1/friendship-requests/%s'%solicitacao_id
    token = Token.objects.get(user_id=request.user.id)
    auth_token = "token %s"%token

    headers = {"Content-Type": "application/json",
               "Authorization": auth_token}

    print(headers)

    requests.delete(url,headers=headers)
    messages.success(request,"A solicitação foi rejeitada com sucesso!")

    return redirect('/')


##MÓDULO API##

#POST WITH TOKEN
class AdicionaPostView(View):

    def get(self, request):
        return render(request, 'flash_newsfeed.html')

    def post(self, request):
        url = 'http://127.0.0.1:8000/api/v1/posts/'
        token = Token.objects.get(user_id=request.user.id)
        auth_token = 'token %s'%token

        headers = {'Content-Type': 'application/json',
                   'Authorization': auth_token}

        form = PostForm(request.POST, request.FILES)
        if (form.is_valid()):
            dados = form.data

            data = {'descricao': '%s' % dados['descricao'],
                    'usuario': request.user.id,
                    'colecao': None,
                    'compartilhado': None}

            requests.post(url,json=data,headers=headers)

            messages.success(request, 'Seu post foi publicado com êxito.')

            #post.save()
            print(request)
            return redirect('/')

        messages.error(request, 'Seu post NÃO foi publicado com êxito.')
        return redirect('/')


#TELEGRAM
#GET WITH TOKEN
@login_required
def exibir_colecoes(request):
    usuarios_nao_amigo = nao_amigo(request.user)
    url_colecoes = 'http://127.0.0.1:8000/api/v1/colecoes/'
    token = Token.objects.get(user_id=request.user.id)

    headers = {"X-Auth-Token": token,
               "Accept-Language": "en",
               "Date": "Tue, 11 Feb 2019 20:00:00 GMT",
               "X-Api-Key": ""}

    colecoes = requests.get(url_colecoes,headers).json()
    qtd_amigos = quant_amigos(request.user)

    return render(request, 'flash_colecoes.html',
                  {'colecoes': colecoes, 'usuarios_nao_amigo': usuarios_nao_amigo[:6], 'qtd_amigos': qtd_amigos})


def compartilhar_post(request, post_compartilhado_id):
    url = 'http://127.0.0.1:8000/api/v1/posts/'
    token = Token.objects.get(user_id=request.user.id)
    auth_token = 'token %s' % token

    headers = {'Content-Type': 'application/json',
               'Authorization': auth_token}
    form = PostForm(request.POST, request.FILES)

    if (form.is_valid()):
        dados = form.data
        data = {'descricao': '%s' % dados['descricao'],
                'usuario': request.user.id,
                'colecao': None,
                'compartilhado': post_compartilhado_id}

        requests.post(url=url, json=data, headers=headers)
        messages.success(request, 'Post compartilhado com sucesso!.')
        return redirect('/')

    messages.error(request, 'O post NÃO foi compartilhado com êxito.')
    return redirect('/')

#PATCH
def desativar_perfil(request):
    url = 'http://127.0.0.1:8000/api/v1/usuarios/%s' % request.user.id

    data = {
        'is_active': False
    }
    requests.patch(url,data)

    return redirect('logout')

#GET IN COLEÇÕES
@login_required
def exibir_colecao(request, colecao_id):
    posts_colecao = []
    seguindo = False
    colecao = colecao_id
    url_colecao = 'http://127.0.0.1:8000/api/v1/colecoes/%s' % colecao
    colecao = requests.get(url_colecao).json()

    for iter in colecao['posts']:
        post = Post.objects.get(pk=iter['id'])
        posts_colecao.append(post)

    for seguidor in colecao['seguidores']:
        if seguidor['id'] == request.user.id:
            seguindo = True

    return render(request, 'flash_colecao.html', {'posts': posts_colecao, 'colecao': colecao, 'seguindo': seguindo})

#POST
@login_required
def add_post_colecao(request, colecao_id):
    url = 'http://127.0.0.1:8000/api/v1/posts/'
    form = PostForm(request.POST, request.FILES)

    if (form.is_valid()):
        dados = form.data
        data = {'descricao': '%s' % dados['descricao'],
                'usuario': request.user.id,
                'colecao': colecao_id,
                'compartilhado': None}
        requests.post(url=url, data=data)
        messages.success(request, 'Seu post foi publicado com êxito.')

        print(request)
        return redirect('/')

    messages.error(request, 'Seu post NÃO foi publicado com êxito.')
    return redirect('/')


def seguir_colecao(request, colecao_id):
    colecao = Colecao.objects.get(pk=colecao_id)
    colecao.seguidores.add(request.user.id)
    return redirect('/colecao/%s' % colecao_id)


def deixar_seguir_colecao(request, colecao_id):
    colecao = Colecao.objects.get(pk=colecao_id)
    colecao.seguidores.remove(request.user.id)
    return redirect('/colecao/%s' % colecao_id)


def exibir_minhas_colecoes(request):
    url = 'http://127.0.0.1:8000/api/v1/colecoes/'
    colecoes = requests.get(url).json()
    print(colecoes)
    minhas_colecoes = []
    for colecao in colecoes:
        if colecao['autor'] == request.user.id:
            minhas_colecoes.append(colecao)

    return render(request, 'flash_minhas_colecoes.html', {'usuario': request.user, 'minhas_colecoes': minhas_colecoes})


def handle_uploaded_file_foto_colecao(file, filename):
    if not os.path.exists('../media_cdn/imagens/2019/'):
        os.mkdir('../media_cdn/imagens/2019/')

    with open('../media_cdn/imagens/2019/' + filename, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)


@login_required
def add_colecao(request):
    url = 'http://127.0.0.1:8000/api/v1/colecoes/'
    form = ColecaoForm(request.POST, request.FILES)

    if (form.is_valid()):
        dados = form.data
        data = {'titulo': '%s' % dados['titulo'],
                'autor': request.user.id,
                'foto_perfil': "http://127.0.0.1:8000/media/imagens/2019/%s" % (str(request.FILES['foto'])),
                'capa': 'http://127.0.0.1:8000/media/imagens/2019/demo-bg.jpg'
                }
        requests.post(url=url, data=data)
        handle_uploaded_file_foto_colecao(request.FILES['foto'], str(request.FILES['foto']))

        messages.success(request, 'Seu coleção foi criada com êxito.')
        return redirect('/')

    messages.error(request, 'Algo deu errado.')
    return redirect('/')


class CompartilhaPostView(View):
    @login_required
    def get(self, request):
        return render(request, 'flash_newsfeed.html')

    @login_required
    def post(self, request, post_compartilhado_id):
        form = PostForm(request.POST)
        print(form)
        if (form.is_valid()):
            dados = form.data
            post = Post(descricao=dados['descricao'],
                        criado_em=timezone.now(),
                        atualizado_em=timezone.now(),
                        aplausos=randint(0, 100),
                        foto=None,
                        video=None,
                        editado=False,
                        compartilhado=Post.objects.get(pk=post_compartilhado_id),
                        colecao_id=None,
                        comunidade_id=None,
                        usuario_id=request.user.id)
            messages.success(request, 'Post compartilhado com sucesso!.')
            post.save()
            print(request)
            return redirect('/')
        messages.error(request, 'O post NÃO foi compartilhado com êxito.')
        return redirect('/')


class ComentaPostView(View):

    def get(self, request):
        return render(request, 'flash_newsfeed.html')

    def post(self, request, post_comentado_id):
        post_comentado = Post.objects.get(pk=post_comentado_id)
        form = ComentarPostForm(request.POST)
        if (form.is_valid()):
            dados = form.data
            comentario = Comentario(descricao=dados['descricao'],
                                    criado_em=timezone.now(),
                                    atualizado_em=timezone.now(),
                                    editado=False,
                                    usuario_id=request.user.id,
                                    post=post_comentado)
            messages.success(request, 'Seu comentário foi realizado com êxito.')

            comentario.save()
            print(request)
            return redirect('/')

        messages.error(request, 'Seu comentário NÃO foi realizado com êxito.')
        return redirect('/post-detail/%s' % post_comentado_id)


def exibir_comentarios_post(request, post_comentado_id):
    post_comentado = Post.objects.get(pk=post_comentado_id)
    comentarios = []
    comentarios_all = Comentario.objects.all()
    for comentario in comentarios_all:
        if comentario.post == post_comentado:
            comentarios.append(comentario)

    return redirect('/', {'comentarios': comentarios})



