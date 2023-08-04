from ..tables import *
from .o_views import username
from django.shortcuts import render
from django.db.models.functions import Concat
from django.db.models import Value, Sum
from django_tables2 import RequestConfig

def resident(request, res_id):
    res = Resident.objects.get(id=res_id)

    fullname = username(request)
    page = 'View Single Resident'
    name = res.full_name()
    headers = ['Balance: $' + str(res.balance())]
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
        bed_name = None
        res_house = None
        house_link = ''

    res_info = list(res.__dict__.items())
    res_info = [(item[0].replace('_', ' ').title(), item[1]) for item in res_info]
    res_info.append(('Bed Name', bed_name))
    res_info.append(('House Name', res_house, house_link))

    contact_info = res_info[4:6]

    res_details = [res_info[i] for i in [6, 12, 7, 16, 15, 9, 10, 11]]

    # TODO Maybe add date filters to ledger, dtests, and check_ins
    ledger = TransactionTable(Transaction.objects.filter(resident=res_id),
                              order_by='-date', orderable=True,
                              exclude=('submission_date', 'resident', 'last_update'))
    RequestConfig(request).configure(ledger)

    dtests = DrugTestTable(Drug_test.objects.filter(resident=res_id),
                           order_by='-date', orderable=True,
                           exclude={'resident'})
    RequestConfig(request).configure(dtests)

    check_ins = CheckInTable(Check_in.objects.filter(resident=res_id),
                             order_by='-date', orderable=True,
                             exclude={'resident'})
    RequestConfig(request).configure(check_ins)

    sections = [
        ('Contact Info', False, contact_info),
        ('Resident Details', False, res_details),
        ('Ledger', True, ledger),
        ('Drug Tests', True, dtests),
        ('Check-ins', True, check_ins)
    ]

    return render(request, 'admin/overview.html', locals())


def house(request, house_id):
    cur_house = House.objects.get(id=house_id)

    fullname = username(request)
    page = 'View Single House'
    name = cur_house.name
    headers = ['Address: ' + cur_house.address + ' ' + cur_house.city + ', ' + cur_house.state]
    buttons = [('Edit info', '/portal/edit_house/' + str(house_id))]

    # House residents table
    house_res = ShortResidentsTable(Resident.objects.filter(bed__house=house_id)
                                    .annotate(balance=Sum('transaction__amount'),
                                              full_name=Concat('first_name', Value(' '), 'last_name')),
                                    order_by='-balance', orderable=True)
    RequestConfig(request).configure(house_res)

    # Vacant beds table
    occupied_beds = Resident.objects.all().filter(bed_id__isnull=False).distinct()
    vacant_beds = BedTable(Bed.objects
                           .exclude(id__in=occupied_beds.values_list('bed_id', flat=True))
                           .filter(id=house_id),
                           exclude=('resident', 'house'))

    # Most recent drug test for each resident table
    latest_dtests = []
    for res in house_res.data:
        latest_dtests.append(Drug_test.objects.filter(resident=res).latest('date').pk)
    recent_dtests = DrugTestTable(Drug_test.objects.filter(pk__in=latest_dtests),
                                  order_by='-date', orderable=True)
    RequestConfig(request).configure(recent_dtests)

    # Most recent check in for each resident table
    latest_check_ins = []
    for res in house_res.data:
        latest_check_ins.append(Check_in.objects.filter(resident=res).latest('date').pk)

    recent_check_ins = CheckInTable(Check_in.objects.filter(pk__in=latest_check_ins),
                                    order_by='-date', orderable=True, exclude='manager')
    RequestConfig(request).configure(recent_check_ins)

    # Latest site visit info table
    house_sv = Site_visit.objects.filter(house=house_id)
    if len(house_sv) == 0:
        visit = []
    else:
        latest_sv = house_sv.latest('date')
        sv_list = list(latest_sv.__dict__.items())
        sv_list = [(item[0].replace('_', ' ').title(), item[1]) for item in sv_list]
        sv_list.append(('Manager', latest_sv.manager, ' href=' + latest_sv.manager.get_absolute_url()))
        sv_list.append(('Edit link', 'X', ' href=' + latest_sv.get_absolute_url()))
        visit = [sv_list[i] for i in [2, 3, 4, 9, 7, 8, 10]]

    # Latest house meeting info tables
    house_m = House_meeting.objects.filter(house=house_id)
    if len(house_m) == 0:
        meeting = []
    else:
        latest_m = house_m.latest('date')
        m_list = list(latest_m.__dict__.items())
        m_list = [(item[0].replace('_', ' ').title(), item[1]) for item in m_list]
        m_list.append(('Manager', latest_m.manager, ' href=' + latest_m.manager.get_absolute_url()))
        m_list.append(('Edit link', 'X', ' href=' + latest_m.get_absolute_url()))
        absentees = ', '.join(list(Absentee.objects.all()
                                   .filter(meeting_id=latest_m.pk)
                                   .select_related('resident')
                                   .annotate(full_name=Concat('resident__first_name', Value(' '), 'resident__last_name'))
                                   .values_list('full_name', flat=True)))
        m_list.append(('Absentees', absentees, ''))
        meeting = [m_list[i] for i in [2, 3, 10, 8, 6, 7, 9]]

    sections = [
        ('Residents', True, house_res),
        ('Vacant Beds', True, vacant_beds),
        ('Latest Drug Tests', True, recent_dtests),
        ('Latest Check-ins', True, recent_check_ins),
        ('Latest Site Visit', False, visit),
        ('Latest House Meeting', False, meeting)
    ]

    return render(request, 'admin/overview.html', locals())
