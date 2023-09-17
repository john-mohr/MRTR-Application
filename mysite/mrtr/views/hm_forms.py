from . import *
from ..forms import *
from ..tables import *
from custom_user.models import User
from django.shortcuts import render

def new_dtest(request):
    page = 'New Drug Test'
    fullname = username(request)
    rdr = request.META.get('HTTP_REFERER')

    form = DrugTestForm()

    if request.method == 'POST':
        rdr = request.POST.get('rdr')
        sub = DrugTestForm(request.POST)
        if sub.is_valid():
            sub.save()
            if rdr == 'None':
                rdr = 'http://127.0.0.1:8000/portal'
            return render(request, 'admin/confirmation.html', locals())
        else:
            form = DrugTestForm(request.POST)

    if user_is_hm(request):
        sidebar = hm_sidebar
        mngr = User.objects.get(pk=request.user.pk).assoc_resident
        form.fields['manager'].initial = mngr
        form.fields['resident'].queryset = form.fields['resident'].queryset.filter(
            bed__house=House.objects.get(manager=mngr).pk)
    else:
        sidebar = admin_sidebar

    return render(request, 'admin/forms.html', locals())


@groups_only('Admin')
def edit_dtest(request, test_id):
    page = 'Edit Drug Test'
    fullname = username(request)
    sidebar = admin_sidebar
    rdr = request.META.get('HTTP_REFERER')

    dtest = Drug_test.objects.get(id=test_id)
    dtest_subs = dtest.substances.split(', ')

    form = DrugTestForm(instance=dtest, initial={'substances': dtest_subs})
    if request.method == 'POST':
        rdr = request.POST.get('rdr')
        sub = DrugTestForm(request.POST, instance=dtest, initial={'substances': dtest_subs})
        if sub.is_valid():
            sub.save()
            dtest.last_update = timezone.now()
            dtest.save()
            if rdr == 'None':
                rdr = 'http://127.0.0.1:8000/portal'
            return render(request, 'admin/confirmation.html', locals())
        else:
            form = DrugTestForm(request.POST, instance=dtest)
    return render(request, 'admin/forms.html', locals())


# New Check-in
def new_check_in(request):
    page = 'New Check In'
    fullname = username(request)
    rdr = request.META.get('HTTP_REFERER')

    form = CheckInForm()

    if request.method == 'POST':
        rdr = request.POST.get('rdr')
        sub = CheckInForm(request.POST)
        if sub.is_valid():
            sub.save()
            if rdr == 'None':
                rdr = 'http://127.0.0.1:8000/portal'
            return render(request, 'admin/confirmation.html', locals())
        else:
            form = CheckInForm(request.POST)

    if user_is_hm(request):
        sidebar = hm_sidebar
        mngr = User.objects.get(pk=request.user.pk).assoc_resident
        form.fields['manager'].initial = mngr
        form.fields['resident'].queryset = form.fields['resident'].queryset.filter(
            bed__house=House.objects.get(manager=mngr).pk)
    else:
        sidebar = admin_sidebar

    return render(request, 'admin/forms.html', locals())


@groups_only('Admin')
def edit_check_in(request, ci_id):
    page = 'Edit Check In'
    fullname = username(request)
    sidebar = admin_sidebar
    rdr = request.META.get('HTTP_REFERER')

    ci = Check_in.objects.get(id=ci_id)
    form = CheckInForm(instance=ci)
    if request.method == 'POST':
        rdr = request.POST.get('rdr')
        sub = CheckInForm(request.POST, instance=ci)
        if sub.is_valid():
            sub.save()
            ci.last_update = timezone.now()
            ci.save()
            if rdr == 'None':
                rdr = 'http://127.0.0.1:8000/portal'
            return render(request, 'admin/confirmation.html', locals())
        else:
            form = CheckInForm(request.POST, instance=ci)
    return render(request, 'admin/forms.html', locals())


