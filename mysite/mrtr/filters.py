from .models import *
from django_filters.widgets import RangeWidget
from django.db.models import Q
from functools import reduce
from operator import or_
import datetime
import django_filters as filters


class MasterFilter(filters.FilterSet):
    field_list = []
    search = filters.CharFilter(method='search_fields',
                                label='Search')
    date = filters.DateFromToRangeFilter(method='date_filter',
                                         widget=RangeWidget(attrs={'type': 'date'}),
                                         label='Filter by date')

    class Meta:
        abstract = True

    def search_fields(self, queryset, name, value):
        q = reduce(or_, [Q(**{f'{f}__icontains': value}) for f in self.field_list], Q())
        return queryset.filter(q)

    @staticmethod
    def date_filter(queryset, name, value):
        start = value.start
        if start is None:
            start = datetime.datetime(1970, 1, 1)

        stop = value.stop
        if stop is None:
            stop = datetime.datetime.now()

        return queryset.filter(date__range=[start, stop])


class ResidentFilter(MasterFilter):
    field_list = [
        'first_name',
        'last_name',
        'phone',
        'email',
        'bed__name',
        'bed__house__name'
    ]

    date = None
    status = filters.ChoiceFilter(method='status_filter',
                                  choices=((1, 'Current'), (0, 'Past')),
                                  empty_label='All',
                                  label='Filter by residency status')

    class Meta:
        model = Resident
        fields = ['search', 'status']

    @staticmethod
    def status_filter(queryset, name, value):
        return queryset.filter(discharge_date__isnull=bool(int(value)))


# TODO This filter needs some work
class ResidentBalanceFilter(MasterFilter):
    date = None
    search = None
    balance = filters.RangeFilter(method='balance_filter',
                                  label='Filter by balance')

    status = filters.ChoiceFilter(method='status_filter',
                                  choices=((1, 'Current'), (0, 'Past')),
                                  empty_label='All',
                                  label='Filter by residency status')
    exclude_zero = filters.BooleanFilter(method='zero_filter',
                                         label='Exclude zero balance')

    class Meta:
        model = Resident
        fields = ['balance', 'status']

    @staticmethod
    def status_filter(queryset, name, value):
        return queryset.filter(discharge_date__isnull=bool(int(value)))

    @staticmethod
    def balance_filter(queryset, name, value):
        start = value.start
        if start is None:
            start = -10000

        stop = value.stop
        if stop is None:
            stop = 10000

        return queryset.filter(balance__range=[start, stop])

    @staticmethod
    def zero_filter(queryset, name, value):
        if value is True:
            return queryset.exclude(balance=0)
        else:
            return queryset




class TransactionFilter(MasterFilter):
    field_list = [
        'resident__first_name',
        'resident__last_name',
        'amount',
        'type',
        'method',
        'notes'
        ]

    class Meta:
        model = Transaction
        fields = ['search', 'date']


class DrugTestFilter(MasterFilter):
    field_list = [
        'resident__first_name',
        'resident__last_name',
        'result',
        'substances',
        'notes'
    ]

    class Meta:
        model = Drug_test
        fields = ['search', 'date']


class CheckInFilter(MasterFilter):
    field_list = [
        'resident__first_name',
        'resident__last_name',
        'manager__first_name',
        'manager__last_name',
        'method',
        'notes'
    ]

    class Meta:
        model = Check_in
        fields = ['search', 'date']


class SiteVisitFilter(MasterFilter):
    field_list = [
        'manager__first_name',
        'manager__last_name',
        'house__name',
        'issues'
    ]

    class Meta:
        model = Site_visit
        fields = ['search', 'date']


class ManagerMeetingFilter(MasterFilter):
    field_list = [
            'title',
            'date',
            'location',
            'submission_date',
            'last_update',
            'attendee',
        ]

    class Meta:
        model = Manager_meeting
        fields = ['search', 'date']


class SupplyRequestFilter(MasterFilter):
    field_list = [
          'id',
          'fulfilled',
          'date',
          'product',
          'quantity',
          'notes',
          'house',
          'trip',
        ]

    class Meta:
        model = Supply_request
        fields = ['search', 'date']


class ShoppingTripFilter(MasterFilter):
    field_list = [
          'id',
          'date',
          'amount',
        ]

    class Meta:
        model = Supply_request
        fields = ['search', 'date']


class HouseMeetingFilter(MasterFilter):
    field_list = [
        'manager__first_name',
        'manager__last_name',
        'house__name',
        'issues',
        'absentee__resident__first_name',
        'absentee__resident__last_name'
    ]

    class Meta:
        model = House_meeting
        fields = ['search', 'date']


class HouseFilter(MasterFilter):
    field_list = [
        'name',
        'manager__first_name',
        'manager__last_name',
        'address',
        'city',
        'state'
    ]
    date = None

    class Meta:
        model = House
        fields = ['search', ]


class BedFilter(MasterFilter):
    field_list = [
        'name',
        'house__name'
    ]

    date = None
    occupied = filters.ChoiceFilter(method='occupied_filter',
                                    choices=((1, 'Vacant'), (0, 'Occupied')),
                                    empty_label='All',
                                    label='Filter by occupancy status')

    class Meta:
        model = Bed
        fields = ['search', 'occupied']

    @staticmethod
    def occupied_filter(queryset, name, value):
        return queryset.filter(resident__isnull=bool(int(value)))
