import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers import serialize
from clinics.models import Clinic


@csrf_exempt
def get_clinic(request, clinic_id=None):
    """
    Get a single clinic by ID or get all clinics
    GET /clinics/get/<clinic_id>/ - Get single clinic
    GET /clinics/get/ - Get all clinics
    """
    if request.method == 'GET':
        try:
            if clinic_id:
                # Get single clinic
                try:
                    clinic = Clinic.objects.get(id=clinic_id)
                    return JsonResponse({
                        'clinic': {
                            'id': str(clinic.id),
                            'name': clinic.name,
                            'address': clinic.address,
                            'unit': clinic.unit,
                            'city': clinic.city,
                            'state': clinic.state,
                            'zip': clinic.zip,
                            'contact_number': clinic.contact_number,
                            'timezone': clinic.timezone,
                            'logo': clinic.logo
                        }
                    }, status=200)
                except Clinic.DoesNotExist:
                    return JsonResponse({'error': 'Clinic not found'}, status=404)
            else:
                # Get all clinics
                clinics = Clinic.objects.all().order_by('name')
                clinics_list = []
                for clinic in clinics:
                    clinics_list.append({
                        'id': str(clinic.id),
                        'name': clinic.name,
                        'address': clinic.address,
                        'unit': clinic.unit,
                        'city': clinic.city,
                        'state': clinic.state,
                        'zip': clinic.zip,
                        'contact_number': clinic.contact_number,
                        'timezone': clinic.timezone,
                        'logo': clinic.logo
                    })
                
                return JsonResponse({
                    'clinics': clinics_list,
                    'count': len(clinics_list)
                }, status=200)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

