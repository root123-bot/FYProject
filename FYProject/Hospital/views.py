from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from .models import *
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from geopy.geocoders import Nominatim
import json
import datetime as dt

def get_coords(address):
    while True:
        try:
            geolocator = Nominatim(user_agent="hospital")
            location = geolocator.geocode(address)
            return f"{location.latitude}, {location.longitude}"
        except:
            pass


@require_http_methods(['HEAD', 'GET'])
def logoutuser(request):
    logout(request)
    return redirect('/')

   
# Create your views here.
class RegisterView(View):
    template_name = "register.html"
    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        print('IM POST IM EXECUTED')
        password = request.POST['password']
        user_group = request.POST.get('user_group', None)
        email = request.POST.get('email')
        print(password, user_group, email)
        try:
            if (email and password and user_group):
                password_hash = make_password(password)
                user = get_user_model().objects.create(
                    email = email,
                    password = password_hash
                )

                user.save()

                if(user_group == "customer"):
                    normal_user = NormalUsers.objects.create(
                        user = user
                    )
                    normal_user.save()
                    login(request, user)

                elif (user_group == "Hospital"):
                    hospital = Hospital.objects.create(
                        user=user
                    )
                    hospital.save()
                    login(request, user)



                return HttpResponseRedirect(reverse("completeprofilehospital"))

            else:
                return render(request, self.template_name, {"error": "Missing some fields"})
        
        except Exception as error:
            print("Error ", str(error))
            return render(request, self.template_name, {"error": str(error)})

register_view = RegisterView.as_view()

class CompleteHospitalProfile(View):
    template_name = "completeHospitalProfile.html"

    @method_decorator(login_required(login_url="/login"))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        hospital = self.request.user.hospital
        try:
            logo = request.FILES.get('logo', None)
            address = request.POST.get('address', None)
            brand = request.POST.get('brand', None)

            hospital.name = brand
            hospital.logo = logo
            hospital.physical_address = address

            # also we should fetch coords but i think for now its okay
            hospital.is_profile_completed = True
            hospital.coords = get_coords(address)
            hospital.save()
            
            return HttpResponseRedirect(reverse("waitingverification"))
        
        except Exception as err:
            return render(request, self.template_name, {"errors": str(err)})

complete_hospital_profile = CompleteHospitalProfile.as_view()

class DeleteView(View):
    templat_name = "delete.html"

    def get(self, request, *args, **kwargs):
        doctor_id = kwargs.get('did', None)
        if doctor_id:
            doctor = Doctor.objects.get(id = int(doctor_id))
            doctor.delete()
            return HttpResponseRedirect(reverse("dashboard"))
        
        return render(request, self.template_name)

delete_doctor = DeleteView.as_view()

class MapView(View):
    template_name = "map.html"

    def get(self, request):
        hospitals = Hospital.objects.filter(is_profile_completed=True, is_approved=True)
        hospital_metadata = []

        for hospital in hospitals:
            department_metadata = []
            for department in hospital.departments.all():
                department_metadata.append({
                    "name": department.name,
                    "hospital": hospital.name,
                    "id": hospital.id,
                    "queue": department.patients.all().filter(status = "Pending").count(),
                })

            hospital_metadata.append({
                "name": hospital.name,
                "coords": hospital.coords,
                "logo": hospital.logo.url,
                "queue": hospital.wagonjwa.all().filter(status = "Pending").count(),
                "pbookings": hospital.bookings.all().filter(status = 'Pending').count(),
                "id": hospital.id,
                "totalDoctors": hospital.madokta.all().count(),
                "department_metadata": department_metadata
            })
        print("Hospital metadata ", hospital_metadata)
        
        return render(request, self.template_name, {"dmetadata": json.dumps(department_metadata), "metadata": json.dumps(hospital_metadata)})
    
map_view = MapView.as_view()

