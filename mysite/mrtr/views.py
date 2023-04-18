from .forms import *
from .models import *
from .utils import prorate
from django.shortcuts import render, redirect
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.utils import timezone
from dateutil.relativedelta import relativedelta


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
    return render(request, 'mrtr/temp_forms.html', {'form': form})
    # return render(request, 'mrtr/administrative.html', context)


# TODO Figure out better way to select residents from a list/search
def select_res(request):
    form = SelectResForm()
    if request.method == 'POST':
        sub = SelectResForm(request.POST)
        if sub.is_valid():
            if 'edit' in request.POST:
                return redirect('/edit_res/' + str(request.POST['resident']))
            elif 'discharge' in request.POST:
                return redirect('/discharge_res/' + str(request.POST['resident']))
            elif 'delete' in request.POST:
                res_to_delete = Resident.objects.get(id=request.POST['resident'])
                res_to_delete.delete()
    return render(request, 'mrtr/temp_selects.html', {'form': form})


# Edit resident
# TODO Handle resident balance when admit date is changed
def edit_res(request, id):
    resident = Resident.objects.get(id=id)
    old_rent = resident.rent
    form = ResidentForm(instance=resident)
    if request.method == 'POST':
        sub = ResidentForm(request.POST, instance=resident)
        if sub.is_valid():
            new_rent = int(request.POST['rent'])
            if old_rent != new_rent:
                adj_trans = Transaction(date=sub.cleaned_data['effective_date'],
                                        amount=prorate(new_rent - old_rent, sub.cleaned_data['effective_date']),
                                        type='nra',
                                        resident=resident,
                                        notes='$' + str(old_rent) + ' > $' + str(new_rent) + ' (manual edit)'
                                        )
                adj_trans.save()
            sub.save()
            resident.last_update = timezone.now()
            resident.save()
            return render(request, 'mrtr/temp_forms.html', {'form': form})
        else:
            form = ResidentForm(instance=resident)
    return render(request, 'mrtr/temp_forms.html', {'form': form})


# Discharge resident
def discharge_res(request, id):
    resident = Resident.objects.get(id=id)
    form = DischargeResForm()
    if request.method == 'POST':
        sub = DischargeResForm(request.POST)
        if sub.is_valid():
            resident.discharge_date = sub.cleaned_data['date']
            resident.bed = None
            resident.last_update = timezone.now()
            if len(sub.cleaned_data['reason']) > 0:
                resident.notes = str(resident.notes) + '\nReason Discharged (' + str(sub.cleaned_data['date']) + '): ' + sub.cleaned_data['reason']
            # TODO Figure out if TC wants an option to refund rent
            resident.save()
            return render(request, 'mrtr/temp_forms.html', {'form': form})
    return render(request, 'mrtr/temp_forms.html', {'form': form})


def select_past_res(request):
    form = SelectPastResForm()
    if request.method == 'POST':
        sub = SelectPastResForm(request.POST)
        if sub.is_valid():
            return redirect('/readmit_res/' + str(request.POST['resident']))
    return render(request, 'mrtr/temp_forms.html', {'form': form})


# Readmit resident
def readmit_res(request, id):
    resident = Resident.objects.get(id=id)
    form = ResidentForm(instance=resident)
    if request.method == 'POST':
        sub = ResidentForm(request.POST, instance=resident)
        if sub.is_valid():
            resident.notes = resident.notes + '\n Previous residency: ' + \
                             str(resident.admit_date) + ' to ' + str(resident.discharge_date)
            resident.discharge_date = None
            resident.last_update = timezone.now()
            sub.save()
            resident.save()

            # TODO Figure out how to handle readmission balance
            return render(request, 'mrtr/temp_forms.html', {'form': form})
        else:
            form = ResidentForm(instance=resident)
    return render(request, 'mrtr/temp_forms.html', {'form': form})


def show_res(request):
    table = Resident.objects.all().prefetch_related('bed')
    return render(request, 'mrtr/temp_tables.html', locals())


# New transaction
# TODO Figure out how to make method field appear conditional on if type == 'pmt' (possible workaround - separate form for payments)
def new_trans(request):
    form = TransactionForm()
    if request.method == 'POST':
        sub = TransactionForm(request.POST)
        if sub.is_valid():

            # Make transaction amount negative for transactions that decrease a resident's balance
            decrease = ['pmt', 'bon', 'wrk', 'sos']
            if sub.instance.type in decrease:
                sub.instance.amount *= -1
            sub.save()
    return render(request, 'mrtr/temp_forms.html', {'form': form})


# TODO Figure out better way to select residents from a list/search
def select_trans(request):
    form = SelectTransForm()
    if request.method == 'POST':
        sub = SelectTransForm(request.POST)
        if sub.is_valid():
            if 'edit' in request.POST:
                return redirect('/edit_trans/' + str(request.POST['transaction']))
            elif 'delete' in request.POST:
                trans_to_delete = Transaction.objects.get(id=request.POST['transaction'])
                trans_to_delete.delete()
            elif 'discharge' in request.POST:
                render(request, 'mrtr/temp_selects.html', {'form': form})
    return render(request, 'mrtr/temp_selects.html', {'form': form})


# Edit transaction
def edit_trans(request, id):
    transaction = Transaction.objects.get(id=id)
    form = TransactionForm(instance=transaction)
    if request.method == 'POST':
        old_type = transaction.type
        sub = TransactionForm(request.POST, instance=transaction)
        if sub.is_valid():

            # Make transaction amount negative for transactions that decrease a resident's balance
            # But also keep amount negative if it wasn't changed
            decrease = ['pmt', 'bon', 'wrk', 'sos']
            if old_type not in decrease and sub.instance.type in decrease:
                sub.instance.amount *= -1
            transaction.last_update = timezone.now()
            sub.save()
            return render(request, 'mrtr/temp_forms.html', {'form': form})
        else:
            form = TransactionForm(instance=transaction)
    return render(request, 'mrtr/temp_forms.html', {'form': form})


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
    return render(request, 'mrtr/temp_forms.html', {'form': form})


# House manager forms

# New Drug Test
# TODO Make drug field checkboxes inline with their label; Make other field appear conditional on if result == 'oth'
def new_dtest(request):
    form = DrugTestForm()
    if request.method == 'POST':
        sub = DrugTestForm(request.POST)
        if sub.is_valid():
            sub.save()
    return render(request, 'mrtr/temp_forms.html', {'form': form})
