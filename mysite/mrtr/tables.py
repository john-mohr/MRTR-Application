import django_tables2 as tables
# from django_tables2
from .models import *


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

    class Meta:
        model = Transaction
        fields = ('date', 'amount', 'type', 'method', 'notes')


class HouseTable(tables.Table):
    name = tables.Column(linkify=True)
    manager = tables.Column(accessor='manager.full_name')

    class Meta:
        model = House
        exclude = ('id',)


class BedTable(tables.Table):
    occupant = tables.Column(accessor='resident.full_name', verbose_name='Occupant')
    house = tables.Column(accessor='house.name', verbose_name='House')
    name = tables.Column(verbose_name='Bed')

    class Meta:
        model = Bed
        # fields = ('house', 'name')
