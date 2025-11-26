import json
import datetime
import pytz
from django.http import JsonResponse
from clinics.models import Clinic
from appointments.models import Appointment
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def get_appointments(request):
    if request.method == 'GET':
        date = request.GET.get('date')
        doctor_id = request.GET.get('doctor_id')
        clinic_id = request.GET.get('clinic_id')

        clinic_obj = Clinic.objects.filter(id=clinic_id).first()
        if not clinic_obj:
            return JsonResponse({'error': 'Clinic not found'}, status=404)
        
        if not clinic_obj.timezone:
            clinic_timezone = 'EST'
        else:
            clinic_timezone = clinic_obj.timezone

        clinic_timezone = pytz.timezone(clinic_timezone)

        # convert the date to the clinic timezone
        clinic_date = datetime.datetime.strptime(date, '%Y-%m-%d').replace(tzinfo=pytz.utc).astimezone(clinic_timezone)

        clinic_utc_date = clinic_date.astimezone(pytz.utc).date()
       
        
        appointments_list = []
        # get all the appointments for the given date (dates are stored in utc timezone so we need to convert them to the clinic timezone)
        appointments = Appointment.objects.filter(scheduled_time__date=clinic_utc_date, doctor_id=doctor_id, clinic_id=clinic_id)
        for appointment in appointments:
            appointments_list.append({
                'appointment_id': appointment.id,
                'appointment_type': appointment.appointment_type,
                'patinet_id': appointment.patient.id,
                'patient_name': appointment.patient.first_name + ' ' + appointment.patient.last_name,
                'patient_phone': appointment.patient.phone_number,
                'patient_email': appointment.patient.email,
                'scheduled_time': appointment.scheduled_time.astimezone(clinic_timezone).strftime('%Y-%m-%d %H:%M:%S'),
                'status': appointment.status,
                'notes': appointment.notes
            })

        return JsonResponse({'appointments': appointments_list}, status=200)