def new_site_visit(request):
    page = 'New Site Visit'
    fullname = username(request)
    rdr = request.META.get('HTTP_REFERER')

    form = SiteVisitForm()

    if request.method == 'POST':
        rdr = request.POST.get('rdr')
        sub = SiteVisitForm(request.POST)
        if sub.is_valid():
            sub.save()
            if rdr == 'None':
                rdr = 'http://127.0.0.1:8000/portal'
            return render(request, 'admin/confirmation.html', locals())
        else:
            form = SiteVisitForm(request.POST)

    if user_is_hm(request):
        sidebar = hm_sidebar
        mngr = User.objects.get(pk=request.user.pk).assoc_resident
        form.fields['manager'].initial = mngr
        form.fields['house'].initial = House.objects.get(manager=mngr)
        form.fields['house'].widget = forms.HiddenInput()
    else:
        sidebar = admin_sidebar

    return render(request, 'admin/forms.html', locals())


@groups_only('Admin')
def edit_site_visit(request, sv_id):
    page = 'Edit Site Visit'
    fullname = username(request)
    sidebar = admin_sidebar
    rdr = request.META.get('HTTP_REFERER')

    sv = Site_visit.objects.get(id=sv_id)
    sv_issues = sv.issues.split(', ')

    form = SiteVisitForm(instance=sv, initial={'issues': sv_issues})
    if request.method == 'POST':
        rdr = request.POST.get('rdr')
        sub = SiteVisitForm(request.POST, instance=sv, initial={'issues': sv_issues})
        if sub.is_valid():
            sub.save()
            sv.last_update = timezone.now()
            sv.save()
            if rdr == 'None':
                rdr = 'http://127.0.0.1:8000/portal'
            return render(request, 'admin/confirmation.html', locals())
        else:
            form = SiteVisitForm(request.POST, instance=sv)
    return render(request, 'admin/forms.html', locals())


def new_house_meeting(request):
    page = 'New House Meeting'
    fullname = username(request)
    rdr = request.META.get('HTTP_REFERER')

    form = HouseSelectForm()

    if request.method == 'POST':
        rdr = request.POST.get('rdr')
        house_id = request.POST.get('house')
        house = House.objects.get(id=int(house_id))
        form = HouseMeetingForm(initial={'house': house},
                                house=house)
        if 'issues' in request.POST:
            sub = HouseMeetingForm(request.POST, house=house)
            if sub.is_valid():
                meeting_id = sub.save()
                absentees = sub.cleaned_data['absentees']
                for i in range(len(absentees)):
                    absentee = Absentee(resident=absentees[i],
                                        meeting=meeting_id)
                    absentee.save()
                if rdr == 'None':
                    rdr = 'http://127.0.0.1:8000/portal'
                return render(request, 'admin/confirmation.html', locals())
            else:
                form = HouseMeetingForm(request.POST, house=house)

    if user_is_hm(request):
        sidebar = hm_sidebar
        mngr = User.objects.get(pk=request.user.pk).assoc_resident
        if request.method == 'GET':
            form = HouseMeetingForm(initial={'manager': mngr, 'house': House.objects.get(manager=mngr)},
                                    house=House.objects.get(manager=mngr).pk)
    else:
        sidebar = admin_sidebar
        if request.method == 'GET':
            form = HouseSelectForm()

    return render(request, 'admin/forms.html', locals())


