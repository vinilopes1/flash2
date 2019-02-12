from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import generics
from comum.models import Post,Perfil,Comunidade,Colecao
from .serializers import *
from .permissions import IsFriend
from rest_framework import authentication,permissions
from friendship.models import FriendshipRequest

class DefaultMixin(object):

    authentication_classes = (
        authentication.BasicAuthentication,
        authentication.TokenAuthentication,
    )

    permission_classes = (
       permissions.IsAuthenticated,
    )



class ApiRoot(generics.GenericAPIView):
    name = 'api-root'
    def get(self, request, *args, **kwargs):
        return Response({
            'posts': reverse(PostList.name,
                            request=request),
            'perfil': reverse(PerfilList.name,
                             request=request),
            'usuarios': reverse(UserList.name,
                             request=request),
            'comunidades': reverse(ComunidadeList.name,
                                request=request),
            'colecoes': reverse(ColecaoList.name,
                                request=request),
            'friendship_requests': reverse(FriendshipRequestList.name,
                                request=request)
        })

class PostList(DefaultMixin, generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    name = 'post-list'

class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    name = 'post-detail'

class PerfilList(generics.ListCreateAPIView):
    queryset = Perfil.objects.all()
    serializer_class = PerfilSerializer
    name = 'perfil-list'

class PerfilDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Perfil.objects.all()
    serializer_class = PerfilSerializer
    name = 'perfil-detail'

class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    name = 'user-list'

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    name = 'user-detail'

class ComunidadeList(generics.ListCreateAPIView):
    queryset = Comunidade.objects.all()
    serializer_class = ComunidadeSerializer
    name = 'comunidade-list'

class ComunidadeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comunidade.objects.all()
    serializer_class = ComunidadeSerializer
    name = 'comunidade-detail'

class ColecaoList(generics.ListCreateAPIView):
    queryset = Colecao.objects.all()
    serializer_class = ColecaoSerializer
    name = 'colecao-list'

class ColecaoDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Colecao.objects.all()
    serializer_class = ColecaoSerializer
    name = 'colecao-detail'

class FriendshipRequestList(generics.ListCreateAPIView):
    queryset = FriendshipRequest.objects.all()
    serializer_class = FriendshipRequestSerializer
    name = 'friendship-request-list'

class FriendshipRequestDetail(DefaultMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = FriendshipRequest.objects.all()
    serializer_class = FriendshipRequestSerializer
    name = 'friendship-request-detail'
    #
    # authentication_classes = (
    #     authentication.TokenAuthentication,
    # )
    #
    # permission_classes = (
    #     IsFriend,
    # )
    #

