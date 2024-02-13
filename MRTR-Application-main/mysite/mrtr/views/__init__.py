from functools import wraps
from django.shortcuts import redirect

admin_sidebar = [
    ('/portal', 'gauge', 'Dashboard'),
    ('/portal/residents', 'street-view', 'Residents'),
    ('/portal/houses', 'house', 'Houses'),
    ('/portal/beds', 'gear', 'Beds'),
    ('/portal/transactions', 'gear', 'Transactions'),
    ('/portal/dtests', 'gear', 'Drug Tests'),
    ('/portal/check_ins', 'gear', 'Check Ins'),
    ('/portal/site_visits', 'gear', 'Site Visits'),
    ('/portal/house_meetings', 'gear', 'House Meetings'),
    ('/portal/supply_requests', 'gear', 'Supply Requests'),
    ('/portal/current_shopping_trip', 'gear', 'Current Shopping Trip'),
    ('/portal/shopping_trips', 'gear', 'Past Shopping Trips'),
    ('/portal/maintenance_requests', 'gear', 'Maintenance Requests'),
    ('/portal/mngr_meetings', 'handshake', 'Manager Meetings'),
]

hm_sidebar = [
    ('/portal', 'gauge', 'Dashboard'),
    ('/portal/dtests', 'gear', 'Drug Tests'),
    ('/portal/check_ins', 'gear', 'Check Ins'),
    ('/portal/site_visits', 'gear', 'Site Visits'),
    ('/portal/house_meetings', 'gear', 'House Meetings'),
    ('/portal/supply_requests', 'gear', 'Supply Requests'),
    ('/portal/maintenance_requests', 'gear', 'Maintenance Requests'),
    ('/portal/mngr_meetings', 'handshake', 'Manager Meetings'),
]

def user_is_hm(request):
    roles = list(request.user.groups.values_list('name', flat=True))
    if 'House Manager' in roles:
        return True
    else:
        return False

def username(request):
    un = request.user.first_name + " " + request.user.last_name
    return un

def groups_only(*groups):
    def inner(view_func):
        @wraps(view_func)
        def wrapper_func(request, *args, **kwargs):
            if request.user.groups.filter(name__in=groups).exists() or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            else:
                return redirect('/forbidden')
        return wrapper_func
    return inner
