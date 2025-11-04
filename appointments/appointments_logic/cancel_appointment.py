import json
from django.http import JsonResponse
from appointments.models import Appointment
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def cancel_appointment(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        appointment_id = data.get('appointment_id')
        
        appointment = Appointment.objects.filter(id=appointment_id).first()
        if not appointment:
            return JsonResponse({'error': 'Appointment not found'}, status=404)
        
        appointment.status = 'cancelled'
        appointment.save()
        
        return JsonResponse({'message': 'Appointment cancelled successfully'}, status=200)