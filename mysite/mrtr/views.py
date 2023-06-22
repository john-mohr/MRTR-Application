from .forms import *
from .models import *
from .tables import *
from .utils import prorate
from django.shortcuts import render, redirect
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.db.models import Sum
from django.db.models import Value as V
from django.db.models.functions import Concat
from django_tables2 import RequestConfig


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
def username(request):
    username = request.user.first_name +" " + request.user.last_name
    return username


@groups_only('House Manager')
def portal(request):
    page = 'Dashboard'
    fullname = username(request)

    buttons = [('Add Resident', '/portal/new_res'),
               ('Add Rent Payment', '/portal/new_rent_pmt'),
               ('Adjust Balance', '/portal/new_trans')]

    occupied_beds = Resident.objects.all().filter(bed_id__isnull=False).distinct()
    vacant_beds = BedTable(
        Bed.objects.exclude(id__in=occupied_beds.values_list('bed_id', flat=True)),
        order_by='house', orderable=True, exclude=('id', 'occupant'))
    RequestConfig(request).configure(vacant_beds)

    # TODO:
    #  Distinguish between current and past residents
    #  Add a limit to number of residents shown or a threshold balance
    res_balances = ResidentBalanceTable(Resident.objects.annotate(
        balance=Sum('transaction__amount'), full_name=Concat('first_name', V(' '), 'last_name')),
        order_by='-balance')
    RequestConfig(request).configure(res_balances)

    # TODO:
    #  Calculate and display some key metrics (forecasted revenue, occupancy, maintenance costs, etc.)

    return render(request, 'admin/homepage.html', locals())


# New Resident
@groups_only('House Manager')
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
            messages.success(request, 'Form submission successful')
    return render(request, 'admin/forms.html', locals())


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
            messages.success(request, 'Form submission successful')
            return render(request, 'admin/forms.html', {'form': form, 'page': 'Edit Resident Information', 'username': username(request)})
        else:
            form = ResidentForm(instance=resident)
    return render(request, 'admin/forms.html', {'form': form, 'page': 'Edit Resident Information', 'username': username(request)})


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
            messages.success(request, 'Form submission successful')
            return render(request, 'admin/forms.html', {'form': form, 'page': 'Remove Resident', 'fullname': username(request)})
    return render(request, 'admin/forms.html',  {'form': form, 'page': 'Remove Resident', 'fullname': username(request)})


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
            return render(request,'admin/administrative.html', {'form': form})
        else:
            form = ResidentForm(instance=resident)
    return render(request,'admin/administrative.html', {'form': form})


def residents(request):
    table = ResidentsTable(Resident.objects.annotate(balance=Sum('transaction__amount')), order_by='-submission_date', orderable=True, exclude='full_name')
    RequestConfig(request).configure(table)
    button_name = 'Add New Resident'
    button_link = '/portal/new_res'
    page = 'View Residents'
    fullname = str(username(request))

    return render(request, 'admin/temp_tables.html', locals())


def single_res(request, id):
    page = "Current Resident"
    res = Resident.objects.get(id=id)
    name = res.full_name()
    balance = res.balance()

    if res.discharge_date is None:
        buttons = [('Add Rent Payment', '/portal/new_rent_pmt/' + str(id)),
                   ('Adjust Balance', '/portal/new_trans/' + str(id)),
                   ('Discharge', '/portal/discharge_res/' + str(id)),
                   ('Edit info', '/portal/edit_res/' + str(id))]
        bed_name = res.bed.name
        house_name = res.bed.house.name
    else:
        buttons = [('Add Rent Payment', '/portal/new_rent_pmt' + str(id)),
                   ('Adjust Balance', '/portal/new_trans' + str(id)),
                   ('Readmit', '/portal/readmit_res/' + str(id)),
                   ('Edit info', '/portal/edit_res/' + str(id))]
        bed_name = None
        house_name = None

    res_info = list(res.__dict__.items())
    res_info = [(item[0].replace('_', ' '), item[1]) for item in res_info]
    res_info = [(item[0].title(), item[1]) for item in res_info]
    res_info.append(('Bed Name', bed_name))
    res_info.append(('House Name', house_name))

    contact_info = res_info[4:6]
    res_details = [res_info[i] for i in [6, 12, 8, 16, 15, 9, 10, 11]]
    ledger = TransactionTable(Transaction.objects.filter(resident=id).order_by('-date'))

    fullname = username(request)
    return render(request, 'admin/single_res.html', locals())


