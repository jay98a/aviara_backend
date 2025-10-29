import json
from django.http import JsonResponse
from users.models import User
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def login(request):

    if request.method == 'POST':
        data = json.loads(request.body)
    
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return JsonResponse({'error': 'Email and password are required'}, status=400)

        user_obj = User.objects.filter(email=email).first()
        if user_obj.password != password:
            return JsonResponse({'error': 'Invalid email or password'}, status=401)
        else:
            if user_obj.is_active:
                return JsonResponse({'message': 'Authentication successful',
                                      'user_id': user_obj.user_id,
                                      'is_doctor':user_obj.is_doctor,
                                    }, status=200)
            else:
                return JsonResponse({'error': 'User is not active'}, status=401)
