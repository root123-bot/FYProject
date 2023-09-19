from django.db import models
from django.contrib.auth import get_user_model


# Create your models here.
class Hospital(models.Model):
    user = models.OneToOneField(
        get_user_model(), on_delete=models.CASCADE, related_name="hospital"
    )
    name = models.CharField(max_length=255, blank=True, null=True)
    logo = models.ImageField(upload_to="images/", blank=True, null=True)
    license = models.ImageField(upload_to="images/", blank=True, null=True)
    coords = models.CharField(max_length=255, blank=True, null=True)
    physical_address = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=255, default="hospital")
    is_profile_completed = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.name if self.name else "None"

    # property
    # def patients_queue(self):
    #     patients = self.wagonjwa.all().count()
    #     return patients


class Doctor(models.Model):
    hospital = models.ForeignKey(
        Hospital, on_delete=models.CASCADE, related_name="madokta"
    )
    name = models.CharField(max_length=250)

    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    department = models.ForeignKey(
        "Department",
        on_delete=models.CASCADE,
        related_name="doctors",
        blank=True,
        null=True,
    )

    # def __str__(self):
    #     return self.name

    property

    def total_patients(self):
        print("IM GET CALLED")
        patient_number = self.hospital.wagonjwa.filter(doctor=self).count()
        print(patient_number)
        return patient_number


class Department(models.Model):
    hospital = models.ForeignKey(
        Hospital, on_delete=models.CASCADE, related_name="departments"
    )
    name = models.CharField(max_length=250)

    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.name

    @property
    def get_patients(self):
        wagonjwa = self.patients.all()
        return wagonjwa

    @property
    def total_patients(self):
        wagonjwa = self.patients.all().count()
        return wagonjwa

    @property
    def total_doctors(self):
        doctors = self.doctors.all().count()
        return doctors


class Patient(models.Model):
    hospital = models.ForeignKey(
        Hospital, on_delete=models.CASCADE, related_name="wagonjwa"
    )
    name = models.CharField(max_length=250)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="patients",
        blank=True,
        null=True,
    )
    doctor = models.ForeignKey(
        Doctor, blank=True, null=True, on_delete=models.SET_NULL
    )  # our status >> 1. Yupo kwenye foleni, 2. Ameshahudumiwa ... PEDNING, TREATED
    status = models.CharField(max_length=200, null=True, blank=True)
    is_using_NHIF = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.name


class NormalUsers(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=255, default="customer")


class HospitalBooking(models.Model):
    patient_name = models.CharField(max_length=500)
    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="bookings",
    )
    phone = models.CharField(max_length=500, blank=True, null=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="bukings",
    )
    status = models.CharField(default="Pending", max_length=500)  # Pending, Done
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.hospital.name if self.hospital.name else "NoHospitalName"
