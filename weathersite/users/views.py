import logging

from django.contrib.auth import authenticate
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import CreateView

from users.forms import LoginUserForm, RegisterUserForm

# Create your views here.
logger = logging.getLogger("users")


# def login(request):
#     logger.debug("Запрос страницы авторизации: %s", request.method)
#     return render(request, "users/login.html")




class LoginUserView(LoginView):
    form_class = LoginUserForm
    template_name = 'users/login.html'


class RegisterUserView(CreateView):
    form_class = RegisterUserForm
    template_name = 'users/register.html'


# def register(request):
#     logger.debug("Запрос страницы регистрации %s", request.path)
#     return render(request, "users/register.html")
