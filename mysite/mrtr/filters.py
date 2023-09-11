from .models import *
from django_filters.widgets import RangeWidget, SuffixedMultiWidget
from django import forms
from django.db.models import Q
from functools import reduce
from operator import or_
import datetime
import django_filters as filters


class MasterFilter(filters.FilterSet):
    field_list = []
    search = filters.CharFilter(method='search_fields',
                                label='Search')
    # TODO add 'since' and 'to' as tooltips for date filter
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
        'bed__house__name',
        'door_code',
        'referral_info',
        'notes'
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


class BalanceWidget(SuffixedMultiWidget):
    suffixes = ['min', 'max']

class ResidentBalanceFilter(MasterFilter):
    date = None
    search = None
    balance = filters.RangeFilter(method='balance_filter',
                                  label='Filter by amount',
                                  widget=BalanceWidget(widgets=[forms.NumberInput(attrs={'placeholder': 'Balances above this amount'}),
                                                                forms.NumberInput(attrs={'placeholder': 'Balances below this amount'})
                                                                ]))
    status = filters.ChoiceFilter(method='status_filter',
                                  choices=((1, 'Current'), (0, 'Past')),
                                  empty_label='All',
                                  label='Filter by residency status')
    exclude_zero = filters.BooleanFilter(method='zero_filter',
                                         label='Exclude zero balance',
                                         widget=forms.CheckboxInput)

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
            start = -999999

        stop = value.stop
        if stop is None:
            stop = 999999

        return queryset.filter(balance__range=[start, stop])

    @staticmethod
    def zero_filter(queryset, name, value):
        if value:
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
        'issues',
        'explanation'
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
        'house__name',
        'products',
        'other',
        'trip',
        ]
    status = filters.ChoiceFilter(method='status_filter',
                                  choices=((1, 'Fulfilled'), (0, 'Unfulfilled')),
                                  empty_label='All',
                                  label='Filter by fulfillment status')
    date = filters.DateFromToRangeFilter(method='date_filter',
                                         widget=RangeWidget(attrs={'type': 'date'}),
                                         label='Filter by submission date')

    class Meta:
        model = Supply_request
        fields = ['search', 'date']

    @staticmethod
    def date_filter(queryset, name, value):
        start = value.start
        if start is None:
            start = datetime.datetime(1970, 1, 1)

        stop = value.stop
        if stop is None:
            stop = datetime.datetime.now()

        return queryset.filter(submission_date__range=[start, stop])

    @staticmethod
    def status_filter(queryset, name, value):
        return queryset.filter(fulfilled=bool(int(value)))


class ShoppingTripFilter(MasterFilter):
    product = filters
    field_list = [
        'date',
        'amount',
        'notes',
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


class MaintenanceRequestFilter(MasterFilter):
    field_list = [
        'issue',
        'manager__first_name',
        'manager__last_name',
        'house__name',
        'fulfillment_date',
        'fulfillment_notes',
        'fulfillment_cost'
    ]

    date = filters.DateFromToRangeFilter(method='date_filter',
                                         widget=RangeWidget(attrs={'type': 'date'}),
                                         label='Filter by submission date')
    status = filters.ChoiceFilter(method='status_filter',
                                  choices=((1, 'Fulfilled'), (0, 'Unfulfilled')),
                                  empty_label='All',
                                  label='Filter by fulfillment status')

    class Meta:
        model = Maintenance_request
        fields = ['search', 'date']

    @staticmethod
    def date_filter(queryset, name, value):
        start = value.start
        if start is None:
            start = datetime.datetime(1970, 1, 1)

        stop = value.stop
        if stop is None:
            stop = datetime.datetime.now()

        return queryset.filter(submission_date__range=[start, stop])

    @staticmethod
    def status_filter(queryset, name, value):
        return queryset.filter(fulfilled=bool(int(value)))


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