# New transaction
def new_trans(request, id=None):
    page = 'New Transaction'
    fullname = username(request)
    if id is not None:
        form = TransactionForm(initial={'resident': Resident.objects.get(pk=id)})
        form.fields['resident'].widget = forms.HiddenInput()
    else:
        form = TransactionForm()
    if request.method == 'POST':
        sub = TransactionForm(request.POST)
        if sub.is_valid():
            # Make transaction amount negative for transactions that decrease a resident's balance
            decrease = ['pmt', 'bon', 'wrk', 'sos']
            if sub.instance.type in decrease:
                sub.instance.amount *= -1
            messages.success(request, 'Form submission successful')
            sub.save()
    return render(request, 'admin/forms.html', locals())


def new_rent_pmt(request, id=None):
    page = 'New Rent Payment'
    fullname = username(request)
    if id is not None:
        form = RentPaymentForm(initial={'resident': Resident.objects.get(pk=id)})
        form.fields['resident'].widget = forms.HiddenInput()
    else:
        form = RentPaymentForm()
    if request.method == 'POST':
        sub = RentPaymentForm(request.POST)
        if sub.is_valid():
            sub.instance.amount *= -1
            sub.instance.type = 'pmt'
            sub.save()
    return render(request, 'admin/forms.html', locals())


# Edit transaction
def edit_trans(request, id):
    transaction = Transaction.objects.get(id=id)
    fullname = username(request)
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
            return render(request, 'admin/forms.html', {'form': form})
        else:
            form = TransactionForm(instance=transaction)
    return render(request, 'admin/forms.html', {'form': form})


def new_house(request):
    page = 'Edit House'
    fullname = username(request)

    form = HouseForm()
    if request.method == 'POST':
        sub = HouseForm(request.POST)
        if sub.is_valid():
            sub.save()
            messages.success(request, 'Form submission successful')
    return render(request, 'admin/forms.html', locals())


def edit_house(request, id):
    page = 'Edit House'
    fullname = username(request)

    house = House.objects.get(id=id)
    form = HouseForm(instance=house)
    if request.method == 'POST':
        sub = HouseForm(request.POST, instance=house)
        if sub.is_valid():
            sub.save()
            house.last_update = timezone.now()
            house.save()
            messages.success(request, 'Form submission successful')
            return render(request, 'admin/forms.html', locals())
        else:
            form = HouseForm(instance=house)
    return render(request, 'admin/forms.html', locals())


def houses(request):
    page = 'Houses'
    fullname = username(request)
    table = HouseTable(House.objects.all(), orderable=True)
    RequestConfig(request).configure(table)
    name = 'Houses'
    button_name = 'Add New House'
    button_link = '/portal/new_house'
    return render(request, 'admin/temp_tables.html', locals())


def single_house(request, id):
    page = 'Houses'
    cur_house = House.objects.get(id=id)
    name = cur_house.name
    address = cur_house.address + ' ' + cur_house.city + ', ' + cur_house.state

    buttons = [('Edit info', '/portal/edit_house/' + str(id))]

    house_res = ResidentsTable(Resident.objects.filter(bed__house=id).annotate(balance=Sum('transaction__amount')),
                               exclude=('submission_date', 'house', 'referral_info', 'notes', 'last_update'),
                               orderable=True, order_by='-balance')
    RequestConfig(request).configure(house_res)

    occupied_beds = Resident.objects.all().filter(bed_id__isnull=False).distinct()
    vacant_beds = BedTable(
        Bed.objects.exclude(id__in=occupied_beds.values_list('bed_id', flat=True)).filter(id=id),
        order_by='house', orderable=True, exclude=('occupant', 'house'))
    RequestConfig(request).configure(vacant_beds)

    fullname = username(request)
    return render(request, 'admin/single_house.html', locals())


