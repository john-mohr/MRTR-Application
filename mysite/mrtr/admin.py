from django.contrib import admin
from mrtr.models import Resident, Transaction, Drug_test, Rent_change, House, Bed, Shopping_trip, Supply_request, House_manager, Manager_meeting, Attendee, Absentee, Site_visit, Manager_issue, Check_in, House_meeting
# Register your models here.

admin.site.register(Resident)
admin.site.register(Transaction)
admin.site.register(Drug_test)
admin.site.register(Rent_change)
admin.site.register(House)
admin.site.register(Bed)
admin.site.register(Shopping_trip)
admin.site.register(Supply_request)
admin.site.register(House_manager)
admin.site.register(Manager_meeting)
admin.site.register(Attendee)
admin.site.register(Site_visit)
admin.site.register(Manager_issue)
admin.site.register(Check_in)
admin.site.register(House_meeting)
admin.site.register(Absentee)
