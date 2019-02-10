from django.db import models
from django.contrib.auth.models import User
from friendship.models import Friend


class Base(models.Model):

    criado_em = models.DateTimeField('Criado em', auto_now_add=True, blank=False, null=False)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        abstract = True

    def get_criado_em(self, format):
        return self.criado_em.__format__(format).__str__()

    def get_atualizado_em(self, format):
        return self.atualizado_em.__format__(format).__str__()


class Perfil(Base):

    SEXO_CHOICES = (
        ('M', 'Masculino'),
        ('F', 'Feminino'),
        ('O', 'Outros'),
    )

    sexo = models.CharField('Sexo', max_length=16, choices=SEXO_CHOICES, blank=False, null=False)
    telefone = models.CharField('Telefone', max_length=16, blank=False, null=False)
    data_nasc = models.DateField('Data de Nascimento', blank=False, null=False)
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    foto_perfil = models.ImageField('Foto', upload_to='imagens/%Y/',default='default_foto.png',null=True,blank=True)
    capa = models.ImageField('Capa', upload_to='imagens/%Y/',default='default_capa.jpg',null=True,blank=True)


    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'

    def __str__(self):
        return "%s %s" % (self.nome(), self.sobrenome())

    def qtd_amigos(self):
        qtd_amigos = Friend.objects.friends(self.usuario)
        return qtd_amigos.__len__()

    def nome(self):
        return self.usuario.first_name

    def sobrenome(self):
        return self.usuario.last_name


class Post(Base):

    descricao =  models.CharField('Descrição', max_length=1000, blank=True, null=True)
    foto = models.ImageField('Foto', upload_to='arquivos/%Y/posts/', null=True,blank=True)
    video = models.FileField('Vídeo', upload_to='arquivos/%Y/posts/', null=True, blank=True)
    aplausos = models.IntegerField('Aplausos', default=0, blank=False, null=False)
    editado = models.BooleanField('Editado', default=False, blank=False, null=False)
    compartilhado = models.BooleanField('Compartilhado', default=False, blank=False, null=False)
    usuario = models.ForeignKey(Perfil, default=None, null=True, blank=True, on_delete=models.CASCADE, related_name='posts')
    colecao = models.ForeignKey('Colecao', null=True, blank=True, on_delete=models.CASCADE, related_name='posts')
    comunidade = models.ForeignKey('Comunidade', null=True, blank=True, on_delete=models.CASCADE, related_name='comunidades')

    def get_id(self):
        return self.id

    def __str__(self):
        return self.descricao

    class Meta:
        ordering = ('criado_em',)


class Comentario(Base):

    descricao = models.CharField('Descricao', max_length=256, blank=False, null=False)
    usuario = models.ForeignKey(Perfil, null=False, blank=False, on_delete=models.CASCADE, related_name='meus_comentarios')
    editado = models.BooleanField('Editado', default=False, null=False, blank=False)
    post = models.ForeignKey(Post, blank=False, null=False, on_delete = models.CASCADE, related_name = 'comentarios')

    class Meta:
        verbose_name = 'Comentário'
        verbose_name_plural = 'Comentários'

    def __str__(self):
        return self.descricao


class Categoria(Base):

    titulo = models.CharField('Título', max_length=255, null=False, blank=False)
    descricao = models.CharField('Descrição', max_length=255, null=False, blank=False)

    def __str__(self):
        return '%s' % (self.titulo)


class Colecao(Base):

    titulo = models.CharField('Título', max_length=255, null=False, blank=False)
    descricao = models. CharField('Descrição', max_length=255, null=False, blank=False)
    autor = models.ForeignKey(Perfil, null=False, blank=False, on_delete=models.CASCADE, related_name='minhas_colecoes')
    foto_perfil = models.ImageField('Foto', upload_to='imagens/%Y/',default='default_foto.png',null=True,blank=True)
    capa = models.ImageField('Capa', upload_to='imagens/%Y/',default='default_capa.jpg',null=True,blank=True)
    seguidores = models.ManyToManyField(Perfil, related_name='seguidores')

    def nome_autor(self):
        usuario = User.objects.get(pk=self.autor.id)
        return usuario.username

    def __str__(self):
        return self.titulo


class Comunidade(Base):

    titulo = models.CharField('Título', max_length=255, null=False, blank=False)
    descricao = models.CharField('Descrição', max_length=255, null=False, blank=False)
    autor = models.ForeignKey(Perfil, null=False, blank=False, on_delete=models.CASCADE, related_name='minhas_comunidades')
    membros = models.ManyToManyField(Perfil, related_name='membros')
    administradores = models.ManyToManyField(Perfil, related_name='administradores')
    regras = models.CharField('Regras', max_length=10000, null=True, blank=True)



