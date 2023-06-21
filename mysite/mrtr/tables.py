import django_tables2 as tables
from .models import *


class ResidentTable(tables.Table):
    id = tables.Column(linkify=True)
    first_name = tables.Column(linkify=True)
    last_name = tables.Column(linkify=True)
    


    class Meta:
        model = Resident
        # template_name = "django_tables2/bootstrap.html"
        # fields = ("first_name", )


class TransactionTable(tables.Table):

    class Meta:
        model = Transaction
        fields = ('date', 'amount', 'type', 'method', 'notes')


class HouseTable(tables.Table):
    manager = tables.Column(accessor='manager.full_name')

    class Meta:
        model = House