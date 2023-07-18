from ..forms import *
from ..tables import *
from django.shortcuts import render, redirect
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone
from django.contrib import messages
from django.db.models import Sum, Value
from django.db.models.functions import Concat
from django_tables2 import RequestConfig
from functools import wraps


def forbidden(request):
    return render(request, 'mrtr/forbidden.html')


def groups_only(*groups):
    def inner(view_func):
        @wraps(view_func)
        def wrapper_func(request, *args, **kwargs):
            if request.user.groups.filter(name__in=groups).exists() or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            else:
                return redirect('/forbidden')
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
    un = request.user.first_name + " " + request.user.last_name
    return un


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
        balance=Sum('transaction__amount'), full_name=Concat('first_name', Value(' '), 'last_name')),
        order_by='-balance')
    RequestConfig(request).configure(res_balances)
    return render(request, 'admin/homepage.html', locals())


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

# TODO standardize and move to table_views
def meetings(request):
    page = 'All Meetings'
    fullname = username(request)
    try:
        latest_meeting = Manager_meeting.objects.latest('submission_date')
    except :
        print("Empty Database")
    table = ManagerMeetingTable(Manager_meeting.objects.all(), orderable=True)
    RequestConfig(request).configure(table)
    name = 'Meetings'
    button_name = 'Add New Meeting'
    button_link = '/portal/new_meeting'
    return render(request, 'admin/meetings.html', locals())

# TODO standardize and move to single_views (or get rid of)
def single_meeting(request, id):
    page = 'Individual Meeting'
    fullname = username(request)
    meeting = Manager_meeting.objects.get(id=id)
    buttons = [('Edit info', '/portal/edit_meeting/' + str(id))]
    return render(request, 'admin/single_meeting.html', locals())

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


# TODO standardize and move to table_views
def supply_request(request):
    page = 'All Supply Requests'
    fullname = username(request)
    try:
        latest_supply_request = Supply_request.objects.latest('date')
    except :
        print("Empty Database")
    table = SupplyRequestTable(Supply_request.objects.all(), orderable=True)
    RequestConfig(request).configure(table)
    name = 'Supply Request'
    button_name = 'Add New Supply Request'
    button_link = '/portal/new_supply_request'
    return render(request, 'admin/supply_requests.html', locals())

# TODO standardize and move to single_views (or get rid of)
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


# TODO standardize and move to table_views
def shopping_trip(request):
    page = 'All Shopping Trip'
    fullname = username(request)
    
    try:
        latest_shopping_trip = Shopping_trip.objects.latest('date')
    except :
        print("Empty Database")
    table = ShoppingTripTable(Shopping_trip.objects.all(), orderable=True)
    RequestConfig(request).configure(table)
    name = 'Shopping Trip'
    button_name = 'Add New Shopping Trip'
    button_link = '/portal/new_shopping_trip'
    return render(request, 'admin/shopping_trips.html', locals())


# TODO standardize and move to single_views (or get rid of)
def single_shopping_trip(request, id):
    page = 'Individual Shopping Trip'
    fullname = username(request)
    shopping_trip = Shopping_trip.objects.get(id=id)
    buttons = [('Edit info', '/portal/edit_shopping_trip/' + str(id))]
    return render(request, 'admin/single_shopping_trip.html', locals())


# House Manager forms
@groups_only('House Manager')
def house_manager(request):
    context = {
        'page': 'Dashboard',
        'fullname': username(request),
    }
    return render(request, 'house/house_generic.html', context)
