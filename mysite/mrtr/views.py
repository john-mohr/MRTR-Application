from .forms import *
from .models import *
from .utils import prorate
from django.shortcuts import render, redirect
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.utils import timezone
from dateutil.relativedelta import relativedelta
# from datetime import datetime
# from dateutil.utils import today


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


# Admin forms

# New Resident
# TODO Figure out how to handle multiple forms (not sure if this will work, might have to create new URLs)
# @groups_only('House Manager')
def new_res(request):
    form = ResidentForm()
    if request.method == 'POST':
        sub = ResidentForm(request.POST)
        if sub.is_valid():
            sub.save()

            # Add beginning balance transactions
            intake = Transaction(date=sub.instance.admit_date,
                                 amount=75,
                                 type='fee',
                                 resident=sub.instance,
                                 notes='Intake Fee',
                                 submission_date=sub.instance.submission_date
                                 )
            intake.save()
            first_mo = Transaction(date=sub.instance.admit_date,
                                   amount=prorate(sub.instance.rent, sub.instance.admit_date),
                                   type='rnt',
                                   resident=sub.instance,
                                   notes=sub.instance.admit_date.strftime('%B') + ' (partial)',
                                   submission_date=sub.instance.submission_date
                                   )
            first_mo.save()
            second_mo = Transaction(date=sub.instance.admit_date,
                                    amount=sub.instance.rent,
                                    type='rnt',
                                    resident=sub.instance,
                                    notes=(sub.instance.admit_date + relativedelta(months=1)).strftime('%B'),
                                    submission_date=sub.instance.submission_date
                                    )
            second_mo.save()
    return render(request, 'mrtr/form_test.html', {'form': form})
    # return render(request, 'mrtr/administrative.html', context)


# TODO Figure out better way to select residents from a list/search
def select_res(request):
    form = SelectResForm()
    if request.method == 'POST':
        sub = SelectResForm(request.POST)
        if sub.is_valid():
            return redirect('/edit_res/' + str(request.POST['resident']))
    return render(request, 'mrtr/form_test.html', {'form': form})


# Edit resident
# TODO Handle resident balance when admit date is changed
def edit_res(request, id):
    resident = Resident.objects.get(id=id)
    form = ResidentForm(instance=resident)
    if request.method == 'POST':
        sub = ResidentForm(request.POST, instance=resident)
        if sub.is_valid():
            sub.save()
            resident.last_update = timezone.now()
            resident.save()
            return render(request, 'mrtr/form_test.html', {'form': form})
        else:
            form = ResidentForm(instance=resident)
    return render(request, 'mrtr/form_test.html', {'form': form})


# New transaction
# TODO Figure out how to make method field appear conditional on if type == 'pmt' (possible workaround - separate form for payments)
def new_trans(request):
    form = NewTransactionForm()
    if request.method == 'POST':
        sub = NewTransactionForm(request.POST)
        if sub.is_valid():

            # Make transaction amount negative for transactions that decrease a resident's balance
            decrease = ['pmt', 'bon', 'wrk', 'sos']
            if sub.instance.type in decrease:
                sub.instance.amount *= -1
            sub.save()
    return render(request, 'mrtr/form_test.html', {'form': form})


# Rent change
def change_rent(request):
    form = RentChangeForm()
    if request.method == 'POST':
        sub = RentChangeForm(request.POST)
        if sub.is_valid():
            res_to_edit = sub.cleaned_data['resident']

            # Create adjustment transaction for new rent amount
            adj_trans = Transaction(date=sub.cleaned_data['effective_date'],
                                    amount=prorate(sub.cleaned_data['new_rent'] - res_to_edit.rent,
                                                   sub.cleaned_data['effective_date']),
                                    type='nra',
                                    resident=res_to_edit,
                                    notes='Change: $' +
                                          str(res_to_edit.rent) + ' > $' + str(sub.cleaned_data['new_rent']) +
                                          '; Reason: ' + str(sub.cleaned_data['reason'])
                                    )
            adj_trans.save()
            res_to_edit.rent = sub.cleaned_data['new_rent']
            res_to_edit.last_update = timezone.now()
            res_to_edit.save()
    return render(request, 'mrtr/form_test.html', {'form': form})


# Change House Manager
# TODO Handle multiple house managers for one house (replace House.manager with a relationship table)
def change_hm(request):
    form = ChangeHMForm()
    if request.method == 'POST':
        sub = ChangeHMForm(request.POST)
        if sub.is_valid():
            house_to_edit = sub.cleaned_data['house']
            old_hm = house_to_edit.manager
            new_hm = sub.cleaned_data['new_manager']
            current_datetime = timezone.now()
            current_date = current_datetime.date()

            # Remove old house manager's rent discount
            if old_hm is not None:
                rm_discount = Transaction(date=current_date,
                                          amount=prorate((old_hm.rent * 2) - old_hm.rent, current_date),
                                          type='nra',
                                          resident=old_hm,
                                          notes='Change: $' + str(old_hm.rent) + ' > $' + str(old_hm.rent * 2) +
                                                '; Reason: removed house manager discount'
                                          )
                rm_discount.save()
                old_hm.rent = old_hm.rent * 2
                old_hm.save()

            # Give new house manager the rent discount
            add_discount = Transaction(date=current_date,
                                       amount=prorate((new_hm.rent / 2) - new_hm.rent, current_date),
                                       type='nra',
                                       resident=new_hm,
                                       notes='Change: $' + str(new_hm.rent) + ' > $' + str(new_hm.rent / 2) +
                                             '; Reason: house manager discount'
                                       )
            add_discount.save()
            new_hm.rent = new_hm.rent / 2
            new_hm.save()

            # Assign new house manager
            house_to_edit.manager = new_hm
            house_to_edit.last_update = current_datetime
            house_to_edit.save()
    return render(request, 'mrtr/form_test.html', {'form': form})


# House manager forms

# New Drug Test
# TODO Make drug field checkboxes inline with their label; Make other field appear conditional on if result == 'oth'
def new_dtest(request):
    form = DrugTestForm()
    if request.method == 'POST':
        sub = DrugTestForm(request.POST)
        if sub.is_valid():
            sub.save()
    return render(request, 'mrtr/form_test.html', {'form': form})
