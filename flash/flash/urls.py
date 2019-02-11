"""flash URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path,include
from comum import views
from api import views as api_views
from django.conf import settings
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    #API
    path('api/v1/', api_views.ApiRoot.as_view(), name=api_views.ApiRoot.name),
    path('api/v1/token/', obtain_auth_token),
    path('api/v1/posts/',api_views.PostList.as_view(), name=api_views.PostList.name),
    path('api/v1/posts/<int:pk>', api_views.PostDetail.as_view(), name=api_views.PostDetail.name),
    path('api/v1/perfil/', api_views.PerfilList.as_view(), name=api_views.PerfilList.name),
    path('api/v1/perfil/<int:pk>', api_views.PerfilDetail.as_view(), name=api_views.PerfilDetail.name),
    path('api/v1/usuarios/', api_views.UserList.as_view(), name=api_views.UserList.name),
    path('api/v1/usuarios/<int:pk>', api_views.UserDetail.as_view(), name=api_views.UserDetail.name),
    path('api/v1/colecoes/', api_views.ColecaoList.as_view(), name=api_views.ColecaoList.name),
    path('api/v1/colecoes/<int:pk>', api_views.ColecaoDetail.as_view(), name=api_views.ColecaoDetail.name),
    path('api/v1/comunidades/', api_views.ComunidadeList.as_view(), name=api_views.ComunidadeList.name),
    path('api/v1/comunidades/<int:pk>', api_views.ComunidadeDetail.as_view(),name=api_views.ComunidadeDetail.name),

    #WEB
    path('admin/', admin.site.urls),
    path('', include('usuario.urls')),
    path('', views.exibir_newsfeed, name='exibir_newsfeed'),
    path('friendship/', include('friendship.urls')),
    path('new-post/', views.AdicionaPostView.as_view() , name = 'add_post'),
    path('delete-post/<string>/<int:post_id>/', views.delete_post, name='delete_post'),
    path('post-detail/<int:post_id>/', views.post_detail , name='post_detail'),
    path('usuario/<int:usuario_id>/', views.exibir_usuario, name='exibir_usuario'),
    path('newsfeed/add/<int:usuario_id>/', views.enviar_pedido, name='enviar_pedido'),
    path('newsfeed/accept/<int:solicitacao_id>/', views.aceitar_pedido, name='aceitar_pedido'),
    path('newsfeed/reject/<int:solicitacao_id>/', views.rejeitar_pedido, name='rejeitar_pedido'),
    path('timeline/', views.exibir_minha_timeline, name='exibir_minha_timeline'),
    path('flash-friends/', views.exibir_flash_friends, name='exibir_flash_friends'),
    path('requests/', views.exibir_friends_requests, name='exibir_friends_requests'),
    path('about/<int:usuario_id>', views.exibir_about, name='exibir_about'),
    path('change-password/', views.alterar_senha, name='change_password'),
    path('change-password/done/', views.change_password, name='alterar_senha'),
    path('desfazer-amizade/<int:usuario_id>/', views.desfazer_amizade, name="desfazer_amizade"),
    path('bloquear/<int:usuario_id>/', views.bloquear_usuario, name="bloquear_usuario"),
    path('desbloquear/<int:usuario_id>/', views.desbloquear_usuario, name="desbloquear_usuario"),
    path('search/',views.buscar_usuario, name='buscar_usuario'),
    path('search/results', views.buscar_usuario, name='buscar_usuario_results'),
    path('settings/',views.exibir_flash_settings, name='exibir_flash_settings'),
    path('settings/super-usuario/<int:usuario_id>',views.definir_super_usuario, name='definir_super_usuario'),
    path('settings/usuario-comum/<int:usuario_id>',views.definir_usuario_comum, name='definir_usuario_comum'),
    path('desativar-perfil/', views.desativar_perfil, name='desativar_perfil'),
    path('settings/posts/usuario/<int:usuario_id>', views.gerenciar_posts, name='gerenciar_posts'),
    path('settings/friends/usuario/<int:usuario_id>', views.gerenciar_flash_friends, name='gerenciar_amigos'),
    path('settings/requests/usuario/<int:usuario_id>', views.gerenciar_friends_requests, name='gerenciar_solicitacoes'),
    path('settings/desativar-perfil/<int:usuario_id>', views.superuser_desativar_perfil, name='superuser_desativar_perfil'),
    path('settings/ativar-perfil/<int:usuario_id>', views.superuser_ativar_perfil, name='superuser_ativar_perfil'),
    path('colecoes', views.exibir_colecoes, name='exibir_colecoes'),
    path('colecao/<int:colecao_id>', views.exibir_colecao, name='exibir_colecao'),
    path('new-post-colecao/<int:colecao_id>', views.add_post_colecao, name='add_post_colecao'),
    path('seguir-colecao/<int:colecao_id>', views.seguir_colecao, name='seguir_colecao'),
    path('deixar-seguir-colecao/<int:colecao_id>', views.deixar_seguir_colecao, name='deixar_seguir_colecao'),
    path('minhas-colecoes', views.exibir_minhas_colecoes, name='exibir_minhas_colecoes'),
    path('new-colecao/', views.add_colecao , name='add_colecao'),
    path('compartilhar-post/<int:post_compartilhado_id>', views.compartilhar_post, name ='compartilhar_post'),
    path('comentar-post/<int:post_comentado_id>', views.ComentaPostView.as_view(), name ='comentar_post'),
    path('comentarios-post/<int:post_comentado_id>', views.exibir_comentarios_post , name='exibir_comentarios_post'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)