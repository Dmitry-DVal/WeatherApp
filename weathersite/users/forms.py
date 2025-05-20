from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control me-2 ' }))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control me-2'}))


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control me-2 '}))
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control me-2'}), label='Password')
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control me-2'}), label='Confirm Password')




