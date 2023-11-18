from . import *
from .singles import house
from ..forms import *
from ..tables import *
from ..filters import *
from custom_user.models import User
from django.shortcuts import render, redirect
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.db.models import Sum, Value
from django.db.models.functions import Concat
from django_tables2 import RequestConfig


def forbidden(request):
    return render(request, 'mrtr/forbidden.html')


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
def portal(request):
    current_user = User.objects.get(pk=request.user.pk)
    request.session['django_timezone'] = current_user.timezone

    if user_is_hm(request):
        mngr = User.objects.get(pk=request.user.pk)
        cur_house = House.objects.get(manager=mngr.assoc_resident)
        return house(request, cur_house.name)
    else:
        page = 'Dashboard'
        fullname = username(request)
        sidebar = admin_sidebar

        buttons = [('Add Resident', '/portal/new_res'),
                   ('Add Rent Payment', '/portal/new_rent_pmt'),
                   ('Adjust Balance', '/portal/new_trans')]

        occupied_beds = Resident.objects.all().filter(bed_id__isnull=False).distinct()
        beds_qs = Bed.objects.exclude(id__in=occupied_beds.values_list('bed_id', flat=True))
        vacant_beds = BedTable(beds_qs, order_by='house', orderable=True,
                               exclude=('id', 'resident', ))
        RequestConfig(request, paginate=False).configure(vacant_beds)

        balances_qs = Resident.objects.annotate(
            balance=Sum('transaction__amount'),
            full_name=Concat('first_name', Value(' '), 'last_name'))
        table_filter = ResidentBalanceFilter(request.GET, queryset=balances_qs)
        res_balances = ShortResidentsTable(table_filter.qs, order_by='-balance', orderable=True,
                                           exclude=('rent', 'bed', 'door_code'))
        RequestConfig(request, paginate=False).configure(res_balances)

        return render(request, 'admin/admin_portal.html', locals())


def intake(request):
    return render(request, 'mrtr/intake.html', locals())
