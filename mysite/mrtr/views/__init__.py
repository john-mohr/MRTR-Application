from functools import wraps
from django.shortcuts import redirect

admin_sidebar = [
    ('/portal', 'gauge', 'Dashboard'),
    ('/portal/residents', 'street-view', 'View Residents'),
    ('/portal/houses', 'house', 'View Houses'),
    ('/portal/beds', 'gear', 'View Beds'),
    ('/portal/transactions', 'gear', 'View Transactions'),
    ('/portal/dtests', 'gear', 'View Drug Tests'),
    ('/portal/check_ins', 'gear', 'View Check Ins'),
    ('/portal/site_visits', 'gear', 'View Site Visits'),
    ('/portal/house_meetings', 'gear', 'View House Meetings'),
    ('/portal/supply_requests', 'gear', 'View Supply Requests'),
    ('/portal/current_shopping_trip', 'gear', 'Current Shopping Trip'),
    ('/portal/shopping_trips', 'gear', 'View Past Shopping Trip'),
    ('/portal/maintenance_requests', 'gear', 'View Maintenance Requests'),
    ('/portal/mngr_meetings', 'handshake', 'View Manager Meetings'),
]

hm_sidebar = [
    ('/portal', 'gauge', 'Dashboard'),
    ('/portal/dtests', 'gear', 'View Drug Tests'),
    ('/portal/check_ins', 'gear', 'View Check Ins'),
    ('/portal/site_visits', 'gear', 'View Site Visits'),
    ('/portal/house_meetings', 'gear', 'View House Meetings'),
    ('/portal/supply_requests', 'gear', 'View Supply Requests'),
    ('/portal/maintenance_requests', 'gear', 'View Maintenance Requests'),
    ('/portal/mngr_meetings', 'handshake', 'View Manager Meetings'),
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
