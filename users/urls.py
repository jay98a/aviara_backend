from django.urls import path
from users.user_logic.get_details import get_doctor_details, get_patient_details
from users.user_logic.get_all_patient_records import get_all_patient_records
from users.user_logic.create_patient import create_patient
from users.doctor_notes_logic.doctor_notes import create_doctor_note, get_doctor_notes, remove_doctor_note


urlpatterns = [
    
    # doctor apis
    path('doctor/get_doctor_details', get_doctor_details, name='get_doctor_details'),
    path('doctor/get_patient_details/', get_patient_details, name='get_patient_details'),
    path('doctor/create_doctor_note/', create_doctor_note, name='create_doctor_note'),
    path('doctor/get_doctor_notes/', get_doctor_notes, name='get_doctor_notes'),
    path('doctor/remove_doctor_note/', remove_doctor_note, name='remove_doctor_note'),
    path('doctor/get_all_patient_records/<str:doctor_id>', get_all_patient_records, name='get_all_patient_records'),

    # get all patient records
    path('patient/create_patient/', create_patient, name='create_patient'),
]