class HospitalDashboard(View):
    template_name = "hospitalDashboard.html"

    @method_decorator(login_required(login_url="/login"))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        hospital = self.request.user.hospital
        patients = hospital.wagonjwa.all()
        created_today = 0
        treated_today = 0
        queue_today = 0
        warded_today = 0
        nhif_patients = patients.filter(is_using_NHIF = True).count()
        today_nhif_patients = 0
        for patient in patients:
            print(patient.created_at.date(), dt.date.today())
            if patient.created_at.date() == dt.date.today():
                created_today += 1
                if patient.status == "Treated":
                    treated_today += 1
                
                if patient.status == "Pending":
                    queue_today += 1

                if patient.status == "Hospitalized":
                    warded_today += 1

                if patient.is_using_NHIF:
                    today_nhif_patients += 1


        metadata = {
            "created_today" : created_today,
            "treated_today" : treated_today,
            "queue_today" : queue_today,
            "hospitalized_today": warded_today,
            "nhif_patients": nhif_patients,
            "total_doctors": hospital.madokta.all().count(),
            "today_nhif_patients": today_nhif_patients,
            "total_departments": hospital.departments.all().count(),
        }
        
        print('patients ', metadata)
        return render(request, self.template_name, {"metadata": metadata, "patients": patients, "infolen": patients.count(), "name": hospital.name, "logo": hospital.logo.url})

hospital_dashboard = HospitalDashboard.as_view()


class HospitalDepartments(View):
    template_name = "departments.html"

    @method_decorator(login_required(login_url="/login"))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        hospital = self.request.user.hospital
        departments = hospital.departments.all()
        print('Departments ', departments)
        return render(request, self.template_name, {"departments" : departments, "idadi": len(departments), "name": hospital.name, "logo": hospital.logo.url})

hospital_departments = HospitalDepartments.as_view()

class AddDepartment(View):
    template_name = "adddepartment.html"

    @method_decorator(login_required(login_url="/login"))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        hospital = self.request.user.hospital
        return render(request, self.template_name, {"name": hospital.name, "logo": hospital.logo.url})

    def post(self, request):
        hospital = self.request.user.hospital
        name = request.POST.get("name", None)

        try:
            department = Department.objects.create(
                hospital = hospital,
                name = name
            )

            department.save()

            return HttpResponseRedirect(reverse("departments"))
        
        except Exception as err:
            return render(request, self.template_name, {"name": hospital.name, "logo": hospital.logo.url})

add_department = AddDepartment.as_view()

class DoctorsPanel(View):
    template_name = "doctors.html"

    @method_decorator(login_required(login_url="/login"))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        hospital = self.request.user.hospital
        doctors = hospital.madokta.all()
        return render(request, self.template_name, {"doctors": doctors, "infolen": doctors.count(), "name": hospital.name, "logo": hospital.logo.url})

doctor_panel = DoctorsPanel.as_view()

class Booking(View):
    template_name = "booking.html"

    @method_decorator(login_required(login_url="/login"))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


    def get(self, request):
        hospital = self.request.user.hospital
        bookings = hospital.bookings.all()

        return render(request, self.template_name, {"bookings": bookings, "infolen": bookings.count(), "name": hospital.name, "logo": hospital.logo.url})

bookings = Booking.as_view()

class EditBooking(View):
    template_name = "editbooking.html"

    @method_decorator(login_required(login_url="/login"))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


    def get(self, request, *args, **kwargs):
        hospital = self.request.user.hospital
        booking_id = self.kwargs.get("bid")
        booking = HospitalBooking.objects.get(id=int(booking_id))

        return render(request, self.template_name, {"booking": booking, "name": hospital.name, "logo": hospital.logo.url})


    def post(self, request, *args, **kwargs):
        name = request.POST.get("name")
        status = request.POST.get("status")
        try:
            booking_id = self.kwargs.get("bid")
            hospital = self.request.user.hospital

            booking = HospitalBooking.objects.get(id=int(booking_id))

            booking.patient_name = name
            booking.status = status

            booking.save()

            return HttpResponseRedirect(reverse("bookings"))

        except Exception as err:
            print("THIS IS EXCEPTION OCCURED ", str(err))
            return render(request, self.template_name, {"booking": booking, "name": hospital.name, "logo": hospital.logo.url})

