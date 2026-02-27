import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from users.models import User, Doctor
from clinics.models import Clinic


@csrf_exempt
def proceeding_clinic_registration(request):
    """
    Called after a user (role=individual) has registered a clinic.
    Accepts user_id and clinic_id; updates user role to doctor and creates
    a Doctor record linked to the clinic.

    POST body: { "user_id": "uuid", "clinic_id": "uuid", "specialization": "...", "license_number": "...", "years_of_experience": 0 }
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    user_id = data.get('user_id')
    clinic_id = data.get('clinic_id')

    if not user_id:
        return JsonResponse({'error': 'user_id is required'}, status=400)
    if not clinic_id:
        return JsonResponse({'error': 'clinic_id is required'}, status=400)

    try:
        user = User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)

    if user.role != 'individual':
        return JsonResponse({
            'error': f'User role must be individual to proceed with clinic registration. Current role: {user.role}'
        }, status=400)

    if hasattr(user, 'doctor_profile') and user.doctor_profile:
        return JsonResponse({
            'error': 'User is already registered as a doctor'
        }, status=400)

    try:
        clinic = Clinic.objects.get(id=clinic_id)
    except Clinic.DoesNotExist:
        return JsonResponse({'error': 'Clinic not found'}, status=404)

    # Update user to doctor role
    user.role = 'doctor'
    user.is_doctor = True
    user.save(update_fields=['role', 'is_doctor'])

    # Optional doctor fields from request
    specialization = data.get('specialization', '') or None
    license_number = data.get('license_number', '') or None
    years_of_experience = data.get('years_of_experience')
    if years_of_experience is not None:
        try:
            years_of_experience = int(years_of_experience)
        except (TypeError, ValueError):
            years_of_experience = 0
    else:
        years_of_experience = 0

    # Create Doctor profile linked to clinic
    doctor = Doctor.objects.create(
        user=user,
        clinic=clinic,
        specialization=specialization,
        license_number=license_number,
        years_of_experience=years_of_experience,
    )

    return JsonResponse({
        'message': 'User registered as doctor under clinic successfully',
        'user_id': str(user.user_id),
        'doctor_id': str(doctor.id),
        'clinic_id': str(clinic.id),
    }, status=200)
