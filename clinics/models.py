from django.db import models
import uuid


# --------------------
# CLINIC MODEL
# --------------------
class Clinic(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True)
    unit = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    zip = models.CharField(max_length=20, blank=True, null=True)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    timezone = models.CharField(max_length=100, blank=True, null=True)
    logo = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'clinics'


# --------------------
# CLINIC BUSINESS HOURS
# --------------------
class ClinicBusinessHours(models.Model):
    """One time slot per row. Multiple rows per (clinic, day) = multiple slots per day. day_of_week: 0=Monday, 6=Sunday."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='business_hours')
    day_of_week = models.PositiveSmallIntegerField()  # 0=Monday, 6=Sunday
    open_time = models.TimeField()
    close_time = models.TimeField()

    class Meta:
        db_table = 'clinic_business_hours'
        ordering = ['clinic', 'day_of_week', 'open_time']