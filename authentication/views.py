from django.shortcuts import render
from django.http import HttpResponse
from .utils import password_is_valid, username_is_valid, email_is_valid, email_html
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.messages import constants
from django.contrib import messages
from django.contrib import auth
import os
from django.conf import settings
from .models import Ativacao
from hashlib import sha256

def cadastro(request):
    if request.method == "GET":

        if request.user.is_authenticated:
            return redirect ('/')
        return render(request, 'cadastro.html')
    
    elif request.method == "POST":

        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        confirm_password = request.POST.get('confirm_password')

        if not password_is_valid(request, password, confirm_password):
            return redirect('/auth/cadastro')
        
        if not username_is_valid(request, username):
            return redirect('/auth;cadastro')
        
        if not email_is_valid(request, email):
            return redirect('/auth;cadastro')
        
        try:
            user = User.objects.create_user(username=username, password=password, is_active=False)
            user.save() 

            token = sha256(f"{username}{email}".encode() ).hexdigest()
            ativacao = Ativacao(token=token, user=user)
            ativacao.save()

            path_template = os.path.join(settings.BASE_DIR, 'authentication/templates/emails/cadastro_confirmado.html')
            email_html(path_template, 'Cadastro confirmado', [email,], username=username, link_ativacao=f"127.0.0.1:8000/auth/ativar_conta/{token}")
            messages.add_message(request, constants.SUCCESS, 'Usuario cadastrado com sucesso')
            return redirect('/auth/logar')
        
        except IntegrityError:
            return messages.add_message(request, constants.ERROR, ("Erro: Nome de usuário já existe."))
        
        except Exception as e:
            return HttpResponse(f"Ocorreu um erro no cadastro: {str(e)}")


def logar(request):

    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect ('/')
        return render (request, 'logar.html')

    elif request.method == "POST":
        username = request.POST.get ('usuario')
        senha = request.POST.get('senha')
        usuario = auth.authenticate(username=username, password=senha)

        if not usuario:
            messages.add_message(request, constants.ERROR, 'username ou senha invalidos')
            return redirect('/auth/logar')
        else:
            auth.login(request, usuario)
            return redirect ('/')
        

    
    
def sair(request):
    auth.logout(request)
    return redirect('/auth/logar')

def ativar_conta(request, token):
    token = get_object_or_404(Ativacao, token=token)
    if token.ativo:
        messages.add_message(request, constants.WARNING, 'Essa token já foi usado')
        return redirect('/auth/logar')
    user = User.objects.get(username=token.user.username)
    user.is_active = True
    user.save()
    token.ativo = True
    token.save()
    messages.add_message(request, constants.SUCCESS, 'Conta ativa com sucesso')
    return redirect('/auth/logar')
        

        