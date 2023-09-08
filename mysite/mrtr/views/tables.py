from . import *
from ..tables import *
from ..filters import *
from custom_user.models import User
from django.shortcuts import render
from django.db.models.functions import Concat
from django.db.models import Value, Sum, Q
from django_tables2 import RequestConfig


def table_view(request, page_link, page_name, table_filter, table, button_name=None, button_link=None):
    fullname = username(request)
    link = page_link
    page = page_name
    if user_is_hm(request):
        sidebar = hm_sidebar
        table.columns[1].link = None
    else:
        sidebar = admin_sidebar
    table_filter = table_filter
    table = table
    RequestConfig(request, paginate=False).configure(table)
    if button_name is None or button_link is None:
        buttons = False
    else:
        buttons = True
        button_name = button_name
        button_link = '/portal/' + button_link
    return render(request, 'admin/tables.html', locals())


@groups_only('Admin')
def residents(request):
    qs = Resident.objects.annotate(
        balance=Sum('transaction__amount'))

    table_filter = ResidentFilter(request.GET, queryset=qs)
    
    table = ResidentsTable(table_filter.qs, order_by='-admit_date', orderable=True, exclude='full_name')
    return table_view(request, 'residents', 'View All Residents', table_filter, table, 'Add New Resident', 'new_res')


@groups_only('Admin')
def transactions(request):
    qs = Transaction.objects.all().select_related('resident')

    table_filter = TransactionFilter(request.GET, queryset=qs)

    table = TransactionTable(table_filter.qs, order_by='-date', orderable=True)
    return table_view(request, 'transactions', 'View All Transactions', table_filter, table, 'Add New Transaction', 'new_trans')


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
    if user_is_hm(request):
        mngr = User.objects.get(pk=request.user.pk).assoc_resident
        qs = Drug_test.objects.filter(resident__bed__house=House.objects.get(manager=mngr))
        hm_exc = ('id', )
    else:
        qs = Drug_test.objects.all()
        hm_exc = ''

    table_filter = DrugTestFilter(request.GET, queryset=qs)

    table = DrugTestTable(table_filter.qs, order_by='-date', orderable=True, exclude=hm_exc)
    return table_view(request, 'dtests', 'View All Drug Tests', table_filter, table, 'Add New Drug Test', 'new_dtest')


def check_ins(request):
    if user_is_hm(request):
        mngr = User.objects.get(pk=request.user.pk).assoc_resident
        qs = Check_in.objects.filter(resident__bed__house=House.objects.get(manager=mngr))
        hm_exc = ('id', )
    else:
        qs = Check_in.objects.all()
        hm_exc = ''

    table_filter = CheckInFilter(request.GET, queryset=qs)

    table = CheckInTable(table_filter.qs, order_by='-date', orderable=True, exclude=hm_exc)
    return table_view(request, 'check_ins', 'View All Check Ins', table_filter, table, 'Add New Check In', 'new_check_in')


def site_visits(request):
    if user_is_hm(request):
        mngr = User.objects.get(pk=request.user.pk).assoc_resident
        qs = Site_visit.objects.filter(house=House.objects.get(manager=mngr))
        hm_exc = ('id', 'house')
    else:
        qs = Site_visit.objects.all()
        hm_exc = ''

    table_filter = SiteVisitFilter(request.GET, queryset=qs)

    table = SiteVisitTable(table_filter.qs, order_by='-date', orderable=True, exclude=hm_exc)
    return table_view(request, 'site_visits', 'View All Site Visits', table_filter, table, 'Add New Site Visit', 'new_site_visit')


def house_meetings(request):
    if user_is_hm(request):
        mngr = User.objects.get(pk=request.user.pk).assoc_resident
        qs = House_meeting.objects.filter(house=House.objects.get(manager=mngr))
        hm_exc = ('id', 'house')
    else:
        qs = House_meeting.objects.all()
        hm_exc = ''

    table_filter = HouseMeetingFilter(request.GET, queryset=qs)

    table = HouseMeetingTable(table_filter.qs, order_by='-date', orderable=True, exclude=hm_exc)
    return table_view(request, 'house_meetings', 'View All House Meetings', table_filter, table, 'Add New House Meeting', 'new_house_meeting')


def supply_requests(request):
    if user_is_hm(request):
        mngr = User.objects.get(pk=request.user.pk).assoc_resident
        qs = Supply_request.objects.filter(house=House.objects.get(manager=mngr))
        hm_exc = ('id', 'house', 'trip')
    else:
        qs = Supply_request.objects.all()
        hm_exc = ''

    table_filter = SupplyRequestFilter(request.GET, queryset=qs)

    table = SupplyRequestTable(table_filter.qs, order_by='-submission_date', orderable=True, exclude=hm_exc)
    return table_view(request, 'supply_requests', 'View All Supply Requests', table_filter, table, 'Add New Supply Request', 'new_supply_request')


@groups_only('Admin')
def shopping_trips(request):
    qs = Shopping_trip.objects.all()

    table_filter = ShoppingTripFilter(request.GET, queryset=qs)

    table = ShoppingTripTable(table_filter.qs, order_by='-date', orderable=True)
    return table_view(request, 'shopping_trips', 'View All Shopping Trips', table_filter, table)

@groups_only('Admin')
def meetings(request):
    qs = Manager_meeting.objects.all()

    table_filter = ManagerMeetingFilter(request.GET, queryset=qs)

    table = ManagerMeetingTable(table_filter.qs, order_by='-date', orderable=True)
    return table_view(request, 'View All Meetings', table_filter, table, 'Add New Meeting', 'new_meeting')


