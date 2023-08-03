from django import forms
from .models import *
from django.core.validators import MaxValueValidator
from django.contrib.auth.forms import UserCreationForm


class ContactForm(forms.Form):
    email = forms.EmailField()
    first_name = forms.CharField(label= 'First Name', max_length = 20)
    last_name = forms.CharField(label= 'Last Name', max_length = 20)
    message = forms.CharField(widget = forms.Textarea, max_length = 2000)


class DateInput(forms.DateInput):
    input_type = 'date'


class BedField(forms.ModelChoiceField):
    def label_from_instance(self, bed):
        label = f"{bed.name}"
        return label


class ResidentForm(forms.ModelForm):
    phone = forms.IntegerField(validators=[MaxValueValidator(9999999999)], required=False)
    email = forms.EmailField(max_length=62, required=False)
    door_code = forms.IntegerField(validators=[MaxValueValidator(9999)], required=False)
    referral_info = forms.CharField(required=False)
    notes = forms.CharField(widget=forms.Textarea, required=False)
    occupied_beds = Resident.objects.all().filter(bed_id__isnull=False).distinct()
    bed = BedField(queryset=Bed.objects.exclude(id__in=occupied_beds.values_list('bed_id', flat=True)))
    effective_date = forms.DateField(widget=DateInput(), initial=timezone.now)  # for edit_res only

    # Allows selection of resident's current bed and removes rent field for editing
    def __init__(self, *args, **kwargs):
        super(ResidentForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:  # edit and readmit
            res = kwargs.pop('instance')
            if res.discharge_date is None:  # edit
                edit_beds = self.occupied_beds.exclude(pk=res.pk)
                self.fields['bed'].queryset = Bed.objects.exclude(id__in=edit_beds.values_list('bed_id', flat=True))
            else:  # readmit
                self.fields['admit_date'].label = 'Readmission date'
                del self.fields['effective_date']
        else:  # new
            del self.fields['effective_date']

    class Meta:
        model = Resident
        fields = ['effective_date',  # for edit_res only
                  'first_name',
                  'last_name',
                  'phone',
                  'email',
                  'admit_date',
                  'bed',
                  'rent',
                  'door_code',
                  'referral_info',
                  'notes',
                  ]
        widgets = {
            'admit_date': DateInput(),
        }


class DischargeResForm(forms.Form):
    date = forms.DateField(widget=DateInput(), initial=timezone.now)
    reason = forms.CharField(widget=forms.Textarea, required=False)


class ResidentField(forms.ModelChoiceField):
    def label_from_instance(self, resident):
        label = resident.first_name + " " + resident.last_name
        return label


class TransactionForm(forms.ModelForm):
    type = forms.ChoiceField(choices=Transaction.TYPE_CHOICES[5:])
    resident = ResidentField(queryset=Resident.objects.all())
    notes = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = Transaction
        fields = ['resident',
                  'date',
                  'type',
                  'amount',
                  'notes',
                  ]
        widgets = {
            'date': DateInput(),
        }


class RentPaymentForm(forms.ModelForm):
    method = forms.ChoiceField(choices=Transaction.METHOD_CHOICES, required=False)
    resident = ResidentField(queryset=Resident.objects.all())
    notes = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = Transaction
        fields = ['resident',
                  'date',
                  'amount',
                  'method',
                  'notes',
                  ]
        widgets = {
            'date': DateInput(),
        }


class AdjustBalanceForm(forms.ModelForm):
    # method = forms.ChoiceField(choices=Transaction.METHOD_CHOICES, required=False)
    resident = ResidentField(queryset=Resident.objects.all())
    notes = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = Transaction
        fields = ['resident',
                  'date',
                  'amount',
                  # 'method',
                  'notes',
                  ]
        widgets = {
            'date': DateInput(),
        }


class HouseField(forms.ModelChoiceField):
    def label_from_instance(self, house):
        label = f"{house.name}"
        return label


class HouseForm(forms.ModelForm):
    current_HMs = House.objects.all().filter(manager_id__isnull=False).distinct()
    manager = ResidentField(
        # queryset=Resident.objects.exclude(id__in=current_HMs.values_list('manager_id', flat=True)), required=False)
        queryset=Resident.objects.all(), required=False)

    class Meta:
        model = House
        fields = ['name',
                  'manager',
                  'address',
                  'city',
                  'state',
                  ]


class ManagerMeetingForm(forms.ModelForm):
    class Meta:
        model = Manager_meeting
        fields = ['title',
                  'date',
                  'minutes_discussed',
                  'location',
                  'attendee',
                  'issues',
                 ]
        widgets = {
            'date': DateInput(),
        }

class ShoppingTripForm(forms.ModelForm):
    class Meta:
        model = Shopping_trip
        fields = ['date',
                  'amount',
                  'notes',
                  ]
        
class SupplyRequestForm(forms.ModelForm):
    class Meta:
        model = Supply_request
        fields = ['date',
                  'product',
                  'quantity',
                  'notes',
                  'fulfilled',
                  'house',
                  'trip',
                  ]

# class NewPaymentForm(forms.ModelForm):
#
#     type = forms.ChoiceField(choices=TYPE_CHOICES)
#     method = forms.ChoiceField(choices=METHOD_CHOICES, required=False)
#     notes = forms.CharField(widget=forms.Textarea, required=False)
#     resident = ResidentField(queryset=Resident.objects.all())
#
#     def get_form_class(self):
#         if self.object.type != 'pmt':
#             return TransactionForm
#
#     class Meta:
#         model = Transaction
#         fields = ['resident',
#                   'date',
#                   'type',
#                   'amount',
#                   'method',
#                   'notes',
#                   ]
#         widgets = {
#             'date': DateInput(),
#         }
#
#
class DrugTestForm(forms.ModelForm):
    resident = ResidentField(queryset=Resident.objects.filter(discharge_date__isnull=True))
    notes = forms.CharField(required=False)

    SUBSTANCES = (
        ('Amphetamines', 'Amphetamines'),
        ('Barbiturates', 'Barbiturates'),
        ('Benzodiazepines', 'Benzodiazepines'),
        ('Cocaine', 'Cocaine'),
        ('Marijuana', 'Marijuana'),
        ('Opiates', 'Opiates'),
        ('Phencyclidine', 'Phencyclidine'),
        ('Other (Specify)', 'Other (Specify)'),
    )
    substances = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                           choices=SUBSTANCES,
                                           required=False,
                                           label='Substances (if positive)')

    class Meta:
        model = Drug_test
        fields = ['resident',
                  'date',
                  'result',
                  'substances',
                  'notes',
                  # 'amphetamines',
                  # 'barbiturates',
                  # 'benzodiazepines',
                  # 'cocaine',
                  # 'marijuana',
                  # 'opiates',
                  # 'phencyclidine',
                  ]
        widgets = {
            'date': DateInput(),
        }

    def clean_substances(self):
        data = self.cleaned_data['substances']
        data = ', '.join(data)
        return data

    def __init__(self, *args, **kwargs):
        is_hm = kwargs.pop('is_hm', None)
        hm_house = kwargs.pop('house', None)
        super(DrugTestForm, self).__init__(*args, **kwargs)
        if is_hm:
            house_res = Resident.objects.filter(discharge_date__isnull=True, bed__house=hm_house)
            self.fields['resident'].queryset = house_res


