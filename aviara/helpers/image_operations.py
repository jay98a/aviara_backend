import os
import base64
from urllib.parse import urljoin
from django.conf import settings

def get_image_url(request,image_path):
    '''
    This function is used to get the image url from the full image path
    request: request object
    image_path: full image path
    '''
    encoded_image = None
    image_url = None
    
    if os.path.exists(image_path):
        image_path_list = image_path.split('/')

        with open(image_path, 'rb') as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
          
        # Compute the relative path of the image from MEDIA_ROOT
        relative_path = os.path.relpath(image_path, settings.MEDIA_ROOT).replace("\\", "/")

        # Construct the absolute URL
        image_url = urljoin(settings.MEDIA_URL, relative_path)

    return request.build_absolute_uri(image_url)  