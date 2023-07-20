import django_filters as filters
from .models import *
from django import forms
from django.db.models import Q

# TODO Implement filter and search functionality


class ResidentFilter(filters.FilterSet):
    search = filters.CharFilter(method='search_all',
                                label='Search')
    status = filters.ChoiceFilter(method='status_filter',
                                  choices=((1, 'Current'), (0, 'Past')),
                                  empty_label='All',
                                  label='Filter by residency status')
    # house = filters.ModelMultipleChoiceFilter(queryset=House.objects.all(),
    #                                           method='house_filter',
    #                                           widget=forms.CheckboxSelectMultiple,
    #                                           label='Filter by house')

    class Meta:
        model = Resident
        fields = [
            'search',
            'status',
            # 'house'
        ]

    def search_all(self, queryset, name, value):
        return queryset.filter(
            Q(first_name__icontains=value) |
            Q(last_name__icontains=value) |
            Q(phone__icontains=value) |
            Q(email__icontains=value) |
            Q(bed__name__icontains=value)
        )

    def status_filter(self, queryset, name, value):
        return queryset.filter(
            discharge_date__isnull=bool(int(value))
        )

    # def house_filter(self, queryset, name, value):
    #     if len(value) == 0:
    #         return queryset
    #     else:
    #         house_residents = Bed.objects.exclude(resident=None).filter(house__in=value).distinct()
    #         return queryset.filter(
    #             pk__in=house_residents.values_list('resident', flat=True)
    #         )


class TransactionFilter(filters.FilterSet):
    class Meta:
        model = Resident
        fields = [
            # 'search',
            'id'
            # 'status',
            # 'house'
        ]


class DrugTestFilter(filters.FilterSet):
    class Meta:
        model = Resident
        fields = [
            # 'search',
            'id'
            # 'status',
            # 'house'
        ]


class CheckInFilter(filters.FilterSet):
    class Meta:
        model = Resident
        fields = [
            # 'search',
            'id'
            # 'status',
            # 'house'
        ]


class HouseFilter(filters.FilterSet):
    class Meta:
        model = Resident
        fields = [
            # 'search',
            'id'
            # 'status',
            # 'house'
        ]


class BedFilter(filters.FilterSet):
    class Meta:
        model = Resident
        fields = [
            # 'search',
            'id'
            # 'status',
            # 'house'
        ]


class SiteVisitFilter(filters.FilterSet):
    class Meta:
        model = Resident
        fields = [
            # 'search',
            'id'
            # 'status',
            # 'house'
        ]


class HouseMeetingFilter(filters.FilterSet):
    class Meta:
        model = Resident
        fields = [
            # 'search',
            'id'
            # 'status',
            # 'house'
        ]
