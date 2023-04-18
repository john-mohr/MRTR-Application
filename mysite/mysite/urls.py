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
from mrtr import views
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
    # path('portal', views.portal),

    # Resident
    path('new_res', views.new_res),
    path('select_res', views.select_res),
    path('edit_res/<int:id>', views.edit_res),
    path('discharge_res/<int:id>', views.discharge_res),
    path('readmit_res', views.select_past_res),
    path('readmit_res/<int:id>', views.readmit_res),
    path('show_res', views.show_res),

    # Transactions
    path('new_trans', views.new_trans),
    path('select_trans', views.select_trans),
    path('edit_trans/<int:id>', views.edit_trans),

    # Other
    path('change_hm', views.change_hm),
    # path('new_dtest', views.new_dtest),

]

urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register/', user_view.register, name ='register'),
]
