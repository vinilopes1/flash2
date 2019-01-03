from django import forms

from .models import Post

class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = "__all__"
        widgets = {
            'birth_date': forms.DateInput(
                attrs={
                    'type': 'date',
                }
            )
        }