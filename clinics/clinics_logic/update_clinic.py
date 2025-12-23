import json
import os
import base64
import random
import uuid
from urllib.parse import urlparse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from django.conf import settings
from clinics.models import Clinic
from aviara.helpers.image_operations import get_image_url


@csrf_exempt
def update_clinic(request, clinic_id):
    """
    Update an existing clinic
    PUT /clinics/update/<clinic_id>/
    """
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            
            try:
                clinic = Clinic.objects.get(id=clinic_id)
            except Clinic.DoesNotExist:
                return JsonResponse({'error': 'Clinic not found'}, status=404)
            
            # Update fields if provided
            if 'name' in data:
                # Check if new name conflicts with existing clinic
                if Clinic.objects.filter(name=data['name']).exclude(id=clinic_id).exists():
                    return JsonResponse({
                        'error': f'Clinic with name "{data["name"]}" already exists'
                    }, status=400)
                clinic.name = data['name']
            
            if 'address' in data:
                clinic.address = data['address']
            if 'unit' in data:
                clinic.unit = data['unit']
            if 'city' in data:
                clinic.city = data['city']
            if 'state' in data:
                clinic.state = data['state']
            if 'zip' in data:
                clinic.zip = data['zip']
            if 'contact_number' in data:
                clinic.contact_number = data['contact_number']
            if 'timezone' in data:
                clinic.timezone = data['timezone']
            
            # Handle logo upload if provided
            logo_base64 = data.get('logo') if data.get('logo') else None
            
            if logo_base64:
                try:
                    # Delete old logo if it exists
                    if clinic.logo:
                        # Extract file path from URL (handles both absolute and relative URLs)
                        try:
                            # If it's an absolute URL, extract the path
                            if clinic.logo.startswith('http'):
                                parsed_url = urlparse(clinic.logo)
                                logo_path = parsed_url.path
                            else:
                                logo_path = clinic.logo
                            
                            # Convert URL path to file system path
                            if logo_path.startswith(settings.MEDIA_URL):
                                logo_path = logo_path.replace(settings.MEDIA_URL, '')
                            
                            old_logo_path = os.path.join(settings.MEDIA_ROOT, logo_path.lstrip('/'))
                            if os.path.exists(old_logo_path):
                                try:
                                    os.remove(old_logo_path)
                                except Exception:
                                    pass  # Ignore errors when deleting old logo
                        except Exception:
                            pass  # Ignore errors when parsing/deleting old logo
                    
                    # Create random image name
                    clinic_uuid = str(clinic.id)[:8]
                    img_name = f"clinic_{clinic_uuid}_{random.randint(1000, 9999)}"
                    
                    # Decode the base64 image
                    image_data = base64.b64decode(logo_base64)
                    
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
                    clinic.logo = logo_url
                    
                except Exception as e:
                    return JsonResponse({
                        'error': f'Error processing logo image: {str(e)}'
                    }, status=400)
            elif 'logo' in data and data['logo'] is None:
                # If logo is explicitly set to null, remove it
                if clinic.logo:
                    try:
                        # Extract file path from URL (handles both absolute and relative URLs)
                        if clinic.logo.startswith('http'):
                            parsed_url = urlparse(clinic.logo)
                            logo_path = parsed_url.path
                        else:
                            logo_path = clinic.logo
                        
                        # Convert URL path to file system path
                        if logo_path.startswith(settings.MEDIA_URL):
                            logo_path = logo_path.replace(settings.MEDIA_URL, '')
                        
                        old_logo_path = os.path.join(settings.MEDIA_ROOT, logo_path.lstrip('/'))
                        if os.path.exists(old_logo_path):
                            try:
                                os.remove(old_logo_path)
                            except Exception:
                                pass  # Ignore errors when deleting old logo
                    except Exception:
                        pass  # Ignore errors when parsing/deleting old logo
                clinic.logo = None
            
            clinic.save()
            
            return JsonResponse({
                'message': 'Clinic updated successfully',
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
            }, status=200)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)
