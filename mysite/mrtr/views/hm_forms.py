from .o_views import username, groups_only
from ..forms import *
from ..tables import *
from custom_user.models import User
from django.shortcuts import render


# TODO:
#  Make substance options appear conditional on if result is positive
#  Make 'other' field appear conditional on if result == 'oth'


# TODO Maybe automatically set manager to the manager who submitted the form
@groups_only('House Manager')
def new_dtest(request):
    page = 'New Drug Test'
    fullname = username(request)
    form = DrugTestForm()
    if request.method == 'POST':
        sub = DrugTestForm(request.POST)
        if sub.is_valid():
            sub.save()
    return render(request, 'admin/forms.html', locals())


@groups_only('Admin')
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


# New Check-in
# TODO Restrict residents to residents in the manager's house
def new_check_in(request):
    page = 'New Check In'
    fullname = username(request)

    mngr = User.objects.get(pk=request.user.pk)

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


def new_site_visit(request):
    page = 'New Site Visit'
    fullname = username(request)

    mngr = User.objects.get(pk=request.user.pk)

    form = SiteVisitForm(initial={'manager': mngr})
    if request.method == 'POST':
        sub = SiteVisitForm(request.POST)
        if sub.is_valid():
            sub.save()
    return render(request, 'admin/forms.html', locals())


def edit_site_visit(request, sv_id):
    page = 'Edit Site Visit'
    fullname = username(request)

    sv = Site_visit.objects.get(id=sv_id)
    sv_issues = sv.issues.split(', ')

    form = SiteVisitForm(instance=sv, initial={'issues': sv_issues})
    if request.method == 'POST':
        sub = SiteVisitForm(request.POST, instance=sv, initial={'issues': sv_issues})
        if sub.is_valid():
            sub.save()
            sv.last_update = timezone.now()
            sv.save()
            return render(request, 'admin/forms.html', locals())
        else:
            form = SiteVisitForm(instance=sv, initial={'issues': sv_issues})
    return render(request, 'admin/forms.html', locals())


def new_house_meeting(request):
    page = 'New House Meeting'
    fullname = username(request)

    mngr = User.objects.get(pk=request.user.pk)

    form = HouseMeetingForm(initial={'manager': mngr})
    if request.method == 'POST':
        sub = HouseMeetingForm(request.POST)
        if sub.is_valid():
            meeting_id = sub.save()
            absentees = sub.cleaned_data['absentees']
            for i in range(len(absentees)):
                absentee = Absentee(resident=absentees[i],
                                    meeting=meeting_id)
                absentee.save()

    return render(request, 'admin/forms.html', locals())


def edit_house_meeting(request, hm_id):
    page = 'Edit House Meeting'
    fullname = username(request)

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
            return render(request, 'admin/forms.html', locals())
        else:
            print('invalid')
            form = HouseMeetingForm(instance=hm, initial={'absentees': hm_absentees})
    return render(request, 'admin/forms.html', locals())