edit_booking = EditBooking.as_view()


class AddBooking(View):
    template_name = "addbooking.html"

    @method_decorator(login_required(login_url="/login"))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        hospital = self.request.user.hospital
        return render(request, self.template_name, {"name": hospital.name, "logo": hospital.logo.url})

    def post(self, request):
        name = request.POST.get("name", None)
        hospital = self.request.user.hospital
        try:
            booking = HospitalBooking.objects.create(
                patient_name = name,
                hospital = hospital
            )

            booking.save()
            return HttpResponseRedirect(reverse("bookings"))
 
        except Exception as err:
            print('There are exceptions ', str(err))
            return render(request, self.template_name, {"name": hospital.name, "logo": hospital.logo.url})

addbooking = AddBooking.as_view()

class ChangePassword(View):
    template_name = 'changepassword.html'

    @method_decorator(login_required(login_url="/login"))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


    def get(self, request):
        hospital = self.request.user.hospital
        return render(request, self.template_name, {"name": hospital.name, "logo": hospital.logo.url})
    
    def post(self, request):
        password = request.POST.get('password')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        user = self.request.user
        hospital = user.hospital

       
        if (password1 != password2):
            print('failed password is not the same')
            return render(request, self.template_name, {"message": "Password didn\'t match", "name": hospital.name, "logo": hospital.logo.url})

        if (len(password1.strip()) < 6):
            print('failed password should be greater that 6')
            return render(request, self.template_name, {"message": "Use longer password more than 6 characters is required", "name": hospital.name, "logo": hospital.logo.url})

        if user.check_password(password):
            user.password = make_password(password1)
            user.save()
            login(request, user)
            return HttpResponseRedirect(reverse("dashboard"))

        # this means the old password is invalid..
        return render(request, self.template_name, {"name": hospital.name, "logo": hospital.logo.url})


change_password = ChangePassword.as_view()

class EditProfile(View):
    template_name = 'editprofile.html'

    @method_decorator(login_required(login_url="/login"))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


    def get(self, request):
        hospital = self.request.user.hospital
        return render(request, self.template_name, {"address": hospital.physical_address, "name": hospital.name, "logo": hospital.logo.url})


    def post(self, request):
        hospital = self.request.user.hospital
        try:
            logo = request.FILES.get('logo', None)
            address = request.POST.get('address', None)
            brand = request.POST.get('brand', None)

            hospital.name = brand
            print('this is logo ', logo)
            if (logo != 'null' and logo != None):
                hospital.logo = logo
            hospital.physical_address = address

            # also we should fetch coords but i think for now its okay
            hospital.is_profile_completed = True
            hospital.coords = get_coords(address)
            hospital.save()

            return HttpResponseRedirect(reverse("dashboard"))
        
        except Exception as err:
            print('this is exception ', err)
            return render(request, self.template_name, {"errors": str(err), "address": hospital.physical_address, "name": hospital.name, "logo": hospital.logo.url})


edit_profile = EditProfile.as_view()

