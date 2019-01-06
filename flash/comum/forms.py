from django import forms

from .models import Post

class PostForm(forms.Form):

    descricao = forms.CharField(required=True)