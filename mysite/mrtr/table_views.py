from .tables import *
from .views import username
from django.shortcuts import render, redirect
from django.db.models.functions import Concat
from django.db.models import Value, Sum
from django_tables2 import RequestConfig


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
    qs = Transaction.objects.all().select_related('resident').annotate(
        full_name=Concat('resident__first_name', Value(' '), 'resident__last_name'))

    table = TransactionTable(qs, order_by='-submission_date', orderable=True)
    return table_view(request, 'View All Transactions', 'Add New Transaction', 'new_trans', table)


def dtests(request):
    qs = Drug_test.objects.all().select_related('resident').annotate(
        full_name=Concat('resident__first_name', Value(' '), 'resident__last_name'))

    table = DrugTestTable(qs, order_by='-submission_date', orderable=True)
    return table_view(request, 'View All Drug Tests', 'Add New Drug Test', 'new_dtest', table)


def check_ins(request):
    qs = Check_in.objects.all().select_related('resident').select_related('manager').annotate(
        r_full_name=Concat('resident__first_name', Value(' '), 'resident__last_name'),
        m_full_name=Concat('manager__first_name', Value(' '), 'manager__last_name'))

    table = CheckInTable(qs, order_by='-submission_date', orderable=True)
    return table_view(request, 'View All Check Ins', 'Add New Check In', 'new_check_in', table)


def houses(request):
    qs = House.objects.all().select_related('manager').annotate(
        full_name=Concat('manager__first_name', Value(' '), 'manager__last_name'))

    table = HouseTable(qs, orderable=True)
    return table_view(request, 'View All Houses', 'Add New House', 'new_house', table)


def beds(request):
    qs = Bed.objects.all().select_related('resident').annotate(
        full_name=Concat('resident__first_name', Value(' '), 'resident__last_name'))

    table = BedTable(qs, exclude=('id',))
    return table_view(request, 'View All Beds', 'Add New Bed', 'beds#', table)

