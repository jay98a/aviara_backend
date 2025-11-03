import uuid
from django.db import models
from django.utils import timezone
from clinics.models import Clinic

# --------------------
# USER MODEL
# --------------------
class User(models.Model):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("patient", "Patient"),
        ("doctor", "Doctor"),
    )

    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100, null=True)
    full_name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="doctor")

    is_active = models.BooleanField(default=True)
    is_doctor = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'users'


# --------------------
# DOCTOR MODEL
# --------------------
class Doctor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="doctor_profile")
    clinic = models.ForeignKey(Clinic, on_delete=models.SET_NULL, null=True, related_name="doctors")
    specialization = models.CharField(max_length=255, blank=True, null=True)
    license_number = models.CharField(max_length=100, blank=True, null=True)
    years_of_experience = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'doctors'

# --------------------
# PATIENT MODEL
# --------------------
class Patient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="patients")
    first_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    ssn = models.CharField(max_length=20, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    street_address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    date_added = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'patients'


class PatientInsurance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="insurances")
    
    insurance_company = models.CharField(max_length=255)
    insurance_policy_number = models.CharField(max_length=255)
    insurance_policy_holder_name = models.CharField(max_length=255)
    insurance_policy_holder_ssn = models.CharField(max_length=20)

    primary_care_physician_name = models.CharField(max_length=255, null=True, blank=True)
    primary_care_physician_phone = models.CharField(max_length=20, null=True, blank=True)
    primary_care_clinic_name = models.CharField(max_length=255, null=True, blank=True)

    preferred_pharmacy_name = models.CharField(max_length=255, null=True, blank=True)
    preferred_pharmacy_address = models.TextField(null=True, blank=True)
    preferred_pharmacy_phone = models.CharField(max_length=20, null=True, blank=True)

    date_added = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'patient_insurances'


class MedicalHistory(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_history')
    condition = models.CharField(max_length=255)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'patient_medical_history'


class Medication(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medications')
    name = models.CharField(max_length=255)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)

    class Meta:
        db_table = 'patient_medications'


class Allergen(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'allergens'

class PatientAllergy(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='allergies')
    allergen = models.ForeignKey(Allergen, on_delete=models.CASCADE)
    is_allergic = models.BooleanField(default=False)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'patient_allergies'

class SurgicalHistory(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='surgeries')
    procedure_name = models.CharField(max_length=255)
    date = models.DateField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'patient_surgeries'

class FamilyHistory(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='family_history')
    condition = models.CharField(max_length=255)
    has_condition = models.BooleanField(default=False)

    class Meta:
        db_table = 'patient_family_history'
