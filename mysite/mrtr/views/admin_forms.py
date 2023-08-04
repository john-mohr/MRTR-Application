from ..forms import *
from ..tables import *
from .o_views import username, groups_only
from ..utils import prorate
from django.shortcuts import render, redirect
from dateutil.relativedelta import relativedelta

# TODO improve or remove messages
from django.contrib import messages


# TODO Add proper redirects to each view (see new_trans and new_rent_pmt)


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
    return render(request, 'admin/forms.html', {'form': form, 'page': 'Remove Resident', 'fullname': username(request)})


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
    prev_mngr = house.manager
    form = HouseForm(instance=house)
    if request.method == 'POST':
        sub = HouseForm(request.POST, instance=house)
        if sub.is_valid():
            sub.save()
            house.last_update = timezone.now()
            house.save()
            # # TODO Handle multiple house managers for one house (replace House.manager with a relationship table)
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

            messages.success(request, 'Form submission successful')
            return render(request, 'admin/forms.html', locals())
        else:
            form = HouseForm(instance=house)
    return render(request, 'admin/forms.html', locals())


