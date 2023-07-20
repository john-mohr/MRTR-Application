from ..tables import *
from ..filters import *
from .o_views import username
from django.shortcuts import render
from django.db.models.functions import Concat
from django.db.models import Value, Sum, Q
from django_tables2 import RequestConfig


# TODO Implement filter and search functionality


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

    table = TransactionTable(qs, order_by='-submission_date', orderable=True)
    return table_view(request, 'View All Transactions', 'Add New Transaction', 'new_trans', table_filter, table)


def dtests(request):
    qs = Drug_test.objects.all()

    table_filter = DrugTestFilter(request.GET, queryset=qs)

    table = DrugTestTable(qs, order_by='-submission_date', orderable=True)
    return table_view(request, 'View All Drug Tests', 'Add New Drug Test', 'new_dtest', table_filter, table)


def check_ins(request):
    qs = Check_in.objects.all()

    table_filter = CheckInFilter(request.GET, queryset=qs)

    table = CheckInTable(qs, order_by='-submission_date', orderable=True)
    return table_view(request, 'View All Check Ins', 'Add New Check In', 'new_check_in', table_filter, table)


def houses(request):
    qs = House.objects.all()

    table_filter = HouseFilter(request.GET, queryset=qs)

    table = HouseTable(qs, orderable=True)
    return table_view(request, 'View All Houses', 'Add New House', 'new_house', table_filter, table)


def beds(request):
    qs = Bed.objects.all()

    table_filter = BedFilter(request.GET, queryset=qs)

    table = BedTable(qs, exclude=('id',))
    return table_view(request, 'View All Beds', 'Add New Bed', 'beds#', table_filter, table)


def site_visits(request):
    qs = Site_visit.objects.all()

    table_filter = SiteVisitFilter(request.GET, queryset=qs)

    table = SiteVisitTable(qs)
    return table_view(request, 'View All Site Visits', 'Add New Site Visit', 'new_site_visit', table_filter, table)


def house_meetings(request):
    qs = House_meeting.objects.all()

    table_filter = HouseMeetingFilter(request.GET, queryset=qs)

    table = HouseMeetingTable(qs)
    return table_view(request, 'View All House Meetings', 'Add New House Meeting', 'new_house_meeting', table_filter, table)


