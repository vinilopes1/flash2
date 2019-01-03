from django.contrib import admin

# Register your models here.
from .models import Perfil, Comentario, Post, Categoria, Colecao, Comunidade

admin.site.register(Perfil)
admin.site.register(Post)
admin.site.register(Comentario)
admin.site.register(Categoria)
admin.site.register(Colecao)
admin.site.register(Comunidade)