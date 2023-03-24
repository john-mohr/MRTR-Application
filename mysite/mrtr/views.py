from django.shortcuts import render, redirect
from .forms import ContactForm
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from .models import Resident, Transaction, Drug_test, Rent_change, House, Bed, Shopping_trip, Supply_request, House_manager, Manager_meeting, Attendee, Absentee, Site_visit, Manager_issue, Check_in, House_meeting

# Create your views here.

def home(request):
	if request.method == 'POST':
		form = ContactForm(request.POST)
		if form.is_valid():
			subject = "Website Inquiry" 
			body = {
			'first_name': form.cleaned_data['first_name'], 
			'last_name': form.cleaned_data['last_name'], 
			'email': form.cleaned_data['email'], 
			'message':form.cleaned_data['message'], 
			}
			message = "\n".join(body.values())

			try:
				send_mail(subject, message, 'deanpham1200@gmail.com', ['deanpham1200@gmail.com']) 
			except BadHeaderError:
				return HttpResponse('Invalid header found.')
			return redirect ('/')
      
	form = ContactForm()
	return render(request, 'mrtr/index.html', {'form':form})

def locations(request):
    
    return render(request, '.html')

def about(request):
    
    return render(request, '.html')

def payment(request):
    
    return render(request, '.html')

def contact(request):
    
    return render(request, '.html')

def portal(request):
    return render(request, 'mrtr/administrative.html')