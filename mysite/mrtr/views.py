from django.shortcuts import render
from .models import Resident, Transaction, Drug_test, Rent_change, House, Bed, Shopping_trip, Supply_request, House_manager, Manager_meeting, Attendee, Absentee, Site_visit, Manager_issue, Check_in, House_meeting

# Create your views here.


def home(request):
    
    return render(request, 'mrtr/index.html')

def locations(request):
    
    return render(request, '.html')

def about(request):
    
    return render(request, '.html')

def payment(request):
    
    return render(request, '.html')

def contact(request):
    
    return render(request, '.html')