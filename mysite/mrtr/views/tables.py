from . import *
from ..tables import *
from ..filters import *
from custom_user.models import User
from django.shortcuts import render
from django.db.models import Sum
from django_tables2 import RequestConfig


def table_view(request, page_link, page_name, table_filter, table, buttons=None):
    fullname = username(request)
    link = page_link
    page = page_name
    if user_is_hm(request):
        sidebar = hm_sidebar
        if 'manager' in table.columns:
            table.columns['manager'].link = None
    else:
        sidebar = admin_sidebar
    table_filter = table_filter
    table = table
    RequestConfig(request, paginate=False).configure(table)
    if buttons is not None:
        add_buttons = True
    return render(request, 'admin/tables.html', locals())


@groups_only('Admin')
def residents(request):
    buttons = [('Add New Resident', '/portal/new_res'), ]
    qs = Resident.objects.annotate(
        balance=Sum('transaction__amount'))

    table_filter = ResidentFilter(request.GET, queryset=qs)
    
    table = ResidentsTable(table_filter.qs, order_by='-admit_date', orderable=True, exclude='full_name')
    return table_view(request, 'residents', 'View All Residents', table_filter, table, buttons)


@groups_only('Admin')
def transactions(request):
    buttons = [('Add New Transaction', '/portal/new_trans'), ]
    qs = Transaction.objects.all().select_related('resident')

    table_filter = TransactionFilter(request.GET, queryset=qs)

    table = TransactionTable(table_filter.qs, order_by='-date', orderable=True)
    return table_view(request, 'transactions', 'View All Transactions', table_filter, table, buttons)


@groups_only('Admin')
def houses(request):
    qs = House.objects.all()

    table_filter = HouseFilter(request.GET, queryset=qs)

    table = HouseTable(table_filter.qs, orderable=True)
    return table_view(request, 'houses', 'View All Houses', table_filter, table)


@groups_only('Admin')
def beds(request):
    qs = Bed.objects.all()

    table_filter = BedFilter(request.GET, queryset=qs)

    table = BedTable(table_filter.qs, exclude=('id',))
    return table_view(request, 'beds', 'View All Beds', table_filter, table)


def dtests(request):
    buttons = [('Add New Drug Test', '/portal/new_dtest'), ]
    if user_is_hm(request):
        mngr = User.objects.get(pk=request.user.pk).assoc_resident
        qs = Drug_test.objects.filter(resident__bed__house=House.objects.get(manager=mngr))
        hm_exc = ('id', )
    else:
        qs = Drug_test.objects.all()
        hm_exc = ''

    table_filter = DrugTestFilter(request.GET, queryset=qs)

    table = DrugTestTable(table_filter.qs, order_by='-date', orderable=True, exclude=hm_exc)
    return table_view(request, 'dtests', 'View All Drug Tests', table_filter, table, buttons)


def check_ins(request):
    buttons = [('Add New Check In', '/portal/new_check_in'), ]
    if user_is_hm(request):
        mngr = User.objects.get(pk=request.user.pk).assoc_resident
        qs = Check_in.objects.filter(resident__bed__house=House.objects.get(manager=mngr))
        hm_exc = ('id', )
    else:
        qs = Check_in.objects.all()
        hm_exc = ''

    table_filter = CheckInFilter(request.GET, queryset=qs)

    table = CheckInTable(table_filter.qs, order_by='-date', orderable=True, exclude=hm_exc)
    return table_view(request, 'check_ins', 'View All Check Ins', table_filter, table, buttons)


def site_visits(request):
    buttons = [('Add New Site Visit', '/portal/new_site_visit'), ]
    if user_is_hm(request):
        mngr = User.objects.get(pk=request.user.pk).assoc_resident
        qs = Site_visit.objects.filter(house=House.objects.get(manager=mngr))
        hm_exc = ('id', 'house')
    else:
        qs = Site_visit.objects.all()
        hm_exc = ''

    table_filter = SiteVisitFilter(request.GET, queryset=qs)

    table = SiteVisitTable(table_filter.qs, order_by='-date', orderable=True, exclude=hm_exc)
    return table_view(request, 'site_visits', 'View All Site Visits', table_filter, table, buttons)


def house_meetings(request):
    buttons = [('Add New House Meeting', '/portal/new_house_meeting'), ]
    if user_is_hm(request):
        mngr = User.objects.get(pk=request.user.pk).assoc_resident
        qs = House_meeting.objects.filter(house=House.objects.get(manager=mngr))
        hm_exc = ('id', 'house')
    else:
        qs = House_meeting.objects.all()
        hm_exc = ''

    table_filter = HouseMeetingFilter(request.GET, queryset=qs)

    table = HouseMeetingTable(table_filter.qs, order_by='-date', orderable=True, exclude=hm_exc)
    return table_view(request, 'house_meetings', 'View All House Meetings', table_filter, table, buttons)


def supply_requests(request):
    buttons = [('Add New Supply Request', '/portal/new_supply_request'), ]
    if user_is_hm(request):
        mngr = User.objects.get(pk=request.user.pk).assoc_resident
        qs = Supply_request.objects.filter(house=House.objects.get(manager=mngr))
        hm_exc = ('id', 'house', 'trip')
    else:
        qs = Supply_request.objects.all()
        hm_exc = ''

    table_filter = SupplyRequestFilter(request.GET, queryset=qs)

    table = SupplyRequestTable(table_filter.qs, order_by='-submission_date', orderable=True, exclude=hm_exc)
    return table_view(request, 'supply_requests', 'View All Supply Requests', table_filter, table, buttons)


@groups_only('Admin')
def shopping_trips(request):
    qs = Shopping_trip.objects.all()

    table_filter = ShoppingTripFilter(request.GET, queryset=qs)

    table = ShoppingTripTable(table_filter.qs, order_by='-date', orderable=True)
    return table_view(request, 'shopping_trips', 'View All Shopping Trips', table_filter, table)


def maintenance_requests(request):
    buttons = [('Add New Maintenance Request', '/portal/new_maintenance_request'), ]
    if user_is_hm(request):
        mngr = User.objects.get(pk=request.user.pk).assoc_resident
        qs = Maintenance_request.objects.filter(house=House.objects.get(manager=mngr))
        hm_exc = ('id', 'house')
    else:
        qs = Maintenance_request.objects.all()
        hm_exc = ''
        buttons.append(('Fulfill Maintenance Request', '/portal/fulfill_maintenance_request'))

    table_filter = MaintenanceRequestFilter(request.GET, queryset=qs)

    table = MaintenanceRequestTable(table_filter.qs, order_by=('fulfilled', '-fulfillment_date'), orderable=True, exclude=hm_exc)
    return table_view(request, 'maintenance_requests', 'View All Maintenance Requests', table_filter, table, buttons)


def mngr_meetings(request):
    qs = Manager_meeting.objects.all()

    if user_is_hm(request):
        hm_exc = ('id', )
        buttons = None
    else:
        hm_exc = ''
        buttons = [('Add New Meeting', '/portal/new_mngr_meeting'), ]

    table_filter = ManagerMeetingFilter(request.GET, queryset=qs)

    table = ManagerMeetingTable(table_filter.qs, order_by='-date', orderable=True, exclude=hm_exc)
    return table_view(request, 'mngr_meetings', 'View All Manager Meetings', table_filter, table, buttons)
