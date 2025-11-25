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
    logo = models.TextField()

    class Meta:
        db_table = 'clinics'