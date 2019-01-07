from django import forms

from .models import Post

class PostForm(forms.Form):

    descricao = forms.CharField(required=True)

class CriarPerfilForm(forms.Form):

    username = forms.CharField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    password = forms.CharField(required=True)
    email = forms.EmailField(required=True)

