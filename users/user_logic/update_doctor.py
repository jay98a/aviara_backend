import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_date
from users.models import Doctor
from clinics.models import Clinic


@csrf_exempt
def update_doctor_details(request, doctor_id):
    """
    Update doctor profile and optionally linked user details.
    PUT /users/doctor/update/<doctor_id>/

    Body (all optional): specialization, license_number, years_of_experience,
    profile_picture, hire_date, clinic_id, full_name. Email is not updatable.
    """
    if request.method != 'PUT':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        doctor = Doctor.objects.get(id=doctor_id)
    except Doctor.DoesNotExist:
        return JsonResponse({'error': 'Doctor not found'}, status=404)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    user = doctor.user

    # Update doctor fields if provided
    if 'specialization' in data:
        doctor.specialization = data['specialization'] or None
    if 'license_number' in data:
        doctor.license_number = data['license_number'] or None
    if 'years_of_experience' in data:
        try:
            doctor.years_of_experience = int(data['years_of_experience'])
        except (TypeError, ValueError):
            pass
    if 'profile_picture' in data:
        doctor.profile_picture = data['profile_picture'] or None
    if 'hire_date' in data:
        val = data['hire_date']
        if val:
            doctor.hire_date = parse_date(val) if isinstance(val, str) else val
        else:
            doctor.hire_date = None
    if 'clinic_id' in data:
        clinic_id = data['clinic_id']
        if clinic_id:
            try:
                clinic = Clinic.objects.get(id=clinic_id)
                doctor.clinic = clinic
            except Clinic.DoesNotExist:
                return JsonResponse({'error': 'Clinic not found'}, status=404)
        else:
            doctor.clinic = None

    doctor.save()

    # Update linked user fields if provided (email is not updatable)
    if 'full_name' in data and data['full_name']:
        user.full_name = data['full_name']
        user.save(update_fields=['full_name'])

    return JsonResponse({
        'message': 'Doctor details updated successfully',
        'doctor_id': str(doctor.id),
        'user_id': str(user.user_id),
    }, status=200)
