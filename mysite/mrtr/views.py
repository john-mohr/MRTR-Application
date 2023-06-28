# TODO
#  Add tables for drug tests and check ins to house and resident pages
#  Add proper redirects to each view (see new_trans and new_rent_pmt)

from .forms import *
from .models import *
from .tables import *
from .utils import prorate
from django.shortcuts import render, redirect
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect
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
        order_by='house', orderable=True, exclude=('id', 'occupant', 'full_name'))
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
    page = "Add New Resident"
    if request.method == 'POST':
        sub = ResidentForm(request.POST)
        if sub.is_valid():
            sub.save()

            # Add beginning balance transactions
            intake = Transaction(date=sub.instance.admit_date,
                                 amount=75,
                                 type='Fee',
                                 resident=sub.instance,
                                 notes='Intake Fee',
                                 submission_date=sub.instance.submission_date
                                 )
            intake.save()
            first_mo = Transaction(date=sub.instance.admit_date,
                                   amount=prorate(sub.instance.rent, sub.instance.admit_date),
                                   type='Rent charge',
                                   resident=sub.instance,
                                   notes=sub.instance.admit_date.strftime('%B') + ' (partial)',
                                   submission_date=sub.instance.submission_date
                                   )
            first_mo.save()
            second_mo = Transaction(date=sub.instance.admit_date,
                                    amount=sub.instance.rent,
                                    type='Rent charge',
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
                                        type='Rent adjustment',
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
            return render(request, 'admin/forms.html', locals())
        else:
            form = ResidentForm(instance=resident)
    return render(request, 'admin/forms.html', locals())


def residents(request):
    page = 'View All Residents'
    table = ResidentsTable(Resident.objects.annotate(balance=Sum('transaction__amount')), order_by='-submission_date', orderable=True, exclude='full_name')
    RequestConfig(request).configure(table)
    button_name = 'Add New Resident'
    button_link = '/portal/new_res'
    fullname = str(username(request))

    return render(request, 'admin/temp_tables.html', locals())


def single_res(request, id):
    page = "Resident"
    res = Resident.objects.get(id=id)
    name = res.full_name()
    balance = res.balance()

    if res.discharge_date is None:
        status = 'Current'
        buttons = [('Add Rent Payment', '/portal/new_rent_pmt/' + str(id)),
                   ('Adjust Balance', '/portal/new_trans/' + str(id)),
                   ('Discharge', '/portal/discharge_res/' + str(id)),
                   ('Edit info', '/portal/edit_res/' + str(id))]
        bed_name = res.bed.name
        house_name = res.bed.house.name
    else:
        status = 'Past'
        buttons = [('Add Rent Payment', '/portal/new_rent_pmt/' + str(id)),
                   ('Adjust Balance', '/portal/new_trans/' + str(id)),
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
    ledger = TransactionTable(Transaction.objects.filter(resident=id).order_by('-submission_date'),
                              exclude=('submission_date', 'full_name', 'last_update'))

    fullname = username(request)
    return render(request, 'admin/single_res.html', locals())


# New transaction
def new_trans(request, res_id=None):
    page = 'New Transaction'
    fullname = username(request)

    if res_id is not None:
        form = TransactionForm(initial={'resident': Resident.objects.get(pk=res_id)})
        form.fields['resident'].widget = forms.HiddenInput()
    else:
        form = TransactionForm()

    if request.method == 'POST':
        sub = TransactionForm(request.POST)
        if sub.is_valid():
            # Make transaction amount negative for transactions that decrease a resident's balance
            decrease = ['Rent payment', 'Bonus', 'Work/reimbursement', 'Sober support']
            if sub.instance.type in decrease:
                sub.instance.amount *= -1
            messages.success(request, 'Form submission successful')
            sub.save()
            if res_id is not None:
                return redirect('/portal/resident/' + str(res_id))
            else:
                return redirect('/portal')
    return render(request, 'admin/forms.html', locals())


def new_rent_pmt(request, res_id=None):
    page = 'New Rent Payment'
    fullname = username(request)

    if res_id is not None:
        form = RentPaymentForm(initial={'resident': Resident.objects.get(pk=res_id)})
        form.fields['resident'].widget = forms.HiddenInput()
    else:
        form = RentPaymentForm()

    if request.method == 'POST':
        sub = RentPaymentForm(request.POST)
        if sub.is_valid():
            sub.instance.amount *= -1
            sub.instance.type = 'Rent payment'
            sub.save()
            if res_id is not None:
                return redirect('/portal/resident/' + str(res_id))
            else:
                return redirect('/portal')
    return render(request, 'admin/forms.html', locals())


# Edit transaction
def edit_trans(request, id):
    trans = Transaction.objects.get(id=id)
    fullname = username(request)
    form = TransactionForm(instance=trans)
    if request.method == 'POST':
        old_type = trans.type
        sub = TransactionForm(request.POST, instance=trans)
        if sub.is_valid():

            # Make transaction amount negative for transactions that decrease a resident's balance
            # But also keep amount negative if it wasn't changed
            decrease = ['Rent payment', 'Bonus', 'Work/reimbursement', 'Sober support']
            if old_type not in decrease and sub.instance.type in decrease:
                sub.instance.amount *= -1
            trans.last_update = timezone.now()
            sub.save()
            return render(request, 'admin/forms.html', {'form': form})
        else:
            form = TransactionForm(instance=trans)
    return render(request, 'admin/forms.html', {'form': form})


def transactions(request):
    page = 'View All Transactions'
    table = TransactionTable(Transaction.objects.all()
                             .select_related('resident')
                             .annotate(full_name=Concat('resident__first_name', V(' '), 'resident__last_name')),
                             ) # , order_by='-submission_date',
                           # orderable=True, exclude='full_name')
    RequestConfig(request).configure(table)
    button_name = 'Add New Transaction'
    button_link = '/portal/new_trans'
    fullname = str(username(request))

    return render(request, 'admin/temp_tables.html', locals())


def transaction(request, id):
    page = "Transaction"
    trans = Transaction.objects.get(id=id)
    # name = res.full_name()
    # balance = res.balance()

    # if res.discharge_date is None:
    #     buttons = [('Add Rent Payment', '/portal/new_rent_pmt/' + str(id)),
    #                ('Adjust Balance', '/portal/new_trans/' + str(id)),
    #                ('Discharge', '/portal/discharge_res/' + str(id)),
    #                ('Edit info', '/portal/edit_res/' + str(id))]
    #     bed_name = res.bed.name
    #     house_name = res.bed.house.name
    # else:
    #     buttons = [('Add Rent Payment', '/portal/new_rent_pmt/' + str(id)),
    #                ('Adjust Balance', '/portal/new_trans/' + str(id)),
    #                ('Readmit', '/portal/readmit_res/' + str(id)),
    #                ('Edit info', '/portal/edit_res/' + str(id))]
    #     bed_name = None
    #     house_name = None

    buttons = [('Edit', '/portal/edit_trans/' + str(id))]

    trans_info = list(trans.__dict__.items())
    trans_info = [(item[0].replace('_', ' '), item[1]) for item in trans_info]
    trans_info = [(item[0].title(), item[1]) for item in trans_info]

    # print(trans_info)
    trans_details = trans_info[2:]
    # ledger = TransactionTable(Transaction.objects.filter(resident=id).order_by('-date'),
    #                           exclude=('submission_date', 'full_name', 'last_update'))

    fullname = username(request)
    return render(request, 'admin/single_trans.html', locals())


# New Meeting
def new_meeting(request):
    page = 'Add New Meeting'
    fullname = username(request)

    form = ManagerMeetingForm()
    if request.method == 'POST':
        sub = ManagerMeetingForm(request.POST)
        if sub.is_valid():
            sub.save()
            messages.success(request, 'Form submission successful')
    return render(request, 'admin/forms.html', locals())


def edit_meeting(request, id):
    page = 'Edit Meeting'
    fullname = username(request)

    meeting = Manager_meeting.objects.get(id=id)
    form = ManagerMeetingForm(instance=meeting)
    if request.method == 'POST':
        sub = ManagerMeetingForm(request.POST, instance=meeting)
        if sub.is_valid():
            sub.save()
            meeting.last_update = timezone.now()
            meeting.save()
            messages.success(request, 'Form submission successful')
            return render(request, 'admin/forms.html', locals())
        else:
            form = ManagerMeetingForm(instance=meeting)
    return render(request, 'admin/forms.html', locals())

def meetings(request):
    page = 'All Meetings'
    fullname = username(request)
    latest_meeting = Manager_meeting.objects.latest('submission_date')
    table = ManagerMeetingTable(Manager_meeting.objects.all(), orderable=True)
    RequestConfig(request).configure(table)
    name = 'Meetings'
    button_name = 'Add New Meeting'
    button_link = '/portal/new_meeting'
    return render(request, 'admin/meetings.html', locals())

def single_meeting(request, id):
    page = 'Individual Meeting'
    fullname = username(request)
    meeting = Manager_meeting.objects.get(id=id)
    buttons = [('Edit info', '/portal/edit_meeting/' + str(id))]
    return render(request, 'admin/single_meeting.html', locals())

# New House
def new_house(request):
    page = 'Add New House'
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
    page = 'View All Houses'
    fullname = username(request)
    table = HouseTable(House.objects.all()
                       .select_related('manager')
                       .annotate(full_name=Concat('manager__first_name', V(' '), 'manager__last_name')),
                       orderable=True)

    # table = BedTable(Bed.objects.all()
    #                  .select_related('resident')
    #                  .values()
    #                  .annotate(full_name=Concat('resident__first_name', V(' '), 'resident__last_name')),
    #                  exclude=('id',))

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


def beds(request):
    page = 'View All Beds'
    fullname = username(request)
    table = BedTable(Bed.objects.all()
                     .select_related('resident')
                     .annotate(full_name=Concat('resident__first_name', V(' '), 'resident__last_name')),
                     exclude=('id',))
    RequestConfig(request).configure(table)

    name = 'Beds'
    button_name = 'Add New Bed'
    button_link = '/portal/beds#'  # new_house'
    return render(request, 'admin/temp_tables.html', locals())


# New Supply Request
def new_supply_request(request):
    page = 'Add New Supply Request'
    fullname = username(request)
    form = SupplyRequestForm()
    if request.method == 'POST':
        sub = SupplyRequestForm(request.POST)
        if sub.is_valid():
            sub.save()
            messages.success(request, 'Form submission successful')
    return render(request, 'admin/forms.html', locals())


def edit_supply_request(request, id):
    page = 'Edit Supply_Request'
    fullname = username(request)

    supply_request = Supply_request.objects.get(id=id)
    form = SupplyRequestForm(instance=supply_request)
    if request.method == 'POST':
        sub = SupplyRequestForm(request.POST, instance=supply_request)
        if sub.is_valid():
            sub.save()
            supply_request.last_update = timezone.now()
            supply_request.save()
            messages.success(request, 'Form submission successful')
            return render(request, 'admin/forms.html', locals())
        else:
            form = SupplyRequestForm(instance=supply_request)
    return render(request, 'admin/forms.html', locals())

def supply_request(request):
    page = 'All Supply Requests'
    fullname = username(request)
    latest_supply_request = Supply_request.objects.latest('date')
    table = SupplyRequestTable(Supply_request.objects.all(), orderable=True)
    RequestConfig(request).configure(table)
    name = 'Supply Request'
    button_name = 'Add New Supply Request'
    button_link = '/portal/new_supply_request'
    return render(request, 'admin/supply_requests.html', locals())

def single_supply_request(request, id):
    page = 'Individual Supply Meeting'
    fullname = username(request)
    supply_request = Supply_request.objects.get(id=id)
    buttons = [('Edit info', '/portal/edit_supply_request/' + str(id))]
    return render(request, 'admin/single_supply_request.html', locals())

#New Shopping Trip 

def new_shopping_trip(request):
    page = 'Add New Shopping Trip'
    fullname = username(request)
    form = ShoppingTripForm()
    if request.method == 'POST':
        sub = ShoppingTripForm(request.POST)
        if sub.is_valid():
            sub.save()
            messages.success(request, 'Form submission successful')
    return render(request, 'admin/forms.html', locals())


def edit_shopping_trip(request, id):
    page = 'Edit Shopping Trip'
    fullname = username(request)

    shopping_trip = Shopping_trip.objects.get(id=id)
    form = ShoppingTripForm(instance=shopping_trip)
    if request.method == 'POST':
        sub = ShoppingTripForm(request.POST, instance=shopping_trip)
        if sub.is_valid():
            sub.save()
            shopping_trip.last_update = timezone.now()
            shopping_trip.save()
            messages.success(request, 'Form submission successful')
            return render(request, 'admin/forms.html', locals())
        else:
            form = ShoppingTripForm(instance=shopping_trip)
    return render(request, 'admin/forms.html', locals())

def shopping_trip(request):
    page = 'All Shopping Trip'
    fullname = username(request)
    latest_shopping_trip = Shopping_trip.objects.latest('date')
    table = ShoppingTripTable(Shopping_trip.objects.all(), orderable=True)
    RequestConfig(request).configure(table)
    name = 'Shopping Trip'
    button_name = 'Add New Shopping Trip'
    button_link = '/portal/new_shopping_trip'
    return render(request, 'admin/shopping_trips.html', locals())

def single_shopping_trip(request, id):
    page = 'Individual Shopping Trip'
    fullname = username(request)
    shopping_trip = Shopping_trip.objects.get(id=id)
    buttons = [('Edit info', '/portal/edit_shopping_trip/' + str(id))]
    return render(request, 'admin/single_shopping_trip.html', locals())




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

# New Drug Test
# TODO Make drug field checkboxes inline with their label; Make other field appear conditional on if result == 'oth'
def new_dtest(request):
    page = 'New Drug Test'
    fullname = username(request)
    form = DrugTestForm()
    if request.method == 'POST':
        sub = DrugTestForm(request.POST)
        if sub.is_valid():
            sub.save()
    return render(request, 'admin/forms.html', locals())


def edit_dtest(request, test_id):
    page = 'Edit Drug Test'
    fullname = username(request)

    dtest = Drug_test.objects.get(id=test_id)
    form = DrugTestForm(instance=dtest)
    if request.method == 'POST':
        sub = DrugTestForm(request.POST, instance=dtest)
        if sub.is_valid():
            sub.save()
            dtest.last_update = timezone.now()
            dtest.save()
            return render(request, 'admin/forms.html', locals())
        else:
            form = DrugTestForm(instance=dtest)
    return render(request, 'admin/forms.html', locals())


def dtests(request):
    page = 'View All Drug Tests'
    fullname = username(request)

    table = DrugTestTable(Drug_test.objects.all().select_related('resident')
                          .annotate(full_name=Concat('resident__first_name', V(' '), 'resident__last_name')), )
    RequestConfig(request).configure(table)

    name = 'Drug Tests'
    button_name = 'Add New Drug Test'
    button_link = '/portal/new_dtest'
    return render(request, 'admin/temp_tables.html', locals())


# New Check-in
# TODO Restrict residents to residents in the manager's house
def new_check_in(request):
    page = 'New Check In'
    fullname = username(request)
    mngr = Resident.objects.get(pk=1)

    # TODO Automatically set manager to the manager who submitted the form
    form = CheckInForm(initial={'manager': mngr})
    if request.method == 'POST':
        sub = CheckInForm(request.POST)
        if sub.is_valid():
            sub.save()
    return render(request, 'admin/forms.html', locals())


def edit_check_in(request, ci_id):
    page = 'Edit Check In'
    fullname = username(request)

    ci = Check_in.objects.get(id=ci_id)
    form = CheckInForm(instance=ci)
    if request.method == 'POST':
        sub = CheckInForm(request.POST, instance=ci)
        if sub.is_valid():
            sub.save()
            ci.last_update = timezone.now()
            ci.save()
            return render(request, 'admin/forms.html', locals())
        else:
            form = CheckInForm(instance=ci)
    return render(request, 'admin/forms.html', locals())

def check_ins(request):
    page = 'View All Check Ins'
    fullname = username(request)

    # table = DrugTestTable(Drug_test.objects.all().select_related('resident')
    #                       .annotate(full_name=Concat('resident__first_name', V(' '), 'resident__last_name')), )

    table = CheckInTable(Check_in.objects.all().select_related('resident').select_related('manager')
                         .annotate(r_full_name=Concat('resident__first_name', V(' '), 'resident__last_name'),
                                   m_full_name=Concat('manager__first_name', V(' '), 'manager__last_name')))

    # table = CheckInTable(Check_in.objects.all())

    RequestConfig(request).configure(table)

    name = 'Check ins'
    button_name = 'Add New Check in'
    button_link = '/portal/new_check)in'
    return render(request, 'admin/temp_tables.html', locals())


# House Manager forms
@groups_only('House Manager')
def house_manager(request):
    context = {
        'page': 'Dashboard',
        'fullname': username(request),
    }
    return render(request, 'house/house_generic.html',context)