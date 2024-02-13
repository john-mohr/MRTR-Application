from django_use_email_as_username.models import BaseUser, BaseUserManager
from django.db import models
from mrtr.models import Resident


class User(BaseUser):
    objects = BaseUserManager()
    assoc_resident = models.ForeignKey(Resident, on_delete=models.CASCADE, blank=True, null=True)

    TIMEZONES = [('UTC', 'UTC'),
                 ('America/New_York', 'America/New_York'),
                 ('America/Chicago', 'America/Chicago'),
                 ('America/Denver', 'America/Denver'),
                 ('America/Los_Angeles', 'America/Los_Angeles')]

    timezone = models.CharField(default='UTC', max_length=50, choices=TIMEZONES)

    def get_timezone(self):
        return self.timezone
