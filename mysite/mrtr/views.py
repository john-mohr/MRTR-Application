from dateutil.utils import today
from django.shortcuts import render, redirect
from .forms import *
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from datetime import datetime
from .models import *

# Create your views here.

from functools import wraps

def groups_only(*groups):
    def inner(view_func):
        @wraps(view_func)
        def wrapper_func(request, *args, **kwargs):
            if request.user.groups.filter(name__in=groups).exists() or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            else:
                return redirect('/accounts/logout')
        return wrapper_func
    return inner

def home(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = "Website Inquiry"
            body = {
                'first_name': form.cleaned_data['first_name'],
                'last_name': form.cleaned_data['last_name'],
                'email': form.cleaned_data['email'],
                'message': form.cleaned_data['message'],
            }
            message = "\n".join(body.values())

            try:
                send_mail(subject, message, 'deanpham1200@gmail.com', ['deanpham1200@gmail.com'])
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect('/')

    form = ContactForm()
    return render(request, 'mrtr/index.html', {'form': form})

def locations(request):

    return render(request, 'mrtr/ourlocations.html')

def sobriety_support(request):

    return render(request, 'mrtr/sobriety_support.html')

def about(request):

    return render(request, 'mrtr/about_us.html')

def payment(request):

    return render(request, 'mrtr/payment_options.html')

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = "Website Inquiry"
            body = {
                'first_name': form.cleaned_data['first_name'],
                'last_name': form.cleaned_data['last_name'],
                'email': form.cleaned_data['email'],
                'message': form.cleaned_data['message'],
            }
            message = "\n".join(body.values())

            try:
                send_mail(subject, message, 'deanpham1200@gmail.com', ['deanpham1200@gmail.com'])
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect('/')

    form = ContactForm()
    return render(request, 'mrtr/contact_us.html', {'form': form})


# TODO build if/else train to find the correct form (not sure if this will work, might have to create new URLs)
@groups_only('House Manager')
def portal(request):
    form = NewResidentForm()
    context = {'form': form}

    if request.method == 'POST':
        # print(request.POST)
        new_res = NewResidentForm(request.POST)
        if new_res.is_valid():
            # print('valid')
            new_res.instance.submission_date = datetime.now()
            new_res.save()
            print(type(new_res))
            # TODO add beginning balance transactions

    return render(request, 'mrtr/administrative.html', context)