class EditPatient(View):
    template_name = "editpatient.html"

    @method_decorator(login_required(login_url="/login"))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


    def get(self, request, *args, **kwargs):
        patient_id = self.kwargs.get("pid")
        patient = Patient.objects.get(id=int(patient_id))
        hospital = self.request.user.hospital
        departments = hospital.departments.all()
        # doctors = Doctor.objects.all()
        doctors = hospital.madokta.all()
        return render(request, self.template_name, {"departments": departments, "target": patient, "doctors": doctors, "name": hospital.name, "logo": hospital.logo.url})

    def post(self, request, *args, **kwargs):
        patient_id = self.kwargs.get("pid")
        patient = Patient.objects.get(id=int(patient_id))
        hospital = self.request.user.hospital
        doctors = Doctor.objects.all()
        name = request.POST.get("name", None)
        status = request.POST.get("status", None)
        doctor_id = request.POST.get("doctor", None)
        department = request.POST.get("department", None)
        isuse_nhif = request.POST.get('isusingnhif')
        print('STATUS ', status)
        departments = hospital.departments.all()
        isuse_nhif = True if isuse_nhif == "on" else False
        try:
            patient.name = name
            patient.status = status
            patient.doctor = Doctor.objects.get(id=int(doctor_id))
            patient.is_using_NHIF = isuse_nhif
            patient.department = Department.objects.get(id=int(department))

            patient.save()
            return HttpResponseRedirect(reverse("dashboard"))

        except Exception as err:
            print('error ', err)
            return render(request, self.template_name, {"departments": departments, "target": patient, "doctors": doctors, "name": hospital.name, "logo": hospital.logo.url})


            

edit_patient = EditPatient.as_view()

class AddPatient(View):
    template_name = "addpatient.html"
    
    @method_decorator(login_required(login_url="/login"))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        hospital = self.request.user.hospital
        doctors = hospital.madokta.all()
        departments = hospital.departments.all()
        return render(request, self.template_name, {"departments": departments, "doctors": doctors, "name": hospital.name, "logo": hospital.logo.url})
    
    def post(self, request):
        doctors = Doctor.objects.all()
        name = request.POST.get('name', None)
        doctor = request.POST.get('doctor', None)
        hospital = request.user.hospital
        department = request.POST.get('department', None)
        isuse_nhif = request.POST.get('isusingnhif')
        departments = hospital.departments.all()
        print('this radio button ', isuse_nhif)
        isuse_nhif = True if isuse_nhif == "on" else False
        try:
            patient = Patient.objects.create(
                name = name,
                doctor = Doctor.objects.get(id=int(doctor)),
                is_using_NHIF = isuse_nhif,
                status = "Pending",
                hospital = hospital,
                department = Department.objects.get(id=int(department))
            )

            patient.save()
            return HttpResponseRedirect(reverse("dashboard"))

        except Exception as err:
            print('error is ', err)
            return render(request, self.template_name, {"departments": departments, "doctors": doctors, "name": hospital.name, "logo": hospital.logo.url})


add_patient = AddPatient.as_view()


class HospitalDetails(View):
    template_name = "viewdetails.html"

    def get(self, request, *args, **kwargs):
        hospital_id = self.kwargs.get('hid')
        hospital = Hospital.objects.get(id=int(hospital_id))

        department_metadata = []
        for department in hospital.departments.all():
            department_metadata.append({
                "name": department.name,
                "hospital": hospital.name,
                "id": hospital.id,
                "queue": department.patients.all().filter(status = "Pending").count(),
                "doctors": department.doctors.all().count()
            })
        print("TOTAL DEPARTMENTS ", hospital.departments.all())
        metadata = {
            "name": hospital.name,
            "logo": hospital.logo.url,
            "department": department_metadata,
            "address": hospital.physical_address,
            "total_departments": hospital.departments.all().count(),
            "queue": hospital.wagonjwa.all().filter(status = "Pending").count(),
            "pbookings": hospital.bookings.all().filter(status = 'Pending').count(),

        }

        return render(request, self.template_name, {"hospital": hospital, "metadata": metadata})

hospital_details = HospitalDetails.as_view()

