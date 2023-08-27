from . import *
from ..tables import *
from custom_user.models import User
from django.shortcuts import render
from django.db.models.functions import Concat
from django.db.models import Value, Sum
from ..filters import *
from django_tables2 import RequestConfig

def resident(request, res_id):
    res = Resident.objects.get(id=res_id)

    fullname = username(request)
    page = 'View Single Resident'
    name = res.full_name()

    if res.balance() >= 0:
        bal = '$' + str(res.balance())
    else:
        bal = '-$' + str(res.balance())[1:]
    headers = ['Balance: ' + bal]
    sidebar = admin_sidebar
    buttons = [('Add Rent Payment', '/portal/new_rent_pmt/' + str(res_id)),
               ('Adjust Balance', '/portal/new_trans/' + str(res_id)),
               ('Edit info', '/portal/edit_res/' + str(res_id))]

    if res.discharge_date is None:
        headers.insert(0, '(Current Resident)')
        buttons.append(('Discharge', '/portal/discharge_res/' + str(res_id)))
        bed_name = res.bed.name
        res_house = res.bed.house
        house_link = ' href=' + res.bed.house.get_absolute_url()
    else:
        headers.insert(0, '(Past Resident)')
        buttons.append(('Readmit', '/portal/readmit_res/' + str(res_id)))
        bed_name = ''
        res_house = ''
        house_link = ''

    hm = user_is_hm(request)

    if hm:
        sidebar = hm_sidebar
        buttons = []
        hm_exc = ('id', )
    else:
        hm_exc = ()

    contact_info_data = [{'name': 'Phone', 'value': '(' + res.phone[:3] + ') ' + res.phone[3:6] + '-' + res.phone[6:]},
                         {'name': 'Email', 'value': res.email}]
    contact_info = RowTable(contact_info_data, show_header=False)
    RequestConfig(request).configure(contact_info)

    if res.discharge_date is None:
        dd = '—'
    else:
        dd = res.discharge_date.strftime('%m/%d/%Y')
    res_details_data = [{'name': 'Admit date', 'value': res.admit_date.strftime('%m/%d/%Y')},
                        {'name': 'Discharge date', 'value': dd},
                        {'name': 'Rent', 'value': '$' + str(res.rent)},
                        {'name': 'House', 'value': res.bed.house},
                        {'name': 'Bed', 'value': res.bed.name},
                        {'name': 'Door code', 'value': res.door_code},
                        {'name': 'Referral info', 'value': res.referral_info},
                        {'name': 'Notes', 'value': res.notes}]
    if hm:
        res_details_data[3]['value'] = res_details_data[3].get('value').name
    res_details = RowTable(res_details_data, show_header=False)
    RequestConfig(request).configure(res_details)

    # TODO (dean) allow users to show/hide the ledger, dtests, and check_ins tables
    ledger = TransactionTable(Transaction.objects.filter(resident=res_id),
                              order_by='-date', orderable=True,
                              exclude=('submission_date', 'resident', 'last_update') + hm_exc)
    RequestConfig(request).configure(ledger)

    dtests = DrugTestTable(Drug_test.objects.filter(resident=res_id),
                           order_by='-date', orderable=True,
                           exclude=('resident', ) + hm_exc)
    RequestConfig(request).configure(dtests)

    check_ins = CheckInTable(Check_in.objects.filter(resident=res_id),
                             order_by='-date', orderable=True,
                             exclude=('resident', ) + hm_exc)
    RequestConfig(request).configure(check_ins)

    if hm:
        check_ins.columns[0].link = None

    sections = [
        ('Contact Info', contact_info),
        ('Resident Details', res_details),
        ('Ledger', ledger),
        ('Drug Tests', dtests),
        ('Check-ins', check_ins)
    ]

    if hm:
        mngr = User.objects.get(pk=request.user.pk).assoc_resident
        if res.bed is None:
            return redirect('/forbidden')
        elif res.bed.house != mngr.bed.house:
            return redirect('/forbidden')

    return render(request, 'admin/singles.html', locals())


