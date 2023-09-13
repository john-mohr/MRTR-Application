"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from mrtr.views import admin_forms, tables, hm_forms, o_views, singles
from custom_user import views as user_view
# from django.contrib.auth import views as auth

urlpatterns = [
    path('forbidden', o_views.forbidden),

    path('admin/', admin.site.urls),
    path('', o_views.home),
    path('home', o_views.home),
    path('about-us', o_views.about),
    path('our-locations', o_views.locations),
    path('sobriety-support', o_views.sobriety_support),
    path('contact', o_views.contact),
    path('payment-options', o_views.payment),
    path('portal', o_views.portal),

    # Resident
    path('portal/new_res', admin_forms.new_res),
    path('portal/edit_res/<int:res_id>', admin_forms.edit_res),
    path('portal/discharge_res/<int:res_id>', admin_forms.discharge_res),
    path('portal/readmit_res/<int:res_id>', admin_forms.readmit_res),
    path('portal/residents', tables.residents),
    path('portal/resident/<int:res_id>', singles.resident, name='resident'),

    # Transactions
    path('portal/new_trans', admin_forms.new_trans),
    path('portal/new_trans/<int:res_id>', admin_forms.new_trans),
    path('portal/new_rent_pmt', admin_forms.new_rent_pmt),
    path('portal/new_rent_pmt/<int:res_id>', admin_forms.new_rent_pmt),
    path('portal/edit_trans/<int:trans_id>', admin_forms.edit_trans),
    path('portal/transactions', tables.transactions),

    # Houses
    path('portal/new_house', admin_forms.new_house),
    path('portal/edit_house/<int:house_id>', admin_forms.edit_house),
    path('portal/houses', tables.houses),
    path('portal/house/<str:house_id>', singles.house),
    path('portal/beds', tables.beds),

    path('portal/new_house_meeting', hm_forms.new_house_meeting),
    path('portal/edit_house_meeting/<int:hm_id>', hm_forms.edit_house_meeting),
    path('portal/house_meetings', tables.house_meetings),

    # Drug tests
    path('portal/new_dtest', hm_forms.new_dtest),
    path('portal/edit_dtest/<int:test_id>', hm_forms.edit_dtest),
    path('portal/dtests', tables.dtests),

    # Check ins
    path('portal/new_check_in', hm_forms.new_check_in),
    path('portal/edit_check_in/<int:ci_id>', hm_forms.edit_check_in),
    path('portal/check_ins', tables.check_ins),

    # Site visits
    path('portal/new_site_visit', hm_forms.new_site_visit),
    path('portal/edit_site_visit/<int:sv_id>', hm_forms.edit_site_visit),
    path('portal/site_visits', tables.site_visits),

    # Supply Request
    path('portal/new_supply_request', hm_forms.new_supply_request),
    path('portal/edit_supply_request/<int:sr_id>', hm_forms.edit_supply_request),
    path('portal/supply_requests', tables.supply_requests),

    # Shopping Trip
    path('portal/new_shopping_trip', admin_forms.new_shopping_trip),
    path('portal/edit_shopping_trip/<int:trip_id>', admin_forms.edit_shopping_trip),
    path('portal/shopping_trips', tables.shopping_trips),
    path('portal/current_shopping_trip', singles.single_shopping_trip),
    path('portal/shopping_trip/<int:trip_id>', singles.single_shopping_trip),

    # Maintenance Requests
    path('portal/new_maintenance_request', hm_forms.new_maintenance_request),
    path('portal/fulfill_maintenance_request', hm_forms.fulfill_maintenance_request),
    path('portal/edit_maintenance_request/<int:mr_id>', hm_forms.edit_maintenance_request),
    path('portal/maintenance_requests', tables.maintenance_requests),

    # # Meetings
    # path('portal/new_meeting', o_views.new_meeting),
    # path('portal/edit_meeting/<int:id>', o_views.edit_meeting),
    # path('portal/meetings', tables.meetings),
]

urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register/', user_view.register, name='register'),
]
