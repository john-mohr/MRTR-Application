from django import forms
from .models import *
from django.core.validators import MaxValueValidator
from django.contrib.auth.forms import UserCreationForm
 

class ContactForm(forms.Form):
    email = forms.EmailField()
    first_name = forms.CharField(label= 'First Name', max_length = 20)
    last_name = forms.CharField(label= 'Last Name', max_length = 20)
    message = message = forms.CharField(widget = forms.Textarea, max_length = 2000)


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

    # Allows selection of resident's current bed and removes rent field for editing
    def __init__(self, *args, **kwargs):
        super(ResidentForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            edit_beds = self.occupied_beds.exclude(pk=kwargs.pop('instance').pk)
            self.fields['bed'] = BedField(queryset=Bed.objects.exclude(id__in=edit_beds.values_list('bed_id', flat=True)))
            del self.fields['rent']

    class Meta:
        model = Resident
        fields = ['first_name',
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


TYPE_CHOICES = [

    # # Auto apply
    # ('rnt', 'Rent charge'),
    # ('rfd', 'Refund'),
    # ('inc', 'Sober incentive'),
    # ('nra', 'New rent amount adjustment'),

    # Decrease balance
    ('pmt', 'Rent payment'),
    # ('bon', 'Bonus'),
    # ('wrk', 'Work/reimbursement'),
    # ('sos', "Sober support (won't pay back)"),

    # Increase balance
    ('fee', 'Fee'),
    # ('lon', 'Loan (will pay back)'),

    # Other
    # ('fix', 'Balance fix'),
    ('oth', 'Other adjustment (specify)')
    ]

METHOD_CHOICES = [
    ('ach', 'ACH'),
    ('csh', 'Cash'),
    ('cap', 'Cash App'),
    ('chk', 'Check'),
    ('mod', 'Money order'),
    ('ppl', 'PayPal'),
    ('vnm', 'Venmo'),
    ('zel', 'Zelle'),
    ('oth', 'Other (specify)'),
    ('', '')
    ]


class ResidentField(forms.ModelChoiceField):
    def label_from_instance(self, resident):
        label = resident.first_name + " " + resident.last_name
        return label


class SelectResForm(forms.Form):
    resident = ResidentField(queryset=Resident.objects.all())


class NewTransactionForm(forms.ModelForm):
    resident = ResidentField(queryset=Resident.objects.all())
    type = forms.ChoiceField(choices=TYPE_CHOICES)
    method = forms.ChoiceField(choices=METHOD_CHOICES, required=False)
    notes = forms.CharField(widget=forms.Textarea, required=False)

    # def get_form_class(self):
    #     if self.object.type == 'pmt':
    #         return NewPaymentForm

    class Meta:
        model = Transaction
        fields = ['resident',
                  'date',
                  'type',
                  'amount',
                  'method',
                  'notes',
                  ]
        widgets = {
            'date': DateInput(),
        }


# class NewPaymentForm(forms.ModelForm):
#
#     type = forms.ChoiceField(choices=TYPE_CHOICES)
#     method = forms.ChoiceField(choices=METHOD_CHOICES, required=False)
#     notes = forms.CharField(widget=forms.Textarea, required=False)
#     resident = ResidentField(queryset=Resident.objects.all())
#
#     def get_form_class(self):
#         if self.object.type != 'pmt':
#             return NewTransactionForm
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


class DrugTestForm(forms.ModelForm):
    resident = ResidentField(queryset=Resident.objects.all())
    other = forms.CharField(required=False)

    class Meta:
        model = Drug_test
        fields = ['resident',
                  'date',
                  'result',
                  'amphetamines',
                  'barbiturates',
                  'benzodiazepines',
                  'cocaine',
                  'marijuana',
                  'opiates',
                  'phencyclidine',
                  ]
        widgets = {
            'date': DateInput(),
        }


class HouseField(forms.ModelChoiceField):
    def label_from_instance(self, house):
        label = f"{house.name}"
        return label


# May want to restrict new_manager field to residents who reside in the house
class ChangeHMForm(forms.Form):
    house = HouseField(queryset=House.objects.all())
    current_HMs = House.objects.all().filter(manager_id__isnull=False).distinct()
    new_manager = ResidentField(queryset=Resident.objects.exclude(id__in=current_HMs.values_list('manager_id', flat=True)))

class RentChangeForm(forms.Form):
    resident = ResidentField(queryset=Resident.objects.all())
    effective_date = forms.DateField(widget=DateInput(), initial=timezone.now)
    new_rent = forms.IntegerField(validators=[MaxValueValidator(1000)])
    reason = forms.CharField(widget=forms.Textarea)


# class ManagerMeetingForm:
#     x = ''
#
#     class Meta:
#         model = Manager_meeting
#         fields = ['date',
#                   'location',
#                   'minutes_discussed'
#                  ]
#         widgets = {
#             'date': DateInput()
#         }
#
#
# # May be unnecessary, could add/edit/delete from console instead
# class HouseForm:
#     x = ''
#
#
# # May be unnecessary, could add/edit/delete from console instead
# class BedForm:
#     x = ''
#
#
# class SiteVisitForm:
#     x = ''
#
#
# class CheckInForm:
#     x = ''
#
#
# class HouseMeetingForm:
#     x = ''
#
#
# class SupplyRequestForm:
#     x = ''