@groups_only('Admin')
def edit_house_meeting(request, hm_id):
    page = 'Edit House Meeting'
    fullname = username(request)
    sidebar = admin_sidebar

    hm = House_meeting.objects.get(id=hm_id)
    hm_absentees_list = Absentee.objects.all().filter(meeting_id=hm_id).values_list('resident_id', flat=True)
    hm_absentees = Resident.objects.filter(id__in=hm_absentees_list)

    if request.method == 'GET':
        rdr = request.META.get('HTTP_REFERER')
        form = HouseMeetingForm(instance=hm, initial={'absentees': hm_absentees}, house=hm.house)
    else:
        rdr = request.POST.get('rdr')
        sub = HouseMeetingForm(request.POST, instance=hm, initial={'absentees': hm_absentees}, house=hm.house)
        if sub.is_valid():
            sub.save()
            new_absentees = sub.cleaned_data['absentees']

            if list(hm_absentees) != list(new_absentees):  # Check if Absentee table needs to be changed
                Absentee.objects.filter(meeting_id=hm_id).delete()  # Delete old Absentees
                for i in range(len(new_absentees)):  # Add new Absentees
                    absentee = Absentee(resident=new_absentees[i], meeting=hm)
                    absentee.save()

            hm.last_update = timezone.now()
            hm.save()
            if rdr == 'None':
                rdr = 'http://127.0.0.1:8000/portal'
            return render(request, 'admin/confirmation.html', locals())
        else:
            form = HouseMeetingForm(request.POST, instance=hm, house=hm.house)
    return render(request, 'admin/forms.html', locals())


def new_supply_request(request):
    page = 'Add New Supply Request'
    fullname = username(request)
    rdr = request.META.get('HTTP_REFERER')

    form = SupplyRequestForm()

    if request.method == 'POST':
        rdr = request.POST.get('rdr')
        house = request.POST.get('house')
        manager = request.POST.get('manager')
        products = request.POST.getlist('products')
        if len(products) == 0:
            form = SupplyRequestForm(request.POST)
        else:
            form = ProductForm(initial={'house': house, 'products': products, 'manager': manager}, products=products)
            sub = ProductForm(request.POST, products=products)
            if sub.is_valid():
                products = request.POST.getlist('products')
                replace_products = []
                other_note = ''
                for item in products:
                    if item == 'Other':
                        other_note = request.POST['other']
                    else:
                        x = (item, int(request.POST[item]))
                        replace_products.append(x)

                sr = Supply_request(products=replace_products,
                                    other=other_note,
                                    house_id=house,
                                    manager_id=manager)
                sr.save()
                if rdr == 'None':
                    rdr = 'http://127.0.0.1:8000/portal'
                return render(request, 'admin/confirmation.html', locals())

    if user_is_hm(request):
        sidebar = hm_sidebar
        mngr = User.objects.get(pk=request.user.pk).assoc_resident
        form.fields['manager'].initial = mngr
        form.fields['house'].initial = House.objects.get(manager=mngr)
        form.fields['house'].widget = forms.HiddenInput()
    else:
        sidebar = admin_sidebar

    return render(request, 'admin/forms.html', locals())


@groups_only('Admin')
def edit_supply_request(request, sr_id):
    page = 'Edit Supply_Request'
    fullname = username(request)
    sidebar = admin_sidebar
    supply_request = Supply_request.objects.get(id=sr_id)

    old_products = [ele[0] for ele in list(eval(supply_request.products))]
    old_other_note = ''

    if supply_request.other != '':
        old_products.append('Other')
        old_other_note = supply_request.other

    if request.method == 'GET':
        rdr = request.META.get('HTTP_REFERER')
        form = SupplyRequestForm(instance=supply_request, initial={'products': old_products})

    else:
        rdr = request.POST.get('rdr')
        house = int(request.POST.get('house'))
        new_products = request.POST.getlist('products')

        sub = ProductForm(request.POST, products=new_products)
        if sub.is_valid():
            replace_products = []
            other_note = ''
            for item in new_products:
                if item == 'Other':
                    other_note = request.POST['other']
                else:
                    x = (item, int(request.POST[item]))
                    replace_products.append(x)

            supply_request.house_id = house
            supply_request.products = replace_products
            supply_request.other = other_note
            supply_request.last_update = timezone.now()
            supply_request.save()

            if rdr == 'None':
                rdr = 'http://127.0.0.1:8000/portal'
            return render(request, 'admin/confirmation.html', locals())

        else:
            new_quants = []
            pqdict = dict(list(eval(supply_request.products)))
            for item in new_products:
                if item == 'Other':
                    x = old_other_note
                elif item in old_products:
                    x = pqdict[item]
                else:
                    x = 1
                new_quants.append(x)

            form = ProductForm(initial={'house': house, 'products': new_products, 'quants': new_quants},
                               products=new_products, quants=new_quants)
    return render(request, 'admin/forms.html', locals())


