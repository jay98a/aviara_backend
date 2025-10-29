from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def get_doctor_details(request):
    pass

@csrf_exempt
def get_patient_details(request):
    pass