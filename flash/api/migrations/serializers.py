from rest_framework import serializers
from django.contrib.auth.models import User
from comum.models import Perfil,Post,Colecao,Comunidade


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'id', 'username', 'password', 'first_name', 'last_name')


class PerfilSerializer(serializers.HyperlinkedModelSerializer):
    usuario = UserSerializer()
    class Meta:
        model = Perfil
        fields = (
            'url',
            'id',
            'foto_perfil',
            'capa',
            'usuario',
        )

class PostSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Post
        fields = (
            'url',
            'id',
            'descricao',
            'usuario',
            'colecao',
        )

class ColecaoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Colecao
        fields = (
            'url',
            'id',
            'titulo',
            'autor',
            'posts',
        )


class ComunidadeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Comunidade
        fields = (
            'url',
            'id',
            'titulo',
            'autor',
        )
