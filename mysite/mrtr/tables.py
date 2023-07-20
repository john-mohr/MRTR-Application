import django_tables2 as tables
from .models import *
from django_tables2.utils import A
from django.db.models.functions import Concat
from django.db.models import Value, Sum


class ResidentsTable(tables.Table):
    first_name = tables.Column(linkify=True)
    last_name = tables.Column(linkify=True)
    bed_obj = tables.RelatedLinkColumn()
    bed = tables.Column(accessor='bed.name', verbose_name='Bed')
    house = tables.Column(accessor='bed.house.name', verbose_name='House')
    balance = tables.Column(accessor=tables.A('balance'))

    class Meta:
        model = Resident
        sequence = ('submission_date',
                    'first_name',
                    'last_name',
                    'balance',
                    'phone',
                    'email',
                    'rent',
                    'bed',
                    'house',
                    'door_code',
                    'admit_date',
                    'discharge_date',
                    )
        exclude = ('id', 'bed_obj', )


class ResidentBalanceTable(tables.Table):
    full_name = tables.Column(linkify=True, verbose_name='Name')

    class Meta:
        model = Resident
        fields = ('full_name', 'balance',)


class TransactionTable(tables.Table):
    id = tables.Column(verbose_name='Edit', linkify=True)
    submission_date = tables.Column(linkify=True)
    resident = tables.Column(linkify=True)

    class Meta:
        model = Transaction
        sequence = ('id', 'submission_date', 'date', 'resident', 'amount', 'type', 'method')


class HouseTable(tables.Table):
    name = tables.Column(linkify=True)
    manager = tables.Column(linkify=True)

    class Meta:
        model = House
        sequence = ('name', 'manager')
        exclude = ('id',)


class BedTable(tables.Table):
    resident = tables.Column(linkify=True, verbose_name='Occupant')
    house = tables.Column(accessor='house.name', verbose_name='House')
    name = tables.Column(verbose_name='Bed')

    class Meta:
        model = Bed
        exclude = ('id', 'occupant')


class ManagerMeetingTable(tables.Table):
    title = tables.Column(linkify=True)

    class Meta:
        model = Manager_meeting
        sequence = ('title',
                    'date',
                    'location',
                    'submission_date',
                    'last_update',
                    'attendee',
                    )
        exclude = ('issues','id' )


class DrugTestTable(tables.Table):
    id = tables.Column(verbose_name='Edit', linkify=True)
    resident = tables.Column(linkify=True)

    class Meta:
        model = Drug_test
        sequence = ('id', 'resident',)


class CheckInTable(tables.Table):
    id = tables.Column(verbose_name='Edit', linkify=True)
    resident = tables.Column(linkify=True)
    manager = tables.Column(linkify=True)

    class Meta:
        model = Check_in
        sequence = ('id', 'resident', 'manager')


class SiteVisitTable(tables.Table):
    id = tables.Column(verbose_name='Edit', linkify=True)
    house = tables.Column(linkify=True)
    manager = tables.Column(linkify=True)

    class Meta:
        model = Site_visit
        sequence = ('id', 'date', 'manager', 'house')


class HouseMeetingTable(tables.Table):
    id = tables.Column(verbose_name='Edit', linkify=True)
    house = tables.Column(linkify=True)
    manager = tables.Column(linkify=True)
    absentees = tables.Column(empty_values=())

    class Meta:
        model = House_meeting
        sequence = ('id', 'date', 'manager', 'house', 'issues', 'absentees')

    def render_absentees(self, record):
        absentees = list(Absentee.objects.all().filter(meeting_id=record.pk).select_related('resident').annotate(
            full_name=Concat('resident__first_name', Value(' '), 'resident__last_name')).values_list('full_name', flat=True))
        return ', '.join(absentees)


class SupplyRequestTable(tables.Table):
    id = tables.Column(linkify=True)

    class Meta:
        model = Supply_request
        sequence = ('id',
                    'fulfilled',
                    'date',
                    'product',
                    'quantity',
                    'notes',
                    'house',
                    'trip',
                    )

class ShoppingTripTable(tables.Table):
    id = tables.Column(linkify=True)

    class Meta:
        model = Shopping_trip
        sequence = ('id',
                    'date',
                    'amount',
                    )
