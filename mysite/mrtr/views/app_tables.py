from ..tables import *
from ..filters import *
from .o_views import username
from django.shortcuts import render
from django.db.models.functions import Concat
from django.db.models import Value, Sum, Q
from django_tables2 import RequestConfig


def table_view(request, page_name, button_name, button_link, table_filter, table):
    fullname = username(request)
    page = page_name
    table_filter = table_filter
    table = table
    RequestConfig(request).configure(table)
    button_name = button_name
    button_link = '/portal/' + button_link
    return render(request, 'admin/temp_tables.html', locals())


def residents(request):
    qs = Resident.objects.annotate(
        balance=Sum('transaction__amount'))

    table_filter = ResidentFilter(request.GET, queryset=qs)

    table = ResidentsTable(table_filter.qs, order_by='-submission_date', orderable=True, exclude='full_name')
    return table_view(request, 'View All Residents', 'Add New Resident', 'new_res', table_filter, table)


def transactions(request):
    qs = Transaction.objects.all().select_related('resident')

    table_filter = TransactionFilter(request.GET, queryset=qs)

    table = TransactionTable(table_filter.qs, order_by='-submission_date', orderable=True)
    return table_view(request, 'View All Transactions', 'Add New Transaction', 'new_trans', table_filter, table)


def dtests(request):
    qs = Drug_test.objects.all()

    table_filter = DrugTestFilter(request.GET, queryset=qs)

    table = DrugTestTable(table_filter.qs, order_by='-submission_date', orderable=True)
    return table_view(request, 'View All Drug Tests', 'Add New Drug Test', 'new_dtest', table_filter, table)


def check_ins(request):
    qs = Check_in.objects.all()

    table_filter = CheckInFilter(request.GET, queryset=qs)

    table = CheckInTable(table_filter.qs, order_by='-submission_date', orderable=True)
    return table_view(request, 'View All Check Ins', 'Add New Check In', 'new_check_in', table_filter, table)


def houses(request):
    qs = House.objects.all()

    table_filter = HouseFilter(request.GET, queryset=qs)

    table = HouseTable(table_filter.qs, orderable=True)
    return table_view(request, 'View All Houses', 'Add New House', 'new_house', table_filter, table)


def beds(request):
    qs = Bed.objects.all()

    table_filter = BedFilter(request.GET, queryset=qs)

    table = BedTable(table_filter.qs, exclude=('id',))
    return table_view(request, 'View All Beds', 'Add New Bed', 'beds#', table_filter, table)


def site_visits(request):
    qs = Site_visit.objects.all()

    table_filter = SiteVisitFilter(request.GET, queryset=qs)

    table = SiteVisitTable(table_filter.qs)
    return table_view(request, 'View All Site Visits', 'Add New Site Visit', 'new_site_visit', table_filter, table)


def house_meetings(request):
    qs = House_meeting.objects.all()

    table_filter = HouseMeetingFilter(request.GET, queryset=qs)

    table = HouseMeetingTable(table_filter.qs)
    return table_view(request, 'View All House Meetings', 'Add New House Meeting', 'new_house_meeting', table_filter, table)


def meetings(request):
    qs = Manager_meeting.objects.all()

    table_filter = ManagerMeetingFilter(request.GET, queryset=qs)

    table = ManagerMeetingTable(table_filter.qs)
    return table_view(request, 'View All Meetings', 'Add New Meeting', 'new_meeting', table_filter, table)


def supply_requests(request):
    qs = Supply_request.objects.all()

    table_filter = SupplyRequestFilter(request.GET, queryset=qs)

    table = SupplyRequestTable(table_filter.qs)
    return table_view(request, 'View All Supply Requests', 'Add New Supply Request', 'new_supply_request', table_filter, table)


def shopping_trips(request):
    qs = Shopping_trip.objects.all()

    table_filter = ShoppingTripFilter(request.GET, queryset=qs)

    table = ShoppingTripTable(table_filter.qs)
    return table_view(request, 'View All Shopping Trips', 'Add New Shopping Trip', 'new_shopping_trip', table_filter, table)

