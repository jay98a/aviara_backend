import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def signup(request):
    if request.method == 'POST':
        pass
    return JsonResponse({'message': 'Signup successful'}, status=200)