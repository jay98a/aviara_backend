from django.urls import path, include
from appointments.appointments_logic.create_appointment import create_appointment

urlpatterns = [
    path('create/', create_appointment, name='create_appointment'),
]