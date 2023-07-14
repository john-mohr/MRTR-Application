from .tables import *
from .views import username
from django.shortcuts import render, redirect
from django.db.models.functions import Concat
from django.db.models import Value, Sum, Max, F
from django_tables2 import RequestConfig

# TODO Make tables sortable

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
        house_name = res.bed.house.name
    else:
        headers.insert(0, '(Past Resident)')
        buttons.append(('Readmit', '/portal/readmit_res/' + str(res_id)))
        bed_name = None
        house_name = None

    res_info = list(res.__dict__.items())
    res_info = [(item[0].replace('_', ' '), item[1]) for item in res_info]
    res_info = [(item[0].title(), item[1]) for item in res_info]
    res_info.append(('Bed Name', bed_name))
    res_info.append(('House Name', house_name))

    contact_info = res_info[4:6]
    res_details = [res_info[i] for i in [6, 12, 8, 16, 15, 9, 10, 11]]

    ledger = TransactionTable(Transaction.objects.filter(resident=res_id).order_by('-submission_date'),
                              exclude=('submission_date', 'full_name', 'last_update'))

    dtests = DrugTestTable(Drug_test.objects.filter(resident=res_id).order_by('-date'),
                           exclude={'full_name'})

    check_ins = CheckInTable(Check_in.objects.filter(resident=res_id).select_related('manager').annotate(
        m_full_name=Concat('manager__first_name', Value(' '), 'manager__last_name')).order_by('-date'),
        exclude={'r_full_name'})

    sections = [('Contact Info', False, contact_info),
                ('Resident Details', False, res_details),
                ('Ledger', True, ledger),
                ('Drug Tests', True, dtests),
                ('Check-ins', True, check_ins)]

    return render(request, 'admin/overview.html', locals())


def house(request, house_id):
    cur_house = House.objects.get(id=house_id)

    fullname = username(request)
    page = 'View Single House'
    name = cur_house.name
    headers = ['Address: ' + cur_house.address + ' ' + cur_house.city + ', ' + cur_house.state]
    buttons = [('Edit info', '/portal/edit_house/' + str(house_id))]

    house_res = ResidentsTable(Resident.objects.filter(bed__house=house_id).annotate(balance=Sum('transaction__amount')),
                               exclude=('submission_date', 'house', 'referral_info', 'notes', 'last_update'),
                               orderable=True, order_by='-balance')

    occupied_beds = Resident.objects.all().filter(bed_id__isnull=False).distinct()
    vacant_beds = BedTable(
        Bed.objects.exclude(id__in=occupied_beds.values_list('bed_id', flat=True)).filter(id=house_id),
        order_by='house', orderable=True, exclude=('full_name', 'house'))

    # TODO limit to recent drug tests only
    recent_dtests = DrugTestTable(Drug_test.objects
                                  .filter(resident__bed__house=house_id)
                                  .annotate(full_name=Concat('resident__first_name', Value(' '), 'resident__last_name'))
                                  # [:5]
                                  )

    # TODO limit to recent check ins only
    recent_check_ins = CheckInTable(Check_in.objects.select_related('resident')
                                    .filter(resident__bed__house=house_id)
                                    .annotate(r_full_name=Concat('resident__first_name', Value(' '), 'resident__last_name')),
                                    exclude='m_full_name')

    # TODO limit to recent check ins only
    recent_site_visits = SiteVisitTable(Site_visit.objects.select_related('manager')
                                        .filter(house=house_id)
                                        .annotate(full_name=Concat('manager__first_name', Value(' '), 'manager__last_name')),
                                        exclude='house')

    sections = [('Residents', True, house_res),
                ('Vacant Beds', True, vacant_beds),
                ('Recent Drug Tests', True, recent_dtests),
                ('Recent Check-ins', True, recent_check_ins),
                ('Recent Site Visits', True, recent_site_visits)]

    return render(request, 'admin/overview.html', locals())

