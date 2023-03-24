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


class BedModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, bed):
        label = f"{bed.name}"
        return label


class NewResidentForm(forms.ModelForm):

    phone = forms.IntegerField(validators=[MaxValueValidator(9999999999)], required=False)
    email = forms.EmailField(max_length=62, required=False)
    door_code = forms.IntegerField(validators=[MaxValueValidator(9999)], required=False)
    referral_info = forms.CharField(required=False)
    notes = forms.CharField(widget=forms.Textarea, required=False)
    occupied_beds = Resident.objects.all().filter(bed_id__isnull=False).distinct()
    bed = BedModelChoiceField(queryset=Bed.objects.exclude(id__in=occupied_beds))

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


class DrugTestForm(forms.ModelForm):
    class Meta:
        model = Drug_test
        fields = ['date', 'result', 'amphetamines', 'resident']


