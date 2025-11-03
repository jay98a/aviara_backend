import json
from django.http import JsonResponse
from users.models import Doctor
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def get_doctor_details(request):
    if request.method == 'GET':
        
        user_id = request.GET.get('user_id')
        if not user_id:
            return JsonResponse({'error': 'User ID is required'}, status=400)

        doctor_obj = Doctor.objects.filter(user_id=user_id).first()
        if doctor_obj:
            doctor_details = {
                'doctor_id': doctor_obj.id,
                'doctor_name': doctor_obj.user.full_name,
                'doctor_specialization': doctor_obj.specialization,
                'doctor_license_number': doctor_obj.license_number,
                'doctor_experience': doctor_obj.years_of_experience,
                'doctor_clinic_id': doctor_obj.clinic.id,
            }
            return JsonResponse({'doctor': doctor_details}, status=200)
        else:
            return JsonResponse({'error': 'Doctor not found'}, status=404)

@csrf_exempt
def get_patient_details(request):
    pass