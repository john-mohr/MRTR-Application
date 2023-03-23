
from django import forms
from .models import User

from django.contrib.auth.forms import UserCreationForm
 

class UserRegisterForm(UserCreationForm):
    myfield = forms.CharField(widget=forms.TextInput(attrs={'class': 'myfieldclass'}))
    email = forms.EmailField()
    first_name = forms.CharField(label= 'First Name', max_length = 20)
    last_name = forms.CharField(label= 'Last Name', max_length = 20)
    class Meta:
        model = User
        fields = ['email', 'password1', 'password2','first_name','last_name']


class ContactForm(forms.Form):
    email = forms.EmailField()
    first_name = forms.CharField(label= 'First Name', max_length = 20)
    last_name = forms.CharField(label= 'Last Name', max_length = 20)
    message = message = forms.CharField(widget = forms.Textarea, max_length = 2000)