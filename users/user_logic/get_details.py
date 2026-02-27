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
        doctor_id = request.GET.get('doctor_id')
        if not doctor_id:
            return JsonResponse({'error': 'Doctor ID is required'}, status=400)

        try:
            doctor_obj = Doctor.objects.get(id=doctor_id)
        except Doctor.DoesNotExist:
            return JsonResponse({'error': 'Doctor not found'}, status=404)

        # Clinic logo URL (clinic can be null)
        logo_url = None
        if doctor_obj.clinic and doctor_obj.clinic.logo:
            image_path = os.path.join(settings.MEDIA_ROOT, doctor_obj.clinic.logo)
            logo_url = get_image_url(request, image_path)

        # Profile picture URL
        profile_picture_url = None
        if doctor_obj.profile_picture:
            profile_picture_path = os.path.join(settings.MEDIA_ROOT, doctor_obj.profile_picture)
            profile_picture_url = get_image_url(request, profile_picture_path)

        doctor_details = {
            'doctor_id': str(doctor_obj.id),
            'doctor_name': doctor_obj.user.full_name,
            'doctor_profile_picture': profile_picture_url,
            'doctor_specialization': doctor_obj.specialization,
            'doctor_license_number': doctor_obj.license_number,
            'doctor_experience': doctor_obj.years_of_experience,
            'doctor_hire_date': str(doctor_obj.hire_date) if doctor_obj.hire_date else None,
            'doctor_clinic_id': str(doctor_obj.clinic.id) if doctor_obj.clinic else None,
            'doctor_clinic_logo': logo_url,
            'doctor_clinic_name': doctor_obj.clinic.name if doctor_obj.clinic else None,
            'doctor_clinic_address': doctor_obj.clinic.address if doctor_obj.clinic else None,
            'doctor_clinic_unit': doctor_obj.clinic.unit if doctor_obj.clinic else None,
            'doctor_clinic_city': doctor_obj.clinic.city if doctor_obj.clinic else None,
            'doctor_clinic_state': doctor_obj.clinic.state if doctor_obj.clinic else None,
            'doctor_clinic_zip': doctor_obj.clinic.zip if doctor_obj.clinic else None,
            'doctor_clinic_contact_number': doctor_obj.clinic.contact_number if doctor_obj.clinic else None,
            'total_patient_records': doctor_obj.patients.count(),
            'doctor_email': doctor_obj.user.email,
        }
        return JsonResponse({'doctor': doctor_details}, status=200)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def get_patient_details(request):
    pass