class EditDoctor(View):
    template_name = "editdoctor.html"

    @method_decorator(login_required(login_url="/login"))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        doctor_id = self.kwargs.get('did')
        hospital = self.request.user.hospital
        departments = hospital.departments.all()
        doctor_tochange = Doctor.objects.get(id=int(doctor_id))
        return render(request, self.template_name, {"did": doctor_tochange.department.id if doctor_tochange.department else 1, "departments": departments, "tochange": doctor_tochange, "name": hospital.name, "logo": hospital.logo.url})
    
    def post(self, request, *args, **kwargs):
        name = request.POST.get("name")
        doctor_id = self.kwargs.get('did')
        hospital = self.request.user.hospital
        departments = hospital.departments.all()
        doctor_tochange = Doctor.objects.get(id=int(doctor_id))
        department = request.POST.get("department", None)
        print("RECEIVED ", department)
        try:
            doctor_tochange.name = name
            doctor_tochange.department = Department.objects.get(id=int(department))
            doctor_tochange.save()
            return HttpResponseRedirect(reverse("doctors"))
        
        except:
            return render(request, self.template_name, {"did": doctor_tochange.department.id if doctor_tochange.department else 1, "departments": departments, "tochange": doctor_tochange, "name": hospital.name, "logo": hospital.logo.url})

edit_doctor = EditDoctor.as_view()

class EditDepartment(View):
    template_name = "editdepartment.html"

    @method_decorator(login_required(login_url="/login"))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


    def get(self, request, *args, **kwargs):
        department_id = self.kwargs.get('did')
        hospital = self.request.user.hospital
        department_tochange = Department.objects.get(id=int(department_id))
        return render(request, self.template_name, {"tochange": department_tochange, "name": hospital.name, "logo": hospital.logo.url})

    def post(self, request, *args, **kwargs):
        name = request.POST.get("name")
        department_id = self.kwargs.get('did')
        hospital = self.request.user.hospital
        department_tochange = Department.objects.get(id=int(department_id))

        try:
            department_tochange.name = name
            department_tochange.save()

            return HttpResponseRedirect(reverse("departments"))
        
        except:
            return render(request, self.template_name, {"tochange": department_tochange, "name": hospital.name, "logo": hospital.logo.url})
        
edit_department = EditDepartment.as_view()

class AddDoctor(View):
    template_name = "adddoctor.html"
    
    @method_decorator(login_required(login_url="/login"))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        hospital = self.request.user.hospital
        departments = hospital.departments.all()
        return render(request, self.template_name, {"departments": departments, "name": hospital.name, "logo": hospital.logo.url})

    def post(self, request):
        hospital = request.user.hospital
        name = request.POST.get("name", None)
        department = request.POST.get('department', None)
        departments = hospital.departments.all()
        print("CREATE DOCTOR RECEIVED DEPARMENT ", departments)
        try:
            doctor = Doctor.objects.create(
                hospital = hospital,
                name = name,
                department = Department.objects.get(id=int(department))

            )

            doctor.save()

            return HttpResponseRedirect(reverse("doctors"))
        
        except Exception as err:
            return render(request, self.template_name, {"departments": departments, "name": hospital.name, "logo": hospital.logo.url})
            


add_doctor = AddDoctor.as_view()


class LoginView(View):
    template_name = "login.html"

    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        email = request.POST.get('email', None)
        password = request.POST.get('password', None)

        if (email and password):
            check = get_user_model().objects.filter(email=email)

            if (check.count() > 0):
                user = authenticate(request, username=email, password=password)

                if user is not None:
                    if hasattr(user, 'hospital'):
                        if (user.hospital.is_profile_completed == False):
                            return HttpResponseRedirect(reverse('completeprofilehospital'))
                        
                        if (user.hospital.is_approved == False):
                            return HttpResponseRedirect(reverse('waitingverification'))
                        
                        login(request, user)
                        return HttpResponseRedirect(reverse('dashboard'))
                    
                    if (user.is_superuser):
                        login(request, user)
                        return HttpResponseRedirect('/admin')
                else:
                    return render(request, self.template_name, {"message": 'Unable to login incorrect credentials'})
            
            else:
                return render(request, self.template_name, {"message": 'User does not exist'})
        
        else:
            return render(request, self.template_name, {"message": "We don't accept empty fields"})

                

                        

    
login_view = LoginView.as_view()
                

