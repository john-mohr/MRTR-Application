from . import *
from ..forms import *
from ..tables import *
from ..utils import prorate
from django.shortcuts import render
from dateutil.relativedelta import relativedelta

# New Resident
@groups_only('Admin')
def new_res(request):
    page = "Add New Resident"
    fullname = username(request)
    sidebar = admin_sidebar
    form = ResidentForm()
    rdr = request.META.get('HTTP_REFERER')

    if request.method == 'POST':
        rdr = request.POST.get('rdr')
        sub = ResidentForm(request.POST)
        if sub.is_valid():
            sub.save()

            # Add beginning balance transactions
            intake = Transaction(date=sub.instance.admit_date,
                                 amount=100,
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
                                    notes=(sub.instance.admit_date + relativedelta(months=1)).strftime('%B') + ' (advance)',
                                    submission_date=sub.instance.submission_date
                                    )
            second_mo.save()

            if rdr == 'None':
                rdr = 'http://127.0.0.1:8000/portal'
            return render(request, 'admin/confirmation.html', locals())
        else:
            form = ResidentForm(request.POST)
    return render(request, 'admin/forms.html', locals())


@groups_only('Admin')
def edit_res(request, res_id):
    page = 'Edit Resident Information'
    fullname = username(request)
    sidebar = admin_sidebar
    rdr = request.META.get('HTTP_REFERER')

    resident = Resident.objects.get(id=res_id)
    old_rent = resident.rent
    form = ResidentForm(instance=resident)
    if request.method == 'POST':
        rdr = request.POST.get('rdr')
        sub = ResidentForm(request.POST, instance=resident)
        if sub.is_valid():
            new_rent = int(request.POST['rent'])
            if old_rent != new_rent:
                adj_trans = Transaction(date=sub.cleaned_data['effective_date'],
                                        amount=prorate(new_rent - old_rent, sub.cleaned_data['effective_date']),
                                        type='Rent adjustment',
                                        resident=resident,
                                        notes='$' + str(old_rent) + ' > $' + str(new_rent) + ' (automatic)'
                                        )
                adj_trans.save()
            sub.save()
            resident.last_update = timezone.now()
            resident.save()
            if rdr == 'None':
                rdr = 'http://127.0.0.1:8000/portal'
            return render(request, 'admin/confirmation.html', locals())
        else:
            form = ResidentForm(request.POST, instance=resident)
    return render(request, 'admin/forms.html', locals())


@groups_only('Admin')
def discharge_res(request, res_id):
    page = 'Remove Resident'
    fullname = username(request)
    sidebar = admin_sidebar
    rdr = request.META.get('HTTP_REFERER')

    resident = Resident.objects.get(id=res_id)
    form = DischargeResForm()
    if request.method == 'POST':
        rdr = request.POST.get('rdr')
        sub = DischargeResForm(request.POST)
        if sub.is_valid():
            resident.discharge_date = sub.cleaned_data['date']
            resident.bed = None
            resident.last_update = timezone.now()
            if len(sub.cleaned_data['reason']) > 0:
                resident.notes = str(resident.notes) + '\nReason Discharged (' + str(sub.cleaned_data['date']) + '): ' + sub.cleaned_data['reason']
            # TODO (wait) Figure out if TC wants an option to refund rent
            resident.save()
            if rdr == 'None':
                rdr = 'http://127.0.0.1:8000/portal'
            return render(request, 'admin/confirmation.html', locals())
    return render(request, 'admin/forms.html', locals())


# Readmit resident
@groups_only('Admin')
def readmit_res(request, res_id):
    page = 'Readmit Resident'
    fullname = username(request)
    sidebar = admin_sidebar
    rdr = request.META.get('HTTP_REFERER')

    resident = Resident.objects.get(id=res_id)
    form = ResidentForm(instance=resident)
    if request.method == 'POST':
        rdr = request.POST.get('rdr')
        sub = ResidentForm(request.POST, instance=resident)
        if sub.is_valid():
            resident.notes = resident.notes + '\n Previous residency: ' + \
                             str(resident.admit_date) + ' to ' + str(resident.discharge_date)
            resident.admit_date = sub.cleaned_data['effective_date']
            resident.discharge_date = None
            resident.last_update = timezone.now()
            sub.save()
            resident.save()

            current_month = Transaction(date=sub.instance.admit_date,
                                        amount=prorate(sub.instance.rent, sub.instance.admit_date),
                                        type='Rent charge',
                                        resident=sub.instance,
                                        notes=sub.instance.admit_date.strftime('%B') + ' (partial)',
                                        submission_date=sub.instance.submission_date
                                        )
            current_month.save()

            if rdr == 'None':
                rdr = 'http://127.0.0.1:8000/portal'
            return render(request, 'admin/confirmation.html', locals())
        else:
            form = ResidentForm(request.POST, instance=resident)
    return render(request, 'admin/forms.html', locals())


