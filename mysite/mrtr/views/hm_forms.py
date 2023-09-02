from . import *
from ..forms import *
from ..tables import *
from custom_user.models import User
from django.shortcuts import render


def new_dtest(request):
    page = 'New Drug Test'
    fullname = username(request)
    rdr = request.META.get('HTTP_REFERER')

    mngr = User.objects.get(pk=request.user.pk).assoc_resident

    if user_is_hm(request):
        sidebar = hm_sidebar
        form = DrugTestForm(is_hm=True, house=House.objects.get(manager=mngr).pk)
    else:
        sidebar = admin_sidebar
        form = DrugTestForm()
    if request.method == 'POST':
        sub = DrugTestForm(request.POST)
        if sub.is_valid():
            sub.save()
            rdr = request.POST.get('rdr')
            if rdr == 'None':
                rdr = 'http://127.0.0.1:8000/portal'
            return render(request, 'admin/confirmation.html', locals())
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
        sub = DrugTestForm(request.POST, instance=dtest, initial={'substances': dtest_subs})
        if sub.is_valid():
            sub.save()
            dtest.last_update = timezone.now()
            dtest.save()
            rdr = request.POST.get('rdr')
            if rdr == 'None':
                rdr = 'http://127.0.0.1:8000/portal'
            return render(request, 'admin/confirmation.html', locals())
        else:
            form = DrugTestForm(instance=dtest, initial={'substances': dtest_subs})
    return render(request, 'admin/forms.html', locals())


# New Check-in
def new_check_in(request):
    page = 'New Check In'
    fullname = username(request)
    rdr = request.META.get('HTTP_REFERER')

    mngr = User.objects.get(pk=request.user.pk).assoc_resident

    if user_is_hm(request):
        sidebar = hm_sidebar
        form = CheckInForm(initial={'manager': mngr}, is_hm=True, house=House.objects.get(manager=mngr).pk)
    else:
        sidebar = admin_sidebar
        form = CheckInForm(initial={'manager': mngr})

    if request.method == 'POST':
        sub = CheckInForm(request.POST)
        if sub.is_valid():
            sub.save()
            rdr = request.POST.get('rdr')
            if rdr == 'None':
                rdr = 'http://127.0.0.1:8000/portal'
            return render(request, 'admin/confirmation.html', locals())
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
        sub = CheckInForm(request.POST, instance=ci)
        if sub.is_valid():
            sub.save()
            ci.last_update = timezone.now()
            ci.save()
            rdr = request.POST.get('rdr')
            if rdr == 'None':
                rdr = 'http://127.0.0.1:8000/portal'
            return render(request, 'admin/confirmation.html', locals())
        else:
            form = CheckInForm(instance=ci)
    return render(request, 'admin/forms.html', locals())


def new_site_visit(request):
    page = 'New Site Visit'
    fullname = username(request)
    rdr = request.META.get('HTTP_REFERER')

    mngr = User.objects.get(pk=request.user.pk).assoc_resident

    if user_is_hm(request):
        sidebar = hm_sidebar
        form = SiteVisitForm(initial={'manager': mngr, 'house': House.objects.get(manager=mngr)})
        form.fields['house'].widget = forms.HiddenInput()
    else:
        sidebar = admin_sidebar
        form = SiteVisitForm(initial={'manager': mngr})

    form.fields['manager'].required = False

    if request.method == 'POST':
        sub = SiteVisitForm(request.POST)
        if sub.is_valid():
            sub.save()
            rdr = request.POST.get('rdr')
            if rdr == 'None':
                rdr = 'http://127.0.0.1:8000/portal'
            return render(request, 'admin/confirmation.html', locals())
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
        sub = SiteVisitForm(request.POST, instance=sv, initial={'issues': sv_issues})
        if sub.is_valid():
            sub.save()
            sv.last_update = timezone.now()
            sv.save()
            rdr = request.POST.get('rdr')
            if rdr == 'None':
                rdr = 'http://127.0.0.1:8000/portal'
            return render(request, 'admin/confirmation.html', locals())
        else:
            form = SiteVisitForm(instance=sv, initial={'issues': sv_issues})
    return render(request, 'admin/forms.html', locals())


def new_house_meeting(request):
    page = 'New House Meeting'
    fullname = username(request)
    if request.method == 'GET':
        rdr = request.META.get('HTTP_REFERER')
        mngr = User.objects.get(pk=request.user.pk).assoc_resident

        if user_is_hm(request):
            sidebar = hm_sidebar
            form = HouseMeetingForm(initial={'manager': mngr, 'house': House.objects.get(manager=mngr)},
                                    house=House.objects.get(manager=mngr).pk)
        else:
            sidebar = admin_sidebar
            form = HouseSelectForm()
    else:
        sidebar = admin_sidebar
        rdr = request.POST.get('rdr')
        house_id = request.POST.get('house')
        house = House.objects.get(id=int(house_id))
        form = HouseMeetingForm(initial={'house': house},
                                house=house)
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
    return render(request, 'admin/forms.html', locals())


