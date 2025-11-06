import json
from django.http import JsonResponse
from users.models import Patient
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def create_patient(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        # general info
        doctor_id = data.get('doctor_id')
        
        #page 1
        first_name = data.get('first_name')
        middle_name = data.get('middle_name')
        last_name = data.get('last_name')
        date_of_birth = data.get('date_of_birth')
        gender = data.get('gender')
        ssn = data.get('ssn')
        phone_number = data.get('phone_number')
        email = data.get('email')
        street_address = data.get('street_address')
        city = data.get('city')
        state = data.get('state')
        zip_code = data.get('zip_code')

        #page 2
        insurance_company = data.get('insurance_company')
        insurance_policy_number = data.get('insurance_policy_number')
        insurance_policy_holder_name = data.get('insurance_policy_holder_name')

        primary_care_physician_name = data.get('primary_care_physician_name')
        primary_care_physician_phone = data.get('primary_care_physician_phone')
        primary_care_clinic_name = data.get('primary_care_clinic_name')

        preferred_pharmacy_name = data.get('preferred_pharmacy_name')
        preferred_pharmacy_address = data.get('preferred_pharmacy_address')
        preferred_pharmacy_phone = data.get('preferred_pharmacy_phone')

        #page 3
        medical_history = data.get('medical_history')
        medications = data.get('medications')
        allergies = data.get('allergies')
        surgeries = data.get('surgeries')
        family_history = data.get('family_history')

        #page 4



        #page 5
        




        return JsonResponse({'message': 'Patient created successfully'}, status=200)