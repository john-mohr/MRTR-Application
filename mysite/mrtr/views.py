from django.shortcuts import render
from .models import exampleUser

# Create your views here.


def home(request):
    
    return render(request, '.html')

def locations(request):
    
    return render(request, '.html')

def about(request):
    
    return render(request, '.html')

def payment(request):
    
    return render(request, '.html')

def contact(request):
    
    return render(request, '.html')