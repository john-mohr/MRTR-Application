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
    ('/portal/meetings', 'handshake', 'View Manager Meetings'),
    ('/portal/supply_requests', 'handshake', 'View Supply Requests'),
    ('/portal/shopping_trips', 'handshake', 'View Shopping Trips'),
]

hm_sidebar = [
    ('/portal', 'gauge', 'Dashboard'),
    ('/portal/dtests', 'gear', 'View Drug Tests'),
    ('/portal/check_ins', 'gear', 'View Check Ins'),
    ('/portal/site_visits', 'gear', 'View Site Visits'),
    ('/portal/house_meetings', 'gear', 'View House Meetings'),
    # ('/portal/house_manager//meetings', 'gear', 'View Manager Meetings'),
    # ('#', 'gear', 'View Maintenance Tickets'),
    # ('#', 'gear', 'View Supply Requests'),
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
