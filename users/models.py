import uuid
from django.db import models
from datetime import datetime, timezone
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
    date_joined = models.DateTimeField(default=datetime.now(timezone.utc))

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
    full_name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    date_added = models.DateTimeField(default=datetime.now(timezone.utc))

    class Meta:
        db_table = 'patients'
