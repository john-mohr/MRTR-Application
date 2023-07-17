import django_tables2 as tables
from .models import *
from django_tables2.utils import A
from django.db.models.functions import Concat
from django.db.models import Value, Sum


# TODO:
#  Implement filter and search functionality
#  Make house and bed (?) linkable

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
    full_name = tables.Column(verbose_name='Resident')
    # date = tables.Column(verbose_name='Date of Transaction')

    class Meta:
        model = Transaction
        exclude = ('resident',)
        sequence = ('id', 'submission_date', 'date', 'full_name', 'amount', 'type', 'method')
        # fields = ('date', 'amount', 'type', 'method', 'notes')


class HouseTable(tables.Table):
    name = tables.Column(linkify=True)
    full_name = tables.Column(verbose_name='Manager')
    # full_name = tables.Column(verbose_name='Manager', linkify=('resident', [A('manager_id')]))

    # TODO Prevent linkifying rows where manager is None
    # def before_render(self, request):
    #     print(request)
    #     if self.columns.__getitem__('full_name') is None:
    #         self.columns.__getitem__('full_name').linkify = False
    #     else:
    #         self.columns.__getitem__('full_name').linkify = ('resident', [A('manager_id')])

    class Meta:
        model = House
        sequence = ('name', 'full_name')
        exclude = ('id', 'manager')


class BedTable(tables.Table):
    full_name = tables.Column(verbose_name='Occupant')
    # TODO linkify occupant
    # full_name = tables.Column(verbose_name='Occupant', linkify=('resident', [A('id')]))
    house = tables.Column(accessor='house.name', verbose_name='House')
    name = tables.Column(verbose_name='Bed')

    class Meta:
        model = Bed
        exclude = ('id', 'occupant')
        # fields = ('name', 'house', 'full_name')


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
    full_name = tables.Column(verbose_name='Resident')

    class Meta:
        model = Drug_test
        sequence = ('id', 'full_name',)
        exclude = ('resident', )


class CheckInTable(tables.Table):
    id = tables.Column(verbose_name='Edit', linkify=True)
    r_full_name = tables.Column(verbose_name='Resident')
    m_full_name = tables.Column(verbose_name='Manager')

    class Meta:
        model = Check_in
        sequence = ('id', 'r_full_name', 'm_full_name')
        exclude = ('resident', 'manager')


class SiteVisitTable(tables.Table):
    id = tables.Column(verbose_name='Edit', linkify=True)
    house = tables.Column(accessor='house.name', verbose_name='House')
    full_name = tables.Column(verbose_name='Manager')

    class Meta:
        model = Site_visit
        sequence = ('id', 'date', 'full_name', 'house')
        exclude = ('manager', )


class HouseMeetingTable(tables.Table):
    id = tables.Column(verbose_name='Edit', linkify=True)
    house = tables.Column(accessor='house.name', verbose_name='House')
    full_name = tables.Column(verbose_name='Manager')
    absentees = tables.Column(empty_values=())

    class Meta:
        model = House_meeting
        sequence = ('id', 'date', 'full_name', 'house', 'issues', 'absentees')
        exclude = ('manager', )

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
