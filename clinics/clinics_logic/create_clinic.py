import json
import os
import base64
import random
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from django.conf import settings
from clinics.models import Clinic
from aviara.helpers.image_operations import get_image_url


@csrf_exempt
def create_clinic(request):
    """
    Create a new clinic
    POST /clinics/create/
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            name = data.get('name')
            if not name:
                return JsonResponse({'error': 'Clinic name is required'}, status=400)
            
            # Check if clinic with same name already exists
            if Clinic.objects.filter(name=name).exists():
                return JsonResponse({
                    'error': f'Clinic with name "{name}" already exists'
                }, status=400)
            
            # Handle logo upload if provided
            logo_url = None
            logo_base64 = data.get('logo') if data.get('logo') else None
            
            if logo_base64:
                try:
                    # Create random image name
                    clinic_uuid = str(uuid.uuid4())[:8]
                    img_name = f"clinic_{clinic_uuid}_{random.randint(1000, 9999)}"
                    
                    # Decode the base64 image
                    image_data = base64.b64decode(logo_base64)
                    image_file = ContentFile(image_data, name=f"{img_name}.jpg")
                    
                    # Create clinic logos directory if it doesn't exist
                    logos_dir = os.path.join(settings.MEDIA_ROOT, 'clinics')
                    os.makedirs(logos_dir, exist_ok=True)
                    
                    # Save the image file
                    image_path = os.path.join(logos_dir, f"{img_name}.jpg")
                    with open(image_path, 'wb') as f:
                        f.write(image_data)
                    
                    # Get accessible URL using helper function
                    logo_url = get_image_url(request, image_path)
                    if not logo_url:
                        return JsonResponse({
                            'error': 'Failed to generate logo URL'
                        }, status=500)
                    
                except Exception as e:
                    return JsonResponse({
                        'error': f'Error processing logo image: {str(e)}'
                    }, status=400)
            
            # Create clinic
            clinic = Clinic.objects.create(
                name=name,
                address=data.get('address', ''),
                unit=data.get('unit', ''),
                city=data.get('city', ''),
                state=data.get('state', ''),
                zip=data.get('zip', ''),
                contact_number=data.get('contact_number', ''),
                timezone=data.get('timezone', ''),
                logo=logo_url if logo_url else None
            )
            
            return JsonResponse({
                'message': 'Clinic created successfully',
                'clinic_id': str(clinic.id),
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
            }, status=201)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

