"""FYProject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path
from django.views.generic import TemplateView
from django.conf.urls import url
from FYProject.Hospital.views import *
from django.conf import settings
from django.conf.urls.static import static


admin.site.site_header = 'Hospital administration'

urlpatterns = [
    path('editbooking/<int:bid>', edit_booking, name="editbooking"),
    path('addbooking/', addbooking, name="addbooking"),
    path('bookings/', bookings, name="bookings"),
    path('logout/', logoutuser, name="logout"),
    path('waitingverification/', TemplateView.as_view(template_name="waitingverification.html"), name="waitingverification"),
    path('deletedoctor/<int:did>/', delete_doctor, name="deletedoctor"),
    path('editprofile/', edit_profile, name="editprofile"),
    path('changepassword/', change_password, name="changepassword"),
    path('editpatient/<int:pid>/', edit_patient, name="editpatient"),
    path('editdoctor/<int:did>/', edit_doctor, name="editdoctor"),
    path('doctors/', doctor_panel, name="doctors"),
    path('adddoctor/', add_doctor, name="adddoctor"),
    path('locatehospital/', map_view, name="locatehospital"),
    path('hospitaldepartments/', hospital_departments, name="departments"),
    path('adddepartment/', add_department, name="adddepartment"),
    path('editdepartment/<int:did>/', edit_department, name="editdepartment"),
    path('hospitaldetails/<int:hid>/', hospital_details, name="hospitaldetails"),
    path('addpatient/', add_patient, name="addpatient"),
    path('hospitaldashboard/', hospital_dashboard, name="dashboard"),
    path('completehospitalprofile/', complete_hospital_profile, name="completeprofilehospital"),
    path('register/', register_view, name="register"),
    path('login/', login_view, name="login"),
    url(r'^$', TemplateView.as_view(template_name="about.html"), name="index"),
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)