# New transaction
@groups_only('Admin')
def new_trans(request, res_id=None):
    page = 'New Transaction'
    fullname = username(request)
    sidebar = admin_sidebar
    rdr = request.META.get('HTTP_REFERER')

    if res_id is not None:
        form = TransactionForm(initial={'resident': Resident.objects.get(pk=res_id)})
        form.fields['resident'].widget = forms.HiddenInput()
    else:
        form = TransactionForm()

    if request.method == 'POST':
        rdr = request.POST.get('rdr')
        sub = TransactionForm(request.POST)
        if sub.is_valid():
            if sub.instance.type != 'Fix' and sub.instance.type != 'Other (specify)':
                sub.instance.amount = abs(sub.instance.amount)

            # Make transaction amount negative for transactions that decrease a resident's balance
            decrease = ['Rent payment', 'Bonus', 'Work/reimbursement', 'Sober support']
            if sub.instance.type in decrease:
                sub.instance.amount *= -1
            sub.save()

            if rdr == 'None':
                rdr = 'http://127.0.0.1:8000/portal'
            return render(request, 'admin/confirmation.html', locals())
        else:
            form = TransactionForm(request.POST)
    return render(request, 'admin/forms.html', locals())


@groups_only('Admin')
def new_rent_pmt(request, res_id=None):
    page = 'New Rent Payment'
    fullname = username(request)
    sidebar = admin_sidebar
    rdr = request.META.get('HTTP_REFERER')

    if res_id is not None:
        form = RentPaymentForm(initial={'resident': Resident.objects.get(pk=res_id)})
        form.fields['resident'].widget = forms.HiddenInput()
    else:
        form = RentPaymentForm()

    if request.method == 'POST':
        rdr = request.POST.get('rdr')
        sub = RentPaymentForm(request.POST)
        if sub.is_valid():
            sub.instance.amount = abs(sub.instance.amount)
            sub.instance.amount *= -1
            sub.instance.type = 'Rent payment'
            sub.save()
            if rdr == 'None':
                rdr = 'http://127.0.0.1:8000/portal'
            return render(request, 'admin/confirmation.html', locals())
        else:
            form = RentPaymentForm(request.POST)
    return render(request, 'admin/forms.html', locals())


# Edit transaction
@groups_only('Admin')
def edit_trans(request, trans_id):
    page = 'Edit Transaction'
    fullname = username(request)
    sidebar = admin_sidebar
    rdr = request.META.get('HTTP_REFERER')

    trans = Transaction.objects.get(id=trans_id)

    if trans.type != 'Fix' and trans.type != 'Other (specify)':
        trans.amount = abs(trans.amount)

    if trans.type == 'Rent payment':
        form = RentPaymentForm(instance=trans)
    else:
        form = TransactionForm(instance=trans)

    if request.method == 'POST':
        rdr = request.POST.get('rdr')
        if trans.type == 'Rent payment':
            sub = RentPaymentForm(request.POST, instance=trans)
        else:
            sub = TransactionForm(request.POST, instance=trans)
        if sub.is_valid():
            if sub.instance.type != 'Fix' and sub.instance.type != 'Other (specify)':
                sub.instance.amount = abs(sub.instance.amount)

            # Make transaction amount negative for transactions that decrease a resident's balance
            decrease = ['Rent payment', 'Bonus', 'Work/reimbursement', 'Sober support']
            if sub.instance.type in decrease:
                sub.instance.amount *= -1

            trans.last_update = timezone.now()
            sub.save()
            if rdr == 'None':
                rdr = 'http://127.0.0.1:8000/portal'
            return render(request, 'admin/confirmation.html', locals())
        else:
            form = TransactionForm(request.POST, instance=trans)
    return render(request, 'admin/forms.html', locals())


