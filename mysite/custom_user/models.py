from django_use_email_as_username.models import BaseUser, BaseUserManager
from django.db import models
from mrtr.models import Resident


class User(BaseUser):
    objects = BaseUserManager()
    assoc_resident = models.ForeignKey(Resident, on_delete=models.CASCADE, blank=True, null=True)
