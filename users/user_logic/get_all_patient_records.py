import json
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from users.models import Patient
from appointments.models import Appointment
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def get_all_patient_records(request, doctor_id):
    if request.method == 'GET':
        if not doctor_id:
            return JsonResponse({'error': 'User ID is required'}, status=400)

        patient_data_list = []
        patient_obj = Patient.objects.filter(doctor_id=doctor_id).all()
        for patient in patient_obj:
            
            patient_active = False
            appointment_obj = Appointment.objects.filter(patient=patient.id).order_by('-scheduled_time').first()
            if appointment_obj:
                # check of last appointment is within 6 months
                
                if appointment_obj.scheduled_time > timezone.now() - timedelta(days=180):
                    patient_active = True
                else:
                    patient_active = False
            else:
                appointment_obj = None

            patient_data = {
                'patient_id': patient.id,
                'patient_name': patient.first_name + ' ' + patient.last_name,
                'patient_dob': patient.date_of_birth,
                'patient_phone': patient.phone_number,
                'patient_email': patient.email,
                'patient_last_appointment': appointment_obj.scheduled_time if appointment_obj else None,
                'patient_active': patient_active
            }
            patient_data_list.append(patient_data)
        if patient_obj:
            return JsonResponse({'patient_list': patient_data}, status=200)
        else:
            return JsonResponse({'error': 'Patient list not found'}, status=404)