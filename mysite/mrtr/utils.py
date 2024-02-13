from datetime import date

#import zoneinfo
from django.utils import timezone


# Helper function for calculated transactions
def prorate(rent, e_date):
    return (date(e_date.year, e_date.month + 1, 1) - e_date).days * (rent / 30)


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tzname = request.session.get('django_timezone')
        if tzname:
            #timezone.activate(zoneinfo.ZoneInfo(tzname))
            print()
        else:
            timezone.deactivate()
        return self.get_response(request)
