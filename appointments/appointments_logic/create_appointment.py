from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def create_appointment(request):
    if request.method == 'POST':
        pass
    return JsonResponse({'message': 'Appointment created successfully'}, status=200)