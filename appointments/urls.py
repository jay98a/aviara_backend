from django.urls import path, include
from appointments.appointments_logic.create_appointment import create_appointment
from appointments.appointments_logic.get_appointments import get_appointments
from appointments.appointments_logic.cancel_appointment import cancel_appointment

urlpatterns = [
    path('create/', create_appointment, name='create_appointment'),
    path('get_appointments', get_appointments, name='get_appointments'),
    path('cancel_appointment/', cancel_appointment, name='cancel_appointment'),
]