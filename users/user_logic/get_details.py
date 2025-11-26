import os
import json
from django.conf import settings
from django.http import JsonResponse
from users.models import Doctor
from aviara.helpers.image_operations import get_image_url
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def get_doctor_details(request):
    if request.method == 'GET':
        
        user_id = request.GET.get('user_id')
        if not user_id:
            return JsonResponse({'error': 'User ID is required'}, status=400)

        doctor_obj = Doctor.objects.filter(user_id=user_id).first()
        if doctor_obj:
            # make the clinic logo url
            if doctor_obj.clinic.logo:
                image_path = os.path.join(settings.MEDIA_ROOT, doctor_obj.clinic.logo)
                logo_url = get_image_url(request,image_path)
                if doctor_obj.profile_picture:
                    profile_picture_path = os.path.join(settings.MEDIA_ROOT, doctor_obj.profile_picture)
                    profile_picture_url = get_image_url(request,profile_picture_path)
                else:
                    profile_picture_url = None
            else:
                logo_url = None
            
            doctor_details = {
                'doctor_id': doctor_obj.id,
                'doctor_name': doctor_obj.user.full_name,
                'doctor_profile_picture': profile_picture_url,
                'doctor_specialization': doctor_obj.specialization,
                'doctor_license_number': doctor_obj.license_number,
                'doctor_experience': doctor_obj.years_of_experience,
                'doctor_hire_date': doctor_obj.hire_date,
                'doctor_clinic_id': doctor_obj.clinic.id,
                'doctor_clinic_logo': logo_url, # logo url
                'doctor_clinic_name': doctor_obj.clinic.name,
                'doctor_clinic_address': doctor_obj.clinic.address,
                'doctor_clinic_unit': doctor_obj.clinic.unit,
                'doctor_clinic_city': doctor_obj.clinic.city,
                'doctor_clinic_state': doctor_obj.clinic.state,
                'doctor_clinic_zip': doctor_obj.clinic.zip,
                'doctor_clinic_contact_number': doctor_obj.clinic.contact_number,
                'total_patient_records': doctor_obj.patients.count(),
                'doctor_email': doctor_obj.user.email,
            }
            return JsonResponse({'doctor': doctor_details}, status=200)
        else:
            return JsonResponse({'error': 'Doctor not found'}, status=404)

@csrf_exempt
def get_patient_details(request):
    pass