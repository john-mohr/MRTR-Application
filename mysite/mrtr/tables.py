import django_tables2 as tables
from .models import *
from django.db.models.functions import Concat
from django.db.models import Value

def get_manager_url(record):
    if record.manager is None:
        return None
    else:
        return record.manager.get_absolute_url()

def get_trip_url(record):
    if record.trip is None:
        return '/portal/current_shopping_trip'
    else:
        return record.trip.get_absolute_url()


def get_row_url(value):
    if str(value)[1:7] == 'portal':
        return value
    elif type(value) == Resident or type(value) == House:
        return value.get_absolute_url()


class CurrencyColumn(tables.Column):
    def render(self, value):
        if value >= 0:
            return f"${value}"
        else:
            return f"-${str(value)[1:]}"


class EditColumn(tables.Column):
    def render(self, value):
        return 'Edit'


# TODO make the other custom columns like this one
class EditColumn2(tables.Column):
    def render(self, value):
        return 'Edit'

    def __init__(self):
        super().__init__(verbose_name='', linkify=True)


class ManagerColumn(tables.Column):
    def render(self, value):
        if value is None:
            value = 'Admin'
        return value


class DateTimeColumn(tables.Column):
    def render(self, value):
        if value is not None:
            value = timezone.localtime(value, timezone=timezone.get_current_timezone())
            return value.strftime('%m/%d/%Y %I:%M %p')


class ResidentsTable(tables.Table):
    first_name = tables.Column(linkify=True)
    last_name = tables.Column(linkify=True)
    house = tables.Column(linkify=True, accessor='bed.house', verbose_name='House')
    balance = CurrencyColumn(accessor=tables.A('balance'))
    rent = CurrencyColumn()
    full_name = tables.Column(linkify=True, verbose_name='Name')
    notes = tables.Column(attrs={'td': {'style': 'min-width: 250px; white-space: pre-wrap'}})
    submission_date = DateTimeColumn()
    last_update = DateTimeColumn()

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

    @staticmethod
    def render_phone(value):
        num = str(value)
        return '(' + num[:3] + ') ' + num[3:6] + '-' + num[6:]


class ShortResidentsTable(tables.Table):
    full_name = tables.Column(linkify=True, verbose_name='Name')
    discharge_date = tables.Column(empty_values=[], verbose_name='Status')
    balance = CurrencyColumn()
    rent = CurrencyColumn()

    class Meta:
        model = Resident
        fields = ('full_name',
                  'balance',
                  'rent',
                  'bed',
                  'door_code',
                  )
        empty_text = 'None'

    @staticmethod
    def render_discharge_date(value):
        if value is None:
            return 'Current'
        else:
            return 'Past'


class TransactionTable(tables.Table):
    id = EditColumn(verbose_name='', linkify=True)
    resident = tables.Column(linkify=True)
    amount = CurrencyColumn()
    notes = tables.Column(attrs={'td': {'style': 'min-width: 200px; white-space: pre-wrap'}})
    submission_date = DateTimeColumn()
    last_update = DateTimeColumn()

    class Meta:
        model = Transaction
        sequence = ('id', 'date', 'resident', 'amount', 'type', 'method', 'notes', 'submission_date')
        empty_text = 'None'


class HouseTable(tables.Table):
    name = tables.Column(linkify=True)
    manager = tables.Column(linkify=True)
    last_update = DateTimeColumn()

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


class DrugTestTable(tables.Table):
    id = EditColumn(verbose_name='', linkify=True)
    resident = tables.Column(linkify=True)
    manager = ManagerColumn(verbose_name='Submitter', linkify=lambda record: get_manager_url(record), empty_values=[])
    substances = tables.Column(attrs={'td': {'style': 'min-width: 200px; white-space: pre-wrap'}})
    submission_date = DateTimeColumn()
    last_update = DateTimeColumn()

    class Meta:
        model = Drug_test
        sequence = ('id', 'date', 'resident', 'result', 'substances', 'notes', 'manager')
        empty_text = 'None'


class CheckInTable(tables.Table):
    id = EditColumn(verbose_name='', linkify=True)
    resident = tables.Column(linkify=True)
    manager = ManagerColumn(verbose_name='Submitter', linkify=lambda record: get_manager_url(record), empty_values=[])
    notes = tables.Column(attrs={'td': {'style': 'min-width: 200px; white-space: pre-wrap'}})
    submission_date = DateTimeColumn()
    last_update = DateTimeColumn()

    class Meta:
        model = Check_in
        sequence = ('id', 'date', 'resident', 'method', 'notes')
        empty_text = 'None'


class SiteVisitTable(tables.Table):
    id = EditColumn(verbose_name='', linkify=True)
    house = tables.Column(linkify=True)
    manager = ManagerColumn(verbose_name='Submitter', linkify=lambda record: get_manager_url(record), empty_values=[])
    issues = tables.Column(attrs={'td': {'style': 'min-width: 300px; white-space: pre-wrap'}})
    explanation = tables.Column(attrs={'td': {'style': 'min-width: 300px; white-space: pre-wrap; text-align: left'}})
    submission_date = DateTimeColumn()
    last_update = DateTimeColumn()

    class Meta:
        model = Site_visit
        sequence = ('id', 'date', 'house', 'issues', 'explanation')
        empty_text = 'None'


