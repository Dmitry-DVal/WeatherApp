import logging

from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView

from users.forms import LoginUserForm, RegisterUserForm
from users.utils import RedirectAuthenticatedUserMixin

# Create your views here.
logger = logging.getLogger("users")


class LoginUserView(RedirectAuthenticatedUserMixin, LoginView):
    form_class = LoginUserForm
    template_name = 'users/login.html'

class RegisterUserView(RedirectAuthenticatedUserMixin, CreateView):
    form_class = RegisterUserForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response
