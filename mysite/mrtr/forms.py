from django import forms
from django.forms import ModelForm
from .models import Resident, Transaction, Drug_test, Rent_change, House, Bed, Shopping_trip, Supply_request, House_manager, Manager_meeting, Attendee, Absentee, Site_visit, Manager_issue, Check_in, House_meeting


from django.contrib.auth.forms import UserCreationForm
 

class ContactForm(forms.Form):
    email = forms.EmailField()
    first_name = forms.CharField(label= 'First Name', max_length = 20)
    last_name = forms.CharField(label= 'Last Name', max_length = 20)
    message = message = forms.CharField(widget = forms.Textarea, max_length = 2000)


class DateInput(forms.DateInput):
    input_type = 'date'


class HouseModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, house):
        label = f"{house.name}"
        return label


class NewResidentForm(ModelForm):
    class Meta:
        model = Resident
        fields = ['first_name', 'last_name', 'admit_date', 'rent', 'house']
        field_classes = {
            'house': HouseModelChoiceField,
        }
        widgets = {
            'admit_date': DateInput()
        }

class DrugTestForm(ModelForm):
    class Meta:
        model = Drug_test
        fields = ['date', 'result', 'amphetamines', 'resident']