@groups_only('Admin')
def edit_house_meeting(request, hm_id):
    page = 'Edit House Meeting'
    fullname = username(request)
    sidebar = admin_sidebar
    rdr = request.META.get('HTTP_REFERER')

    hm = House_meeting.objects.get(id=hm_id)
    hm_absentees_list = Absentee.objects.all().filter(meeting_id=hm_id).values_list('resident_id', flat=True)
    hm_absentees = Resident.objects.filter(id__in=hm_absentees_list)

    form = HouseMeetingForm(instance=hm, initial={'absentees': hm_absentees}, house=hm.house)
    if request.method == 'POST':
        sub = HouseMeetingForm(request.POST, instance=hm, initial={'absentees': hm_absentees}, house=hm.house)
        if sub.is_valid():
            x = sub.save()

            new_absentees = sub.cleaned_data['absentees']

            if list(hm_absentees) != list(new_absentees):  # Check if Absentee table needs to be changed
                Absentee.objects.filter(meeting_id=hm_id).delete()  # Delete old Absentees
                for i in range(len(new_absentees)):  # Add new Absentees
                    absentee = Absentee(resident=new_absentees[i],
                                        meeting=hm)
                    absentee.save()

            hm.last_update = timezone.now()
            hm.save()
            rdr = request.POST.get('rdr')
            if rdr == 'None':
                rdr = 'http://127.0.0.1:8000/portal'
            return render(request, 'admin/confirmation.html', locals())
    return render(request, 'admin/forms.html', locals())

# New Supply Request
def new_supply_request(request):
    page = 'Add New Supply Request'
    fullname = username(request)

    if request.method == 'GET':
        rdr = request.META.get('HTTP_REFERER')
        mngr = User.objects.get(pk=request.user.pk).assoc_resident

        if user_is_hm(request):
            sidebar = hm_sidebar
            form = SupplyRequestForm(initial={'house': House.objects.get(manager=mngr), 'fulfilled': False})
            form.fields['house'].widget = forms.HiddenInput()
        else:
            sidebar = admin_sidebar
            form = SupplyRequestForm(initial={'fulfilled': False})

    else:
        rdr = request.POST.get('rdr')
        sub = SupplyRequestForm(request.POST)
        products = request.POST.getlist('products')
        # TODO going to the previous page after submitting the first part creates an unfinished duplicate
        if sub.is_valid():
            sr = sub.save()
            sr_id = sr.pk
        else:
            sr_id = 0

        form = ProductForm(initial={'temp1': sr_id}, products=products)
        sub = ProductForm(request.POST, products=products)
        if sub.is_valid():
            sr = Supply_request.objects.get(pk=int(request.POST['temp1']))
            products = list(eval(sr.products))

            replace_products = []
            other_note = ''
            for item in products:
                if item == 'Other':
                    other_note = request.POST['other']
                else:
                    x = (item, int(request.POST[item]))
                    replace_products.append(x)

            sr.products = replace_products
            sr.other = other_note
            sr.trip = Shopping_trip.objects.get(date__isnull=True)
            sr.save()
            if rdr == 'None':
                rdr = 'http://127.0.0.1:8000/portal'
            return render(request, 'admin/confirmation.html', locals())
        else:
            if user_is_hm(request):
                sidebar = hm_sidebar
            else:
                sidebar = admin_sidebar

    return render(request, 'admin/forms.html', locals())


@groups_only('Admin')
def edit_supply_request(request, sr_id):
    page = 'Edit Supply_Request'
    fullname = username(request)
    supply_request = Supply_request.objects.get(id=sr_id)

    old_products = [ele[0] for ele in list(eval(supply_request.products))]
    old_other_note = ''

    if supply_request.other != '':
        old_products.append('Other')
        old_other_note = supply_request.other

    if request.method == 'GET':
        rdr = request.META.get('HTTP_REFERER')
        sidebar = admin_sidebar
        form = SupplyRequestForm(instance=supply_request, initial={'products': old_products})

    else:
        rdr = request.POST.get('rdr')
        sub = SupplyRequestForm(request.POST)
        if sub.is_valid():
            new_products = sub.cleaned_data['products']
            new_quantities = []
            pqdict = dict(list(eval(supply_request.products)))
            for item in new_products:
                if item == 'Other':
                    x = old_other_note
                elif item in old_products:
                    x = pqdict[item]
                else:
                    x = 1
                new_quantities.append(x)

            supply_request.products = new_products
            supply_request.save()
        else:
            new_quantities = list(eval(request.POST['temp2']))
            new_products = list(eval(supply_request.products))
        form = ProductForm(initial={'temp2': new_quantities}, products=new_products, quants=new_quantities)
        sub = ProductForm(request.POST, products=new_products, quants=new_quantities)
        if sub.is_valid():
            products = list(eval(supply_request.products))

            replace_products = []
            other_note = ''
            for item in products:
                if item == 'Other':
                    other_note = request.POST['other']
                else:
                    x = (item, int(request.POST[item]))
                    replace_products.append(x)

            supply_request.products = replace_products
            supply_request.other = other_note
            supply_request.last_update = timezone.now()
            supply_request.save()

            if rdr == 'None':
                rdr = 'http://127.0.0.1:8000/portal'
            return render(request, 'admin/confirmation.html', locals())
        else:
            sidebar = admin_sidebar

    return render(request, 'admin/forms.html', locals())

