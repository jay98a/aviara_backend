import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from clinics.models import Clinic
from users.models import Doctor


@csrf_exempt
def delete_clinic(request, clinic_id):
    """
    Delete a clinic
    DELETE /clinics/delete/<clinic_id>/
    """
    if request.method == 'DELETE':
        try:
            try:
                clinic = Clinic.objects.get(id=clinic_id)
            except Clinic.DoesNotExist:
                return JsonResponse({'error': 'Clinic not found'}, status=404)
            
            # Check if clinic has associated doctors
            doctors_count = Doctor.objects.filter(clinic=clinic).count()
            if doctors_count > 0:
                return JsonResponse({
                    'error': f'Cannot delete clinic. It has {doctors_count} associated doctor(s). Please reassign or remove doctors first.'
                }, status=400)
            
            clinic_name = clinic.name
            clinic.delete()
            
            return JsonResponse({
                'message': f'Clinic "{clinic_name}" deleted successfully'
            }, status=200)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

