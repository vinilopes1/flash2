from rest_framework import serializers
from django.contrib.auth.models import User
from comum.models import Perfil,Post,Colecao,Comunidade


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'id', 'username', 'password', 'first_name', 'last_name')


class PerfilSerializer(serializers.ModelSerializer):
    usuario = UserSerializer()
    class Meta:
        model = Perfil
        fields = (
            'url',
            'id',
            'foto_perfil',
            'capa',
            'usuario',
            'qtd_amigos'
        )

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            'url',
            'id',
            'descricao',
            'usuario',
            'colecao',
        )

class ColecaoSerializer(serializers.ModelSerializer):
    foto_perfil = serializers.CharField()
    capa = serializers.CharField()
    posts = PostSerializer(many=True,read_only=True)
    seguidores = PerfilSerializer(many=True,read_only=True)
    class Meta:
        model = Colecao
        fields = (
            'url',
            'id',
            'titulo',
            'nome_autor',
            'autor',
            'foto_perfil',
            'capa',
            'posts',
            'seguidores',
        )
    extra_kwargs = {'nome_autor':{'write_only': False}}


class ComunidadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comunidade
        fields = (
            'url',
            'id',
            'titulo',
            'autor',
        )