def new_maintenance_request(request):
    page = 'New Maintenance Request'
    fullname = username(request)
    rdr = request.META.get('HTTP_REFERER')

    form = MaintenanceRequestForm()
    form.fields['fulfillment_date'].widget = forms.HiddenInput()
    form.fields['fulfillment_notes'].widget = forms.HiddenInput()
    form.fields['fulfillment_cost'].widget = forms.HiddenInput()

    if request.method == 'POST':
        rdr = request.POST.get('rdr')
        sub = MaintenanceRequestForm(request.POST)
        if sub.is_valid():
            sub.save()
            if rdr == 'None':
                rdr = 'http://127.0.0.1:8000/portal'
            return render(request, 'admin/confirmation.html', locals())

    if user_is_hm(request):
        sidebar = hm_sidebar
        mngr = User.objects.get(pk=request.user.pk).assoc_resident
        form.fields['manager'].initial = mngr
        form.fields['house'].initial = House.objects.get(manager=mngr)
        form.fields['house'].widget = forms.HiddenInput()
    else:
        sidebar = admin_sidebar

    return render(request, 'admin/forms.html', locals())


@groups_only('Admin')
def fulfill_maintenance_request(request):
    page = 'Fulfill Maintenance Request'
    fullname = username(request)
    sidebar = admin_sidebar
    rdr = request.META.get('HTTP_REFERER')
    form = FulfillMaintReqForm()

    if request.method == 'POST':
        rdr = request.POST.get('rdr')
        form = FulfillMaintReqForm(request.POST)
        if len(form.errors) == 0:
            mr = Maintenance_request.objects.get(pk=request.POST.get('request'))
            mr.fulfilled = 1
            mr.fulfillment_date = request.POST.get('fulfillment_date')
            mr.fulfillment_notes = request.POST.get('fulfillment_notes')
            mr.fulfillment_cost = request.POST.get('fulfillment_cost')
            mr.last_update = timezone.now()
            mr.save()

            rdr = request.POST.get('rdr')
            if rdr == 'None':
                rdr = 'http://127.0.0.1:8000/portal'
            return render(request, 'admin/confirmation.html', locals())
    return render(request, 'admin/forms.html', locals())


@groups_only('Admin')
def edit_maintenance_request(request, mr_id):
    page = 'Edit Maintenance Request'
    fullname = username(request)
    sidebar = admin_sidebar
    mr = Maintenance_request.objects.get(id=mr_id)

    if request.method == 'GET':
        rdr = request.META.get('HTTP_REFERER')
        form = MaintenanceRequestForm(instance=mr)
        if mr.fulfilled:
            buttons = [('Mark Request as Unfulfilled', 'unfulfill'), ]
            form.fields['fulfillment_date'].required = True
            form.fields['fulfillment_cost'].required = True
        else:
            form.fields['fulfillment_date'].widget = forms.HiddenInput()
            form.fields['fulfillment_notes'].widget = forms.HiddenInput()
            form.fields['fulfillment_cost'].widget = forms.HiddenInput()
    else:
        rdr = request.POST.get('rdr')
        sub = MaintenanceRequestForm(request.POST, instance=mr)
        if sub.is_valid():
            sub.save()
            mr.last_update = timezone.now()
            if 'unfulfill' in request.POST:
                mr.fulfilled = False
                mr.fulfillment_cost = None
                mr.fulfillment_date = None
                mr.fulfillment_notes = ''
            mr.save()

            if rdr == 'None':
                rdr = 'http://127.0.0.1:8000/portal'
            return render(request, 'admin/confirmation.html', locals())
        else:
            form = MaintenanceRequestForm(request.POST, instance=mr)
    return render(request, 'admin/forms.html', locals())