# New House
@groups_only('Admin')
def new_house(request):
    page = 'Add New House'
    fullname = username(request)
    sidebar = admin_sidebar
    rdr = request.META.get('HTTP_REFERER')

    form = HouseForm()
    if request.method == 'POST':
        rdr = request.POST.get('rdr')
        sub = HouseForm(request.POST)
        if sub.is_valid():
            sub.save()
            if rdr == 'None':
                rdr = 'http://127.0.0.1:8000/portal'
            return render(request, 'admin/confirmation.html', locals())
    return render(request, 'admin/forms.html', locals())


@groups_only('Admin')
def edit_house(request, house_id):
    page = 'Edit House'
    fullname = username(request)
    sidebar = admin_sidebar
    rdr = request.META.get('HTTP_REFERER')

    house = House.objects.get(id=house_id)
    prev_mngr = house.manager
    form = HouseForm(instance=house, house=house)
    if request.method == 'POST':
        rdr = request.POST.get('rdr')
        sub = HouseForm(request.POST, instance=house, house=house)
        if sub.is_valid():
            sub.save()
            house.last_update = timezone.now()
            house.save()
            # TODO (wait) Handle multiple house managers for one house (replace House.manager with a relationship table)
            if house.manager != prev_mngr:
                current_datetime = timezone.now()
                current_date = current_datetime.date()

                if prev_mngr is not None:
                    rm_discount = Transaction(date=current_date,
                                              amount=prorate((prev_mngr.rent * 2) - prev_mngr.rent, current_date),
                                              type='Rent adjustment',
                                              resident=prev_mngr,
                                              notes='Change: $' + str(prev_mngr.rent) +
                                                    ' > $' + str(prev_mngr.rent * 2) +
                                                    '; Reason: removed house manager discount'
                                              )
                    rm_discount.save()
                    prev_mngr.rent = prev_mngr.rent * 2
                    prev_mngr.save()

                if house.manager is not None:
                    add_discount = Transaction(date=current_date,
                                               amount=prorate((house.manager.rent / 2) - house.manager.rent, current_date),
                                               type='Rent adjustment',
                                               resident=house.manager,
                                               notes='Change: $' + str(house.manager.rent) +
                                                     ' > $' + str(house.manager.rent / 2) +
                                                     '; Reason: added house manager discount'
                                               )
                    add_discount.save()
                    house.manager.rent = house.manager.rent / 2
                    house.manager.save()

            if rdr == 'None':
                rdr = 'http://127.0.0.1:8000/portal'
            return render(request, 'admin/confirmation.html', locals())
    return render(request, 'admin/forms.html', locals())


@groups_only('Admin')
def new_shopping_trip(request):
    page = 'Complete shopping trip'
    fullname = username(request)
    sidebar = admin_sidebar
    rdr = request.META.get('HTTP_REFERER')

    form = ShoppingTripForm(initial={'date': timezone.now()})
    if request.method == 'POST':
        rdr = request.POST.get('rdr')
        sub = ShoppingTripForm(request.POST)
        if sub.is_valid():
            trip_id = sub.save()
            assoc_reqs = Supply_request.objects.filter(trip_id__isnull=True)
            for i in range(len(assoc_reqs)):
                assoc_reqs[i].trip = trip_id
                assoc_reqs[i].fulfilled = 1
                assoc_reqs[i].save()
            if rdr == 'None':
                rdr = 'http://127.0.0.1:8000/portal'
            return render(request, 'admin/confirmation.html', locals())
        else:
            form = ShoppingTripForm(request.POST)
    return render(request, 'admin/forms.html', locals())


@groups_only('Admin')
def edit_shopping_trip(request, trip_id):
    page = 'Edit shopping trip'
    fullname = username(request)
    sidebar = admin_sidebar
    rdr = request.META.get('HTTP_REFERER')

    trip = Shopping_trip.objects.get(id=trip_id)
    form = ShoppingTripForm(instance=trip)
    if request.method == 'POST':
        rdr = request.POST.get('rdr')
        sub = ShoppingTripForm(request.POST, instance=trip)
        if sub.is_valid():
            sub.save()
            trip.last_update = timezone.now()
            trip.save()
            if rdr == 'None':
                rdr = 'http://127.0.0.1:8000/portal'
            return render(request, 'admin/confirmation.html', locals())
        else:
            form = ShoppingTripForm(request.POST, instance=trip)
    return render(request, 'admin/forms.html', locals())