# # Change House Manager
# # TODO Handle multiple house managers for one house (replace House.manager with a relationship table)
# def change_hm(request):
#     fullname = username(request)
#     form = ChangeHMForm()
#     if request.method == 'POST':
#         sub = ChangeHMForm(request.POST)
#         if sub.is_valid():
#             house_to_edit = sub.cleaned_data['house']
#             old_hm = house_to_edit.manager
#             new_hm = sub.cleaned_data['new_manager']
#             current_datetime = timezone.now()
#             current_date = current_datetime.date()
#
#             # Remove old house manager's rent discount
#             if old_hm is not None:
#                 rm_discount = Transaction(date=current_date,
#                                           amount=prorate((old_hm.rent * 2) - old_hm.rent, current_date),
#                                           type='nra',
#                                           resident=old_hm,
#                                           notes='Change: $' + str(old_hm.rent) + ' > $' + str(old_hm.rent * 2) +
#                                                 '; Reason: removed house manager discount'
#                                           )
#                 rm_discount.save()
#                 old_hm.rent = old_hm.rent * 2
#                 old_hm.save()
#
#             # Give new house manager the rent discount
#             add_discount = Transaction(date=current_date,
#                                        amount=prorate((new_hm.rent / 2) - new_hm.rent, current_date),
#                                        type='nra',
#                                        resident=new_hm,
#                                        notes='Change: $' + str(new_hm.rent) + ' > $' + str(new_hm.rent / 2) +
#                                              '; Reason: house manager discount'
#                                        )
#             add_discount.save()
#             new_hm.rent = new_hm.rent / 2
#             new_hm.save()
#
#             # Assign new house manager
#             house_to_edit.manager = new_hm
#             house_to_edit.last_update = current_datetime
#             house_to_edit.save()
#     return render(request, 'mrtr/forms.html', {'form': form})


def beds(request):
    fullname = username(request)
    page = 'Beds'

    qs = Bed.objects.all().select_related('resident').annotate(full_name=Concat('resident__first_name', V(' '), 'resident__last_name'))

    table = BedTable(qs, exclude=('id',))

    # table = BedTable(Bed.objects.all()
    #                  .select_related('resident')
    #                  .values()
    #                  .annotate(full_name=Concat('resident__first_name', V(' '), 'resident__last_name')),
    #                  exclude=('id',))
    RequestConfig(request).configure(table)

    name = 'Beds'
    button_name = 'Add New Bed'
    button_link = '/portal/#'  # new_house'
    return render(request, 'admin/temp_tables.html', locals())


# House manager forms

# # New Drug Test
# # TODO Make drug field checkboxes inline with their label; Make other field appear conditional on if result == 'oth'
# def new_dtest(request):
#     form = DrugTestForm()
#     if request.method == 'POST':
#         sub = DrugTestForm(request.POST)
#         if sub.is_valid():
#             sub.save()
#     return render(request, 'mrtr/forms.html', {'form': form})
#
#
# # New Check-in
# # TODO Restrict residents to residents in the manager's house
# def new_check_in(request):
#     form = CheckInForm()
#     if request.method == 'POST':
#         sub = CheckInForm(request.POST)
#         if sub.is_valid():
#             sub.save()
#     return render(request, 'mrtr/forms.html', {'form': form})

# House Manager forms
@groups_only('House Manager')
def house_manager(request):
    context = {
        'page': 'Dashboard',
        'fullname': username(request),
    }
    return render(request, 'house/house_generic.html',context)