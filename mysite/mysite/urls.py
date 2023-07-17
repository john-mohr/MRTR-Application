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
from mrtr import views, table_views, single_views
from custom_user import views as user_view
from django.contrib.auth import views as auth

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home),
    path('home', views.home),
    path('about-us', views.about),
    path('our-locations', views.locations),
    path('sobriety-support', views.sobriety_support),
    path('contact', views.contact),
    path('payment-options', views.payment),
    path('portal', views.portal),

    # Resident
    path('portal/new_res', views.new_res),
    path('portal/edit_res/<int:id>', views.edit_res),
    path('portal/discharge_res/<int:id>', views.discharge_res),
    path('portal/readmit_res/<int:id>', views.readmit_res),
    path('portal/residents', table_views.residents),
    path('portal/resident/<int:res_id>', single_views.resident, name='resident'),

    # Transactions
    path('portal/new_trans', views.new_trans),
    path('portal/new_trans/<int:res_id>', views.new_trans),
    path('portal/new_rent_pmt', views.new_rent_pmt),
    path('portal/new_rent_pmt/<int:res_id>', views.new_rent_pmt),
    path('portal/edit_trans/<int:id>', views.edit_trans),
    path('portal/transactions', table_views.transactions),
    # path('portal/transaction/<int:id>', views.transaction),

    # Houses
    path('portal/new_house', views.new_house),
    path('portal/edit_house/<int:id>', views.edit_house),
    path('portal/houses', table_views.houses),
    path('portal/house/<int:house_id>', single_views.house),

    # Meetings
    path('portal/new_meeting', views.new_meeting),
    path('portal/edit_meeting/<int:id>', views.edit_meeting),
    path('portal/meetings', views.meetings),
    path('portal/meeting/<int:id>', views.single_meeting),

    path('portal/new_house_meeting', views.new_house_meeting),
    path('portal/edit_house_meeting/<int:hm_id>', views.edit_house_meeting),
    path('portal/house_meetings', table_views.house_meetings),

    # Drug tests
    path('portal/new_dtest', views.new_dtest),
    path('portal/edit_dtest/<int:test_id>', views.edit_dtest),
    path('portal/dtests', table_views.dtests),

    # Check ins
    path('portal/new_check_in', views.new_check_in),
    path('portal/edit_check_in/<int:ci_id>', views.edit_check_in),
    path('portal/check_ins', table_views.check_ins),

    # Site visits
    path('portal/new_site_visit', views.new_site_visit),
    path('portal/edit_site_visit/<int:sv_id>', views.edit_site_visit),
    path('portal/site_visits', table_views.site_visits),

    # Supply Request
    path('portal/new_supply_request', views.new_supply_request),
    path('portal/edit_supply_request/<int:id>', views.edit_supply_request),
    path('portal/supply_request', views.supply_request),
    path('portal/supply_request/<int:id>', views.single_supply_request),

    # Shopping Trip
    path('portal/new_shopping_trip', views.new_shopping_trip),
    path('portal/edit_shopping_trip/<int:id>', views.edit_shopping_trip),
    path('portal/shopping_trip', views.shopping_trip),
    path('portal/shopping_trip/<int:id>', views.single_shopping_trip),



    # Other
    # path('portal/change_hm', views.change_hm),
    path('portal/beds', table_views.beds),

    # House Manager Page
    path('portal/house_manager/', views.house_manager),

]

urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register/', user_view.register, name ='register'),
]