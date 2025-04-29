import logging

from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

from django.views.generic import CreateView

from users.forms import LoginUserForm, RegisterUserForm

# Create your views here.
logger = logging.getLogger("users")


class LoginUserView(LoginView):
    form_class = LoginUserForm
    template_name = 'users/login.html'


class RegisterUserView(CreateView):
    form_class = RegisterUserForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')


