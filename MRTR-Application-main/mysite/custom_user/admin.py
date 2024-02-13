from django.contrib import admin
from django_use_email_as_username.admin import BaseUserAdmin
from .models import User


BaseUserAdmin.list_display += ('assoc_resident', 'timezone',)  # don't forget the commas
BaseUserAdmin.list_filter += ('assoc_resident', 'timezone',)
BaseUserAdmin.fieldsets[1][1]['fields'] += ('assoc_resident', 'timezone',)

admin.site.register(User, BaseUserAdmin)
