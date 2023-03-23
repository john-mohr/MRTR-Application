from django import forms

from django.contrib.auth.forms import UserCreationForm
 

class ContactForm(forms.Form):
    email = forms.EmailField()
    first_name = forms.CharField(label= 'First Name', max_length = 20)
    last_name = forms.CharField(label= 'Last Name', max_length = 20)
    message = message = forms.CharField(widget = forms.Textarea, max_length = 2000)