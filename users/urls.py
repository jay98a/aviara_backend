from django.urls import path
from users.user_logic.get_details import get_doctor_details, get_patient_details
from users.user_logic.get_all_patient_records import get_all_patient_records
from users.user_logic.create_patient import create_patient_session
from users.user_logic.patient_intake import (
    submit_patient_info,
    submit_insurance_info,
    submit_medical_history,
    submit_health_wellness,
    submit_consent_signature
)
from users.doctor_notes_logic.doctor_notes import create_doctor_note, get_doctor_notes, remove_doctor_note


urlpatterns = [
    
    # doctor apis
    path('doctor/get_doctor_details', get_doctor_details, name='get_doctor_details'),
    path('doctor/get_patient_details/', get_patient_details, name='get_patient_details'),
    path('doctor/create_doctor_note/', create_doctor_note, name='create_doctor_note'),
    path('doctor/get_doctor_notes/', get_doctor_notes, name='get_doctor_notes'),
    path('doctor/remove_doctor_note/', remove_doctor_note, name='remove_doctor_note'),
    path('doctor/get_all_patient_records/<str:doctor_id>', get_all_patient_records, name='get_all_patient_records'),

    # Patient intake form endpoints
    path('patient/create_patient_session/', create_patient_session, name='create_patient_session'),
    path('patient/submit_patient_info/', submit_patient_info, name='submit_patient_info'),
    path('patient/submit_insurance_info/', submit_insurance_info, name='submit_insurance_info'),
    path('patient/submit_medical_history/', submit_medical_history, name='submit_medical_history'),
    path('patient/submit_health_wellness/', submit_health_wellness, name='submit_health_wellness'),
    path('patient/submit_consent_signature/', submit_consent_signature, name='submit_consent_signature'),
]