class CheckInForm(forms.ModelForm):
    resident = ResidentField(queryset=Resident.objects.filter(discharge_date__isnull=True))
    # house_managers = House.objects.all().filter(manager_id__isnull=False).distinct()
    # manager = ResidentField(queryset=Resident.objects.filter(id__in=house_managers.values_list('manager_id', flat=True)))
    method = forms.ChoiceField(choices=Check_in.METHOD_CHOICES)
    notes = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = Check_in
        fields = ['manager',
                  'resident',
                  'date',
                  'method',
                  'notes',
                  ]
        widgets = {
            'date': DateInput(),
            'manager': forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        is_hm = kwargs.pop('is_hm', None)
        hm_house = kwargs.pop('house', None)
        super(CheckInForm, self).__init__(*args, **kwargs)
        if is_hm:
            house_res = Resident.objects.filter(discharge_date__isnull=True, bed__house=hm_house)
            self.fields['resident'].queryset = house_res


class SiteVisitForm(forms.ModelForm):
    ISSUES = (
        ('Safety issue', 'Safety issue'),
        ('Site not sufficiently clean', 'Site not sufficiently clean'),
        ('Visitors on premises outside visiting hours', 'Visitors on premises outside visiting hours'),
        ('Alcohol/illicit substances present', 'Alcohol/illicit substances present'),
        ('Medications found outside locked safes', 'Medications found outside locked safes'),
        ('Resident curfew violation', 'Resident curfew violation')
    )
    issues = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                       choices=ISSUES,
                                       required=False)
    explanation = forms.CharField(widget=forms.Textarea, required=False)
    house = HouseField(queryset=House.objects.all())

    def clean_issues(self):
        data = self.cleaned_data['issues']
        data = ', '.join(data)
        return data

    class Meta:
        model = Site_visit
        fields = ['manager',
                  'house',
                  'date',
                  'issues',
                  'explanation',
                  ]
        widgets = {
            'date': DateInput(),
            'manager': forms.HiddenInput()
        }


class AbsenteeField(forms.ModelMultipleChoiceField):

    def label_from_instance(self, obj):
        return obj.full_name()


class HouseMeetingForm(forms.ModelForm):
    absentees = AbsenteeField(widget=forms.CheckboxSelectMultiple,
                              queryset=Resident.objects.all(),
                              required=False)

    house = HouseField(queryset=House.objects.all())
    issues = forms.CharField(widget=forms.Textarea, required=False, label='Issues discussed')

    class Meta:
        model = House_meeting
        fields = ['manager',
                  'house',
                  'date',
                  'absentees',
                  'issues',
                  ]
        widgets = {
            'date': DateInput(),
            'manager': forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        is_hm = kwargs.pop('is_hm', None)
        hm_house = kwargs.pop('house', None)
        super(HouseMeetingForm, self).__init__(*args, **kwargs)
        if is_hm:
            house_res = Resident.objects.filter(discharge_date__isnull=True, bed__house=hm_house)
            self.fields['absentees'].queryset = house_res


    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['absentees'].queryset = Resident.objects.none()
    #
    #     if 'house' in self.data:
    #         print(int(self.data.get('house')))
    #         try:
    #             l_house = int(self.data.get('house'))
    #             print(l_house)
    #             print(list(Resident.objects.filter(bed__house_id=l_house).values_list()))
    #             self.fields['absentees'].queryset = Resident.objects.filter(bed__house_id=l_house).order_by('first_name')
    #         except (ValueError, TypeError):
    #             pass
    #     elif self.instance.pk:
    #         self.fields['absentees'].queryset = Resident.objects.all()


# TODO why another form for supply requests?
class AddSupplyForm(forms.ModelForm):
    class Meta:
        model = Supply_request
        fields = ['date',
                  'product',
                  'quantity',
                  'trip',
                  ]


# # May be unnecessary, could add/edit/delete from console instead
# class BedForm:
#     x = ''
#
#
