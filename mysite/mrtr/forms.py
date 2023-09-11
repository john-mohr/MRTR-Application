from django import forms
from .models import *
from django.core.validators import MaxValueValidator
from django.contrib.auth.forms import UserCreationForm


class ContactForm(forms.Form):
    email = forms.EmailField()
    first_name = forms.CharField(label='First Name', max_length=20)
    last_name = forms.CharField(label='Last Name', max_length=20)
    message = forms.CharField(widget=forms.Textarea, max_length=2000)


class DateInput(forms.DateInput):
    input_type = 'date'


class BedField(forms.ModelChoiceField):
    def label_from_instance(self, bed):
        label = f"{bed.name}"
        return label


class ResidentForm(forms.ModelForm):
    phone = forms.CharField(widget=forms.NumberInput, required=False)
    email = forms.EmailField(max_length=62, required=False)
    door_code = forms.CharField(widget=forms.NumberInput, required=False)
    referral_info = forms.CharField(required=False)
    notes = forms.CharField(widget=forms.Textarea, required=False)
    occupied_beds = Resident.objects.all().filter(bed_id__isnull=False).distinct()
    bed = BedField(queryset=Bed.objects.exclude(id__in=occupied_beds.values_list('bed_id', flat=True)))
    effective_date = forms.DateField(widget=DateInput(), initial=timezone.now)  # for edit_res only

    # Allows selection of resident's current bed and removes rent field for editing
    def __init__(self, *args, **kwargs):
        super(ResidentForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:  # edit or readmit
            res = kwargs.pop('instance')
            if res.discharge_date is None:  # edit
                edit_beds = self.occupied_beds.exclude(pk=res.pk)
                self.fields['bed'].queryset = Bed.objects.exclude(id__in=edit_beds.values_list('bed_id', flat=True))
            else:  # readmit
                self.fields['effective_date'].label = 'Readmission date'
                del self.fields['admit_date']
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
    resident = ResidentField(queryset=Resident.objects.all().order_by('first_name'))
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
    method = forms.ChoiceField(choices=Transaction.METHOD_CHOICES, required=True)
    resident = ResidentField(queryset=Resident.objects.filter(discharge_date__isnull=True).order_by('first_name'))
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
    resident = ResidentField(queryset=Resident.objects.all().order_by('first_name'))
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
    manager = ResidentField(
        queryset=Resident.objects.filter(discharge_date__isnull=True).order_by('first_name'), required=False)

    class Meta:
        model = House
        fields = ['name',
                  'manager',
                  'address',
                  'city',
                  'state',
                  ]

    def __init__(self, *args, **kwargs):
        house = kwargs.pop('house', None)
        super(HouseForm, self).__init__(*args, **kwargs)
        house_res = Resident.objects.filter(discharge_date__isnull=True, bed__house=house).order_by('first_name')
        self.fields['manager'].queryset = house_res


class DrugTestForm(forms.ModelForm):
    resident = ResidentField(queryset=Resident.objects.filter(discharge_date__isnull=True).order_by('first_name'))
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
            house_res = Resident.objects.filter(discharge_date__isnull=True, bed__house=hm_house).order_by('first_name')
            self.fields['resident'].queryset = house_res


class CheckInForm(forms.ModelForm):
    resident = ResidentField(queryset=Resident.objects.filter(discharge_date__isnull=True).order_by('first_name'))
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
            house_res = Resident.objects.filter(discharge_date__isnull=True, bed__house=hm_house).order_by('first_name')
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


class HouseSelectForm(forms.Form):
    name = 'house select'
    house = HouseField(queryset=House.objects.all())


class HouseMeetingForm(forms.ModelForm):
    name = 'house meeting'
    absentees = AbsenteeField(widget=forms.CheckboxSelectMultiple,
                              queryset=Resident.objects.all(),
                              required=False)
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
            'manager': forms.HiddenInput(),
            'house': forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        hm_house = kwargs.pop('house', None)
        super(HouseMeetingForm, self).__init__(*args, **kwargs)
        house_res = Resident.objects.filter(discharge_date__isnull=True, bed__house=hm_house).order_by('first_name')
        self.fields['absentees'].queryset = house_res


class ShoppingTripForm(forms.ModelForm):
    amount = forms.DecimalField(decimal_places=2, label='Amount spent')

    class Meta:
        model = Shopping_trip
        fields = ['date',
                  'amount',
                  'notes',
                  ]
        widgets = {
            'date': DateInput()
        }


class SupplyRequestForm(forms.ModelForm):
    products = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                         choices=Supply_request.PRODUCT_CHOICES,
                                         required=False)

    class Meta:
        model = Supply_request
        fields = ['house',
                  'products'
                  ]


class ProductForm(forms.Form):
    quants = forms.CharField(widget=forms.HiddenInput,
                             required=False)
    house = forms.IntegerField(widget=forms.HiddenInput,
                               required=False)
    products = forms.MultipleChoiceField(widget=forms.MultipleHiddenInput(),
                                         choices=Supply_request.PRODUCT_CHOICES,
                                         required=False)

    def __init__(self, *args, **kwargs):
        products = kwargs.pop('products', None)
        if 'quants' in kwargs:
            quants = kwargs.pop('quants', None)
        else:
            quants = None
        super(ProductForm, self).__init__(*args, **kwargs)
        amounts = [
            ('1', 1),
            ('2', 2)
        ]
        for i in range(len(products)):
            if quants is not None:
                if products[i] == 'Other':
                    self.fields['other'] = forms.CharField(label='Other (explain & give quantity)',
                                                           initial=quants[i])
                else:
                    self.fields[products[i]] = forms.ChoiceField(label='Quantity of ' + str(products[i]).lower(),
                                                                 choices=amounts,
                                                                 initial=quants[i])

            else:
                if products[i] == 'Other':
                    self.fields['other'] = forms.CharField(label='Other (explain & give quantity)')
                else:
                    self.fields[products[i]] = forms.ChoiceField(label='Quantity of ' + str(products[i]).lower(),
                                                                 choices=amounts)


class MaintenanceRequestForm(forms.ModelForm):
    house = HouseField(queryset=House.objects.all())
    issue = forms.CharField(widget=forms.Textarea, label='Describe the issue')
    fulfillment_date = forms.DateField(widget=DateInput(), required=False)
    fulfillment_cost = forms.DecimalField(decimal_places=2, required=False)

    class Meta:
        model = Maintenance_request
        fields = [
            'house',
            'manager',
            'issue',
            'fulfillment_date',
            'fulfillment_cost',
            'fulfillment_notes'
        ]
        widgets = {
            'manager': forms.HiddenInput,
        }


class MaintReqField(forms.ModelChoiceField):
    def label_from_instance(self, maint_req):
        label = maint_req.house.name + ': ' + maint_req.issue
        return label


class FulfillMaintReqForm(forms.Form):
    request = MaintReqField(queryset=Maintenance_request.objects.filter(fulfilled=False))
    fulfillment_date = forms.DateField(widget=DateInput(), initial=timezone.now, label='Date fulfilled')
    fulfillment_notes = forms.CharField(widget=forms.Textarea, label='Notes', required=False)
    fulfillment_cost = forms.DecimalField(decimal_places=2, label='Amount spent')


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
