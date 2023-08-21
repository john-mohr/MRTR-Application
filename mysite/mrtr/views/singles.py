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
    headers = ['Balance: $' + str(res.balance())]
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
        bed_name = None
        res_house = None
        house_link = ''

    hm = user_is_hm(request)

    if hm:
        sidebar = hm_sidebar
        buttons = []
        hm_exc = ('id', )
    else:
        hm_exc = ()

    res_info = list(res.__dict__.items())
    res_info = [(item[0].replace('_', ' ').title(), item[1]) for item in res_info]
    res_info.append(('Bed Name', bed_name))
    res_info.append(('House Name', res_house, house_link))

    contact_info = res_info[4:6]

    res_details = [res_info[i] for i in [6, 12, 7, 16, 15, 9, 10, 11]]

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
        ('Contact Info', False, contact_info),
        ('Resident Details', False, res_details),
        ('Ledger', True, ledger),
        ('Drug Tests', True, dtests),
        ('Check-ins', True, check_ins)
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
        sv_list = list(latest_sv.__dict__.items())
        sv_list = [(item[0].replace('_', ' ').title(), item[1]) for item in sv_list]

        if latest_sv.issues == '':
            sv_list[3] = ('Issues', 'None reported')
        if latest_sv.explanation == '':
            sv_list[4] = ('Explanation', 'None provided')
        if latest_sv.manager is None:
            sv_list.append(('Submitter', 'Admin'))
        else:
            sv_list.append(('Submitter', latest_sv.manager, ' href=' + latest_sv.manager.get_absolute_url()))

        sv_list.append(('Edit link', 'Click here', ' href=' + latest_sv.get_absolute_url()))

        visit = [sv_list[i] for i in [2, 3, 4, 9, 7, 8, 10]]
        if user_is_hm(request):
            visit[3] = (visit[3][0], visit[3][1], '')
            visit = visit[:-1]
    else:
        visit = [('None', '(so far)')]

    # Latest house meeting info tables
    house_m = House_meeting.objects.filter(house=house_id)
    if house_m.exists():
        latest_m = house_m.latest('date')
        m_list = list(latest_m.__dict__.items())
        m_list = [(item[0].replace('_', ' ').title(), item[1]) for item in m_list]
        if latest_m.manager is None:
            m_list.append(('Submitter', 'Admin'))
        else:
            m_list.append(('Submitter', latest_m.manager, ' href=' + latest_m.manager.get_absolute_url()))
        m_list.append(('Edit link', 'Click here', ' href=' + latest_m.get_absolute_url()))
        absentees = ', '.join(list(Absentee.objects.all()
                                   .filter(meeting_id=latest_m.pk)
                                   .select_related('resident')
                                   .annotate(full_name=Concat('resident__first_name', Value(' '), 'resident__last_name'))
                                   .values_list('full_name', flat=True)))
        m_list.append(('Absentees', absentees, ''))
        meeting = [m_list[i] for i in [2, 3, 10, 8, 6, 7, 9]]
        if user_is_hm(request):
            meeting[3] = (meeting[3][0], meeting[3][1], '')
            meeting = meeting[:-1]
    else:
        meeting = [('None', '(so far)')]

    sections = [
        ('Residents', True, house_res),
        ('Vacant Beds', True, vacant_beds),
        ('Latest Drug Tests', True, recent_dtests),
        ('Latest Check-ins', True, recent_check_ins),
        ('Latest Site Visit', False, visit),
        ('Latest House Meeting', False, meeting)
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