def house(request, house_id):
    cur_house = House.objects.get(name=house_id)
    house_id = cur_house.pk

    fullname = username(request)
    name = cur_house.name
    headers = ['Address: ' + cur_house.address + ' ' + cur_house.city + ', ' + cur_house.state]

    if user_is_hm(request):
        sidebar = hm_sidebar
        page = 'House Manager Dashboard'
        buttons = [
            ('Add new drug test', '/portal/new_dtest'),
            ('Add new check in', '/portal/new_check_in'),
            ('Add new site visit', '/portal/new_site_visit'),
            ('Add new house meeting', '/portal/new_house_meeting'),
        ]
        hm_exc = ('id', )
    else:
        sidebar = admin_sidebar
        page = 'View Single House'
        buttons = [('Edit info', '/portal/edit_house/' + str(house_id))]
        hm_exc = ()

    # House residents table
    house_res = ShortResidentsTable(Resident.objects.filter(bed__house=house_id)
                                    .annotate(balance=Sum('transaction__amount'),
                                              full_name=Concat('first_name', Value(' '), 'last_name')),
                                    order_by='-balance', orderable=True, exclude='discharge_date')
    RequestConfig(request).configure(house_res)

    # Vacant beds table
    occupied_beds = Resident.objects.all().filter(bed_id__isnull=False).distinct()
    vacant_beds = BedTable(Bed.objects
                           .exclude(id__in=occupied_beds.values_list('bed_id', flat=True))
                           .filter(house__id=house_id),
                           exclude=('resident', 'house'))

    # Most recent drug test for each resident table
    latest_dtests = []
    for res in house_res.data:
        latest_dtest = Drug_test.objects.filter(resident=res)
        if latest_dtest.exists():
            latest_dtests.append(latest_dtest.latest('date').pk)
    recent_dtests = DrugTestTable(Drug_test.objects.filter(pk__in=latest_dtests),
                                  order_by='-date', orderable=True, exclude=hm_exc)
    RequestConfig(request).configure(recent_dtests)

    # Most recent check in for each resident table
    latest_check_ins = []
    for res in house_res.data:
        latest_check_in = Check_in.objects.filter(resident=res)
        if latest_check_in.exists():
            latest_check_ins.append(latest_check_in.latest('date').pk)

    recent_check_ins = CheckInTable(Check_in.objects.filter(pk__in=latest_check_ins),
                                    order_by='-date', orderable=True, exclude=('manager', ) + hm_exc)
    RequestConfig(request).configure(recent_check_ins)

    # Latest site visit info table
    house_sv = Site_visit.objects.filter(house=house_id)
    if house_sv.exists():
        latest_sv = house_sv.latest('date')

        if latest_sv.manager is None:
            mngr = 'Admin'
        else:
            mngr = latest_sv.manager

        if latest_sv.last_update is None:
            lu = '—'
        else:
            lu = latest_sv.last_update.strftime('%m/%d/%Y %I:%M %p')

        visit_data = [{'name': 'Date', 'value': latest_sv.date.strftime('%m/%d/%Y')},
                      {'name': 'Issues', 'value': latest_sv.issues},
                      {'name': 'Explanation', 'value': latest_sv.explanation},
                      {'name': 'Submitter', 'value': mngr},
                      {'name': 'Submission date', 'value': latest_sv.submission_date.strftime('%m/%d/%Y %I:%M %p')},
                      {'name': 'Last update', 'value': lu},
                      {'name': 'Edit', 'value': latest_sv.get_absolute_url()}]

        if user_is_hm(request):
            visit_data = visit_data[:-1]
            visit_data[3]['value'] = visit_data[3].get('value').__str__()

    else:
        visit_data = [{'name': 'None', 'value': '(so far)'}]

    visit = RowTable(visit_data, show_header=False)
    RequestConfig(request).configure(visit)

    # Latest house meeting info tables
    house_m = House_meeting.objects.filter(house=house_id)
    if house_m.exists():
        latest_m = house_m.latest('date')

        if latest_m.manager is None:
            mngr = 'Admin'
        else:
            mngr = latest_m.manager

        if latest_m.last_update is None:
            lu = '—'
        else:
            lu = latest_m.last_update.strftime('%m/%d/%Y %I:%M %p')

        absentees = ', '.join(list(Absentee.objects.all()
                                   .filter(meeting_id=latest_m.pk)
                                   .select_related('resident')
                                   .annotate(full_name=Concat('resident__first_name', Value(' '), 'resident__last_name'))
                                   .values_list('full_name', flat=True)))

        meeting_data = [{'name': 'Date', 'value': latest_m.date.strftime('%m/%d/%Y')},
                        {'name': 'Issues', 'value': latest_m.issues},
                        {'name': 'Absentees', 'value': absentees},
                        {'name': 'Submitter', 'value': mngr},
                        {'name': 'Submission date', 'value': latest_m.submission_date.strftime('%m/%d/%Y %I:%M %p')},
                        {'name': 'Last update', 'value': lu},
                        {'name': 'Edit', 'value': latest_m.get_absolute_url()}]

        if user_is_hm(request):
            meeting_data = meeting_data[:-1]
            meeting_data[3]['value'] = meeting_data[3].get('value').__str__()

    else:
        meeting_data = [{'name': 'None', 'value': '(so far)'}]

    meeting = RowTable(meeting_data, show_header=False)
    RequestConfig(request).configure(meeting)

    sections = [
        ('Residents', house_res),
        ('Vacant Beds', vacant_beds),
        ('Latest Drug Tests', recent_dtests),
        ('Latest Check-ins', recent_check_ins),
        ('Latest Site Visit', visit),
        ('Latest House Meeting', meeting)
    ]

    return render(request, 'admin/singles.html', locals())

# TODO finish implementing
def single_shopping_trip(request, id):
    page = 'Individual Shopping Trip'
    fullname = username(request)
    shoppingtrip = Shopping_trip.objects.get(id=id)
    qs = Supply_request.objects.filter(trip=shoppingtrip)
    buttons = [('Edit info', '/portal/edit_shopping_trip/' + str(id))]
    table_filter = SupplyRequestFilter(request.GET, queryset=qs)
    table = SupplyRequestTable(table_filter.qs)
    return render(request, 'admin/singles.html', locals())
