import django_tables2 as tables
from .models import *
from django.db.models.functions import Concat
from django.db.models import Value, Sum

# TODO change datetime format to .strftime('%m/%d/%Y %I:%M %p')

class ResidentsTable(tables.Table):
    first_name = tables.Column(linkify=True)
    last_name = tables.Column(linkify=True)
    house = tables.Column(linkify=True, accessor='bed.house', verbose_name='House')
    balance = tables.Column(accessor=tables.A('balance'))
    full_name = tables.Column(linkify=True, verbose_name='Name')
    notes = tables.Column(attrs={'td': {'style': 'min-width: 250px; white-space: pre-wrap'}})

    class Meta:
        model = Resident
        sequence = ('full_name',
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
                    'referral_info',
                    'notes',
                    )
        exclude = ('id', )
        empty_text = 'None'

    def render_balance(self, value):
        if value >= 0:
            return f"${value}"
        else:
            return f"-${str(value)[1:]}"

    def render_rent(self, value):
        return f"${value}"

    def render_phone(self, value):
        num = str(value)
        return '(' + num[:3] + ') ' + num[3:6] + '-' + num[6:]


class ShortResidentsTable(tables.Table):
    full_name = tables.Column(linkify=True, verbose_name='Name')
    discharge_date = tables.Column(empty_values=[], verbose_name='Status')

    class Meta:
        model = Resident
        fields = ('full_name',
                  'balance',
                  'rent',
                  'bed',
                  'door_code',
                  )
        empty_text = 'None'

    def render_balance(self, value):
        if value >= 0:
            return f"${value}"
        else:
            return f"-${str(value)[1:]}"

    def render_rent(self, value):
        return f"${value}"

    def render_discharge_date(self, value):
        if value is None:
            return 'Current'
        else:
            return 'Past'


class TransactionTable(tables.Table):
    id = tables.Column(verbose_name='', linkify=True)
    resident = tables.Column(linkify=True)
    notes = tables.Column(attrs={'td': {'style': 'min-width: 200px; white-space: pre-wrap'}})

    class Meta:
        model = Transaction
        sequence = ('id', 'date', 'resident', 'amount', 'type', 'method', 'notes', 'submission_date')
        empty_text = 'None'

    def render_id(self, value):
        return f"Edit"

    def render_amount(self, value):
        if value >= 0:
            return f"${value}"
        else:
            return f"-${str(value)[1:]}"


class HouseTable(tables.Table):
    name = tables.Column(linkify=True)
    manager = tables.Column(linkify=True)

    class Meta:
        model = House
        sequence = ('name', 'manager')
        exclude = ('id',)
        empty_text = 'None'


class BedTable(tables.Table):
    resident = tables.Column(linkify=True, verbose_name='Occupant')
    house = tables.Column(linkify=True, verbose_name='House')
    name = tables.Column(verbose_name='Bed')

    class Meta:
        model = Bed
        exclude = ('id', 'occupant')
        empty_text = 'None'


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
    id = tables.Column(verbose_name='', linkify=True)
    resident = tables.Column(linkify=True)
    substances = tables.Column(attrs={'td': {'style': 'min-width: 200px; white-space: pre-wrap'}})

    class Meta:
        model = Drug_test
        sequence = ('id', 'resident',)
        empty_text = 'None'

    def render_id(self, value):
        return f"Edit"


def get_url(record):
    if record.manager is None:
        return None
    else:
        return record.manager.get_absolute_url()

class CheckInTable(tables.Table):
    id = tables.Column(verbose_name='', linkify=True)
    resident = tables.Column(linkify=True)
    manager = tables.Column(verbose_name='Submitter', linkify=lambda record: get_url(record), empty_values=[])
    notes = tables.Column(attrs={'td': {'style': 'min-width: 200px; white-space: pre-wrap'}})


    class Meta:
        model = Check_in
        sequence = ('id', 'resident', 'manager')
        empty_text = 'None'

    def render_id(self, value):
        return f"Edit"

    def render_manager(self, value):
        if value is None:
            value = 'Admin'
        return value


class SiteVisitTable(tables.Table):
    id = tables.Column(verbose_name='', linkify=True)
    house = tables.Column(linkify=True)
    manager = tables.Column(verbose_name='Submitter', linkify=lambda record: get_url(record), empty_values=[])
    issues = tables.Column(attrs={'td': {'style': 'min-width: 300px; white-space: pre-wrap'}})
    explanation = tables.Column(attrs={'td': {'style': 'min-width: 300px; white-space: pre-wrap; text-align: left'}})

    class Meta:
        model = Site_visit
        sequence = ('id', 'date', 'manager', 'house')
        empty_text = 'None'

    def render_id(self, value):
        return f"Edit"

    def render_manager(self, value):
        if value is None:
            value = 'Admin'
        return value


class HouseMeetingTable(tables.Table):
    id = tables.Column(verbose_name='', linkify=True)
    house = tables.Column(linkify=True)
    manager = tables.Column(verbose_name='Submitter', linkify=lambda record: get_url(record), empty_values=[])
    absentees = tables.Column(empty_values=(), orderable=False, attrs={'td': {'style': 'min-width: 200px; white-space: pre-wrap'}})
    issues = tables.Column(attrs={'td': {'style': 'min-width: 600px; white-space: pre-wrap; text-align: left;'}})

    class Meta:
        model = House_meeting
        sequence = ('id', 'date', 'manager', 'house', 'absentees', 'issues')
        empty_text = 'None'

    @staticmethod
    def render_absentees(record):
        absentees = list(Absentee.objects.all().filter(meeting_id=record.pk).select_related('resident').annotate(
            full_name=Concat('resident__first_name', Value(' '), 'resident__last_name')).values_list('full_name', flat=True))
        return ', '.join(absentees)

    def render_id(self, value):
        return f"Edit"

    def render_manager(self, value):
        if value is None:
            value = 'Admin'
        return value


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
                    # 'trip',
                    )

class ShoppingTripTable(tables.Table):
    id = tables.Column(linkify=True)

    class Meta:
        model = Shopping_trip
        sequence = ('id',
                    'date',
                    'amount',
                    )

def RowTableLink(value):
    if str(value)[1:7] == 'portal':
        return value
    elif type(value) == Resident or type(value) == House:
        return value.get_absolute_url()


class RowTable(tables.Table):
    name = tables.Column()
    value = tables.Column(linkify=lambda value: RowTableLink(value))

    def render_value(self, value):
        if str(value)[1:7] == 'portal':
            value = 'Click here'
        return value

