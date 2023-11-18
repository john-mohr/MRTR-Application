from .models import *
from django_filters.widgets import SuffixedMultiWidget
from django import forms
from django.db.models import Q
import django_filters as filters
from functools import reduce
from operator import or_


class CustomWidget(SuffixedMultiWidget):
    suffixes = ['min', 'max']


class MasterFilter(filters.FilterSet):
    field_list = []
    house_access = True
    search = filters.CharFilter(method='search_fields',
                                label='Search')
    house = filters.ModelChoiceFilter(method='house_filter',
                                      label='Filter by house',
                                      queryset=House.objects.all())
    date = filters.DateFromToRangeFilter(label='Filter by date',
                                         widget=CustomWidget(widgets=[
                                             forms.TextInput(attrs={'type': 'text',
                                                                    'placeholder': 'From',
                                                                    'onfocus': "(this.type='date')",
                                                                    'onblur': "(this.type='text')"}),
                                             forms.TextInput(attrs={'type': 'text',
                                                                    'placeholder': 'To',
                                                                    'onfocus': "(this.type='date')",
                                                                    'onblur': "(this.type='text')"})
                                         ]))

    class Meta:
        abstract = True

    def search_fields(self, queryset, name, value):
        q = reduce(or_, [Q(**{f'{f}__icontains': value}) for f in self.field_list], Q())
        return queryset.filter(q)

    def house_filter(self, queryset, name, value):
        if self.house_access:
            return queryset.filter(house=value)
        else:
            return queryset.filter(resident__bed__house=value)

    @staticmethod
    def res_status_filter(queryset, name, value):
        return queryset.filter(discharge_date__isnull=bool(int(value)))


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
    status = filters.ChoiceFilter(method='res_status_filter',
                                  choices=((1, 'Current'), (0, 'Past')),
                                  empty_label='All',
                                  label='Filter by residency status')

    def house_filter(self, queryset, name, value):
        return queryset.filter(bed__house=value)


class ResidentBalanceFilter(MasterFilter):
    search = None
    house = None
    date = None

    balance = filters.RangeFilter(label='Filter by amount',
                                  widget=CustomWidget(widgets=[
                                      forms.NumberInput(attrs={'placeholder': 'Balances above this amount'}),
                                      forms.NumberInput(attrs={'placeholder': 'Balances below this amount'})
                                  ]))
    status = filters.ChoiceFilter(method='res_status_filter',
                                  choices=((1, 'Current'), (0, 'Past')),
                                  empty_label='All',
                                  label='Filter by residency status')
    exclude_zero = filters.BooleanFilter(method='zero_filter',
                                         label='Exclude zero balance',
                                         widget=forms.CheckboxInput)

    @staticmethod
    def zero_filter(queryset, name, value):
        if value:
            queryset = queryset.exclude(balance=0)
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
    house_access = False


class DrugTestFilter(MasterFilter):
    field_list = [
        'resident__first_name',
        'resident__last_name',
        'manager__first_name',
        'manager__last_name',
        'result',
        'substances',
        'notes'
    ]
    house_access = False


class CheckInFilter(MasterFilter):
    field_list = [
        'resident__first_name',
        'resident__last_name',
        'manager__first_name',
        'manager__last_name',
        'method',
        'notes'
    ]
    house_access = False


class SiteVisitFilter(MasterFilter):
    field_list = [
        'manager__first_name',
        'manager__last_name',
        'house__name',
        'issues',
        'explanation'
    ]


class SupplyRequestFilter(MasterFilter):
    field_list = [
        'house__name',
        'manager__first_name',
        'manager__last_name',
        'products',
        'other',
        'trip__date',
        ]
    date = None
    submission_date = filters.DateFromToRangeFilter(label='Filter by submission date',
                                                    widget=CustomWidget(widgets=[
                                                        forms.TextInput(attrs={'type': 'text',
                                                                               'placeholder': 'From',
                                                                               'onfocus': "(this.type='date')",
                                                                               'onblur': "(this.type='text')"}),
                                                        forms.TextInput(attrs={'type': 'text',
                                                                               'placeholder': 'To',
                                                                               'onfocus': "(this.type='date')",
                                                                               'onblur': "(this.type='text')"})
                                                    ]))
    fulfilled = filters.ChoiceFilter(choices=((1, 'Fulfilled'), (0, 'Unfulfilled')),
                                     empty_label='All',
                                     label='Filter by fulfillment status')


class ShoppingTripFilter(MasterFilter):
    field_list = [
        'date',
        'amount',
        'notes',
    ]
    house = None


class HouseMeetingFilter(MasterFilter):
    field_list = [
        'manager__first_name',
        'manager__last_name',
        'house__name',
        'issues',
        'absentee__resident__first_name',
        'absentee__resident__last_name'
    ]


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
    date = None
    submission_date = filters.DateFromToRangeFilter(label='Filter by submission date',
                                                    widget=CustomWidget(widgets=[
                                                        forms.TextInput(attrs={'type': 'text',
                                                                               'placeholder': 'From',
                                                                               'onfocus': "(this.type='date')",
                                                                               'onblur': "(this.type='text')"}),
                                                        forms.TextInput(attrs={'type': 'text',
                                                                               'placeholder': 'To',
                                                                               'onfocus': "(this.type='date')",
                                                                               'onblur': "(this.type='text')"})
                                                    ]))
    fulfilled = filters.ChoiceFilter(choices=((1, 'Fulfilled'), (0, 'Unfulfilled')),
                                     empty_label='All',
                                     label='Filter by fulfillment status')


class HouseFilter(MasterFilter):
    field_list = [
        'name',
        'manager__first_name',
        'manager__last_name',
        'address',
        'city',
        'state'
    ]
    house = None
    date = None


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

    @staticmethod
    def occupied_filter(queryset, name, value):
        return queryset.filter(resident__isnull=bool(int(value)))


class ManagerMeetingFilter(MasterFilter):
    field_list = [
        'date',
        'location',
        'attendees',
        'ongoing_issues',
        'new_issues'
    ]
    house = None