class HouseMeetingTable(tables.Table):
    id = EditColumn(verbose_name='', linkify=True)
    house = tables.Column(linkify=True)
    manager = ManagerColumn(verbose_name='Submitter', linkify=lambda record: get_manager_url(record), empty_values=[])
    absentees = tables.Column(empty_values=(), orderable=False, attrs={'td': {'style': 'min-width: 200px; white-space: pre-wrap'}})
    issues = tables.Column(attrs={'td': {'style': 'min-width: 500px; white-space: pre-wrap; text-align: left;'}})
    submission_date = DateTimeColumn()
    last_update = DateTimeColumn()

    class Meta:
        model = House_meeting
        sequence = ('id', 'date', 'house', 'absentees', 'issues')
        empty_text = 'None'

    @staticmethod
    def render_absentees(record):
        absentees = list(Absentee.objects.all().filter(meeting_id=record.pk).select_related('resident').annotate(
            full_name=Concat('resident__first_name', Value(' '), 'resident__last_name')).values_list('full_name', flat=True))
        if len(absentees) != 0:
            return ', '.join(absentees)
        else:
            return '—'


class SupplyRequestTable(tables.Table):
    id = EditColumn2()
    house = tables.Column(linkify=True)
    manager = ManagerColumn(verbose_name='Submitter', linkify=lambda record: get_manager_url(record), empty_values=[])
    products = tables.Column(verbose_name='Products requested',
                             attrs={'td': {'style': 'min-width: 300px; white-space: pre-wrap; text-align: left'}})
    other = tables.Column(verbose_name='Other requests')
    trip = tables.Column(verbose_name='Shopping trip', linkify=lambda record: get_trip_url(record), empty_values=[])
    submission_date = DateTimeColumn()
    last_update = DateTimeColumn()

    class Meta:
        model = Supply_request
        sequence = ('id',
                    'fulfilled',
                    'house',
                    'products',
                    'other',
                    'trip'
                    )

    @staticmethod
    def render_products(value):
        value = value[2:-1].replace("', ", " (Qty: ").replace(", (", ", \n").replace("'", "")
        return value

    @staticmethod
    def render_trip(value, record):
        if value is None:
            value = 'Current'
        else:
            value = record.trip.date.strftime('%m/%d/%Y')
        return value


class SpecialRequestTable(tables.Table):
    house = tables.Column(linkify=True)
    other = tables.Column(verbose_name='Request')

    class Meta:
        model = Supply_request
        fields = ('house',
                  'other',
                  )


class ShoppingListTable(tables.Table):
    product = tables.Column()
    quantity = tables.Column()


class ShoppingTripTable(tables.Table):
    id = tables.Column(verbose_name='', linkify=True)
    amount = CurrencyColumn()
    notes = tables.Column(attrs={'td': {'style': 'min-width: 300px; white-space: pre-wrap; text-align: left'}})
    last_update = DateTimeColumn()

    class Meta:
        model = Shopping_trip
        sequence = ('id',
                    'date',
                    'amount',
                    )

    @staticmethod
    def render_id():
        return 'View'


class MaintenanceRequestTable(tables.Table):
    id = EditColumn(verbose_name='', linkify=True)
    manager = ManagerColumn(verbose_name='Submitter', linkify=lambda record: get_manager_url(record), empty_values=[])
    house = tables.Column(linkify=True)
    fulfillment_cost = CurrencyColumn()
    submission_date = DateTimeColumn()
    last_update = DateTimeColumn()

    class Meta:
        model = Maintenance_request
        sequence = ('id',
                    'fulfilled',
                    'house',
                    'issue',
                    'fulfillment_date',
                    'fulfillment_cost',
                    'fulfillment_notes'
                    )


class RowTable(tables.Table):
    name = tables.Column()
    value = tables.Column(linkify=lambda value: get_row_url(value))

    @staticmethod
    def render_value(value):
        if str(value)[1:7] == 'portal':
            value = 'Click here'
        return value


class ManagerMeetingTable(tables.Table):
    id = EditColumn2()
    submission_date = DateTimeColumn()
    last_update = DateTimeColumn()

    class Meta:
        model = Manager_meeting
        sequence = ('id',
                    'date',
                    'location',
                    'attendees',
                    'ongoing_issues',
                    'new_issues',
                    'minutes_discussed')

    @staticmethod
    def render_attendees(value):
        attendees = Resident.objects.filter(id__in=list(eval(value)))
        attendee_list = list(attendees.annotate(
            full_name=Concat('first_name', Value(' '), 'last_name')
        ).values_list('full_name', flat=True))
        return ', '.join(attendee_list)
