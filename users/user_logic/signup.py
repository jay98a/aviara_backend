import json
import uuid
from django.http import JsonResponse
from users.models import User, Doctor, Patient
from clinics.models import Clinic
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def signup(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name')
        middle_name = data.get('middle_name')
        last_name = data.get('last_name')
        # TODO: change the password to encryped for security reasons
        role = data.get('role')
        if role == 'doctor':
            is_doctor = True
            specialization = data.get('specialization')
            license_number = data.get('license_number')
            years_of_experience = data.get('years_of_experience')
            clinic_id = data.get('clinic_id') if data.get('clinic_id') else None
            if not specialization or not license_number or not years_of_experience:
                return JsonResponse({'error': 'All fields are required'}, status=400)
        elif role == 'patient':
            is_doctor = False

        else:
            return JsonResponse({'error': 'Invalid role'}, status=400)

        if middle_name:
            full_name = first_name + ' ' + middle_name + ' ' + last_name
        else:
            full_name = first_name + ' ' + last_name


        if not email or not password or not full_name or not role:
            return JsonResponse({'error': 'All fields are required'}, status=400)
        
        user_obj = User.objects.create(email=email, password=password,
                                       role=role, full_name=full_name,
                                       is_active=True, is_doctor=is_doctor)
        user_obj.save()
        if role == 'doctor':
            clinic_obj = Clinic.objects.filter(id=clinic_id).first()
            if not clinic_obj:
                return JsonResponse({'error': 'Clinic not found'}, status=404)
            doctor_obj = Doctor.objects.create(user=user_obj, specialization=specialization,
                                               license_number=license_number,
                                               years_of_experience=years_of_experience,
                                               clinic=clinic_obj)
            doctor_obj.save()
        elif role == 'patient':
            patient_obj = Patient.objects.create(user=user_obj)
            patient_obj.save()


    return JsonResponse({'message': 'Signup successful'}, status=200)