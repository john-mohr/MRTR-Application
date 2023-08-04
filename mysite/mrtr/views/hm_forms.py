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
        else:
            print(sub.errors)
    return render(request, 'admin/forms.html', locals())


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
    rdr = request.META.get('HTTP_REFERER')

    mngr = User.objects.get(pk=request.user.pk).assoc_resident

    if user_is_hm(request):
        sidebar = hm_sidebar
        form = HouseMeetingForm(initial={'manager': mngr, 'house': House.objects.get(manager=mngr)},
                                is_hm=True, house=House.objects.get(manager=mngr).pk)
        form.fields['house'].widget = forms.HiddenInput()
    else:
        sidebar = admin_sidebar
        form = HouseMeetingForm(initial={'manager': None})

    form.fields['manager'].required = False

    if request.method == 'POST':
        sub = HouseMeetingForm(request.POST)
        if sub.is_valid():
            meeting_id = sub.save()
            absentees = sub.cleaned_data['absentees']
            for i in range(len(absentees)):
                absentee = Absentee(resident=absentees[i],
                                    meeting=meeting_id)
                absentee.save()
            rdr = request.POST.get('rdr')
            if rdr == 'None':
                rdr = 'http://127.0.0.1:8000/portal'
            return render(request, 'admin/confirmation.html', locals())
    return render(request, 'admin/forms.html', locals())


def edit_house_meeting(request, hm_id):
    page = 'Edit House Meeting'
    fullname = username(request)
    sidebar = admin_sidebar
    rdr = request.META.get('HTTP_REFERER')

    hm = House_meeting.objects.get(id=hm_id)
    hm_absentees_list = Absentee.objects.all().filter(meeting_id=hm_id).values_list('resident_id', flat=True)
    hm_absentees = Resident.objects.filter(id__in=hm_absentees_list)

    form = HouseMeetingForm(instance=hm, initial={'absentees': hm_absentees})
    if request.method == 'POST':
        sub = HouseMeetingForm(request.POST, instance=hm, initial={'absentees': hm_absentees})
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
        else:
            print('invalid')
            form = HouseMeetingForm(instance=hm, initial={'absentees': hm_absentees})
    return render(request, 'admin/forms.html', locals())
