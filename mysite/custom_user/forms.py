
from django import forms
from .models import User

from django.contrib.auth.forms import UserCreationForm
 

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(label= 'First Name', max_length = 20)
    last_name = forms.CharField(label= 'Last Name', max_length = 20)
    class Meta:
        model = User
        fields = ['email', 'password1', 'password2','first_name','last_name']