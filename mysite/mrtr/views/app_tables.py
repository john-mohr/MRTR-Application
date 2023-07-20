from ..tables import *
from .o_views import username
from django.shortcuts import render
from django.db.models.functions import Concat
from django.db.models import Value, Sum
from django_tables2 import RequestConfig


# TODO Make tables sortable
# https://django-tables2.readthedocs.io/en/latest/pages/filtering.html


def table_view(request, page_name, button_name, button_link, table):
    fullname = username(request)
    page = page_name
    table = table
    RequestConfig(request).configure(table)
    button_name = button_name
    button_link = '/portal/' + button_link
    return render(request, 'admin/temp_tables.html', locals())


def residents(request):
    qs = Resident.objects.annotate(
        balance=Sum('transaction__amount'))

    table = ResidentsTable(qs, order_by='-submission_date', orderable=True, exclude='full_name')
    return table_view(request, 'View All Residents', 'Add New Resident', 'new_res', table)


def transactions(request):
    qs = Transaction.objects.all().select_related('resident')

    table = TransactionTable(qs, order_by='-submission_date', orderable=True)
    return table_view(request, 'View All Transactions', 'Add New Transaction', 'new_trans', table)


def dtests(request):
    qs = Drug_test.objects.all()

    table = DrugTestTable(qs, order_by='-submission_date', orderable=True)
    return table_view(request, 'View All Drug Tests', 'Add New Drug Test', 'new_dtest', table)


def check_ins(request):
    qs = Check_in.objects.all()

    table = CheckInTable(qs, order_by='-submission_date', orderable=True)
    return table_view(request, 'View All Check Ins', 'Add New Check In', 'new_check_in', table)


def houses(request):
    qs = House.objects.all()

    table = HouseTable(qs, orderable=True)
    return table_view(request, 'View All Houses', 'Add New House', 'new_house', table)


def beds(request):
    qs = Bed.objects.all()

    table = BedTable(qs, exclude=('id',))
    return table_view(request, 'View All Beds', 'Add New Bed', 'beds#', table)


def site_visits(request):
    qs = Site_visit.objects.all()

    table = SiteVisitTable(qs)
    return table_view(request, 'View All Site Visits', 'Add New Site Visit', 'new_site_visit', table)


def house_meetings(request):
    qs = House_meeting.objects.all()

    table = HouseMeetingTable(qs)
    return table_view(request, 'View All House Meetings', 'Add New House Meeting', 'new_house_meeting', table)


