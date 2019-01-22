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
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('usuario.urls')),
    path('', views.exibir_newsfeed, name='exibir_newsfeed'),
    path('friendship/', include('friendship.urls')),
    path('new-post/', views.AdicionaPostView.as_view() , name = 'add_post'),
    path('delete-post/<string>/<int:post_id>/', views.delete_post, name='delete_post'),
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

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)