import json
from django.http import JsonResponse
from appointments.models import Appointment
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def create_appointment(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        doctor_id = data.get('doctor_id')
        patient_id = data.get('patient_id')
        clinic_id = data.get('clinic_id')
        appointment_type = data.get('appointment_type'),
        scheduled_time = data.get('scheduled_time')
        status = data.get('status')
        notes = data.get('notes')

        appointment = Appointment.objects.create(
            doctor_id=doctor_id,
            patient_id=patient_id,
            clinic_id=clinic_id,
            appointment_type=appointment_type if appointment_type else 'Consultation',
            scheduled_time=scheduled_time,
            status=status,
            notes=notes
        )
        
        appointment.save()

        return JsonResponse({'message': 'Appointment created successfully'}, status=200)