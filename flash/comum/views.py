from django.shortcuts import render, redirect
from .forms import PostForm
from django.utils import timezone

# Create your views here.

def exibir_newsfeed(request):
    return render(request, "newsfeed.html")


def index(request):

    form = PostForm()
    return render(request, 'index.html',{'form':form})

def novo_post(request):

    if request.method == "POST":
        print('Post')
        form = PostForm(request.POST)
        if form.is_valid():
            print('Valido')
            post = form.save(commit=False)
            post.usuario = request.user
            post.criado_em = timezone.now()
            post.save()
            return redirect('index.html')
    else:
        form = PostForm()

    return render(request, 'edit_post.html', {'form':form})