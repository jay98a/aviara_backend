import json
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_date
from users.models import (
    User, Patient, PatientInsurance, Medication, Allergen, PatientAllergy,
    SurgicalHistory, FamilyHistory, FamilyHistoryCondition, PatientHealthWellness, PatientConsent
)
from datetime import datetime


@csrf_exempt
def create_patient_session(request):
    """
    Initialize a patient intake session by creating a temporary user with role 'patient'
    and a patient record. Returns patient_id for subsequent steps.
    Always creates a new temporary patient session (GET request).
    """
    if request.method == 'GET':
        try:
            # Generate a unique temporary email that's clearly fake
            # Format: temp_patient_<uuid>@temp.aviara.local
            temp_uuid = uuid.uuid4()
            temp_email = f"temp_patient_{temp_uuid}@temp.aviara.local"
            
            # Ensure email is unique (handle rare collision case)
            while User.objects.filter(email=temp_email).exists():
                temp_uuid = uuid.uuid4()
                temp_email = f"temp_patient_{temp_uuid}@temp.aviara.local"
            
            # Create new temporary user with role patient
            user = User.objects.create(
                email=temp_email,
                password=None,  # No password for temporary patients
                full_name="Temporary Patient",  # Placeholder name
                role='patient',
                is_active=True,
                is_doctor=False
            )
            
            # Create temporary patient record
            patient = Patient.objects.create(
                user=user,
                first_name="",
                middle_name="",
                last_name="",
                intake_completed=False
            )
            
            return JsonResponse({
                'message': 'Temporary patient session created successfully',
                'patient_id': str(patient.id),
                'user_id': str(user.user_id),
                'temp_email': temp_email  # Include temp email for reference
            }, status=201)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed. Use GET request.'}, status=405)


@csrf_exempt
def submit_patient_info(request):
    """
    Step 1: Submit patient basic information
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            patient_id = data.get('patient_id')
            
            if not patient_id:
                return JsonResponse({'error': 'patient_id is required'}, status=400)
            
            try:
                patient = Patient.objects.get(id=patient_id)
            except Patient.DoesNotExist:
                return JsonResponse({'error': 'Patient not found'}, status=404)
            
            # Security check: Prevent resubmission if intake is already completed
            if patient.intake_completed:
                return JsonResponse({
                    'error': 'Patient intake has already been completed. Data cannot be modified.'
                }, status=403)
            
            # Update patient information
            patient.first_name = data.get('first_name', patient.first_name)
            patient.middle_name = data.get('middle_name', patient.middle_name)
            patient.last_name = data.get('last_name', patient.last_name)
            
            dob = data.get('date_of_birth')
            if dob:
                patient.date_of_birth = parse_date(dob) if isinstance(dob, str) else dob
            
            patient.gender = data.get('sex_assigned_at_birth') or data.get('gender', patient.gender)
            patient.ssn = data.get('social_security_number') or data.get('ssn', patient.ssn)
            patient.phone_number = data.get('phone_number', patient.phone_number)
            patient.email = data.get('email_address') or data.get('email', patient.email)
            patient.street_address = data.get('street_address', patient.street_address)
            patient.city = data.get('city', patient.city)
            patient.state = data.get('state', patient.state)
            patient.zip_code = data.get('zip_code', patient.zip_code)
            
            # Update user email if provided (replace temporary email with real email)
            if patient.user:
                new_email = data.get('email_address') or data.get('email')
                if new_email:
                    # Check if it's a temporary email that should be replaced
                    current_email = patient.user.email
                    if current_email and current_email.startswith('temp_patient_') and current_email.endswith('@temp.aviara.local'):
                        # Replace temporary email with real email
                        # Check if the new email already exists for a different user
                        existing_user = User.objects.filter(email=new_email).exclude(user_id=patient.user.user_id).first()
                        if existing_user:
                            return JsonResponse({
                                'error': f'Email {new_email} is already registered to another account'
                            }, status=400)
                        patient.user.email = new_email
                        patient.user.save()
                    elif new_email != current_email:
                        # Email changed, check if new email is available
                        existing_user = User.objects.filter(email=new_email).exclude(user_id=patient.user.user_id).first()
                        if existing_user:
                            return JsonResponse({
                                'error': f'Email {new_email} is already registered to another account'
                            }, status=400)
                        patient.user.email = new_email
                        patient.user.save()
                
                # Update user full_name
                if patient.first_name and patient.last_name:
                    if patient.middle_name:
                        patient.user.full_name = f"{patient.first_name} {patient.middle_name} {patient.last_name}"
                    else:
                        patient.user.full_name = f"{patient.first_name} {patient.last_name}"
                    patient.user.save()
            
            patient.save()
            
            return JsonResponse({
                'message': 'Patient information saved successfully',
                'patient_id': str(patient.id)
            }, status=200)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def submit_insurance_info(request):
    """
    Step 2: Submit insurance and pharmacy information
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            patient_id = data.get('patient_id')
            
            if not patient_id:
                return JsonResponse({'error': 'patient_id is required'}, status=400)
            
            try:
                patient = Patient.objects.get(id=patient_id)
            except Patient.DoesNotExist:
                return JsonResponse({'error': 'Patient not found'}, status=404)
            
            # Security check: Prevent resubmission if intake is already completed
            if patient.intake_completed:
                return JsonResponse({
                    'error': 'Patient intake has already been completed. Data cannot be modified.'
                }, status=403)
            
            # Get or create insurance record
            insurance, created = PatientInsurance.objects.get_or_create(
                patient=patient,
                defaults={}
            )
            
            # Update insurance information
            insurance.insurance_provider_name = data.get('insurance_provider_name', insurance.insurance_provider_name)
            insurance.member_id = data.get('member_id', insurance.member_id)
            insurance.policy_holder_name = data.get('policy_holder_name', insurance.policy_holder_name)
            
            # Preferred Pharmacy
            insurance.preferred_pharmacy_name = data.get('preferred_pharmacy_name', insurance.preferred_pharmacy_name)
            insurance.preferred_pharmacy_address = data.get('preferred_pharmacy_address', insurance.preferred_pharmacy_address)
            insurance.preferred_pharmacy_phone = data.get('preferred_pharmacy_phone', insurance.preferred_pharmacy_phone)
            
            insurance.save()
            
            return JsonResponse({
                'message': 'Insurance information saved successfully',
                'patient_id': str(patient.id)
            }, status=200)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def submit_medical_history(request):
    """
    Step 3: Submit medical history (medications, allergies, surgeries, family history)
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            patient_id = data.get('patient_id')
            
            if not patient_id:
                return JsonResponse({'error': 'patient_id is required'}, status=400)
            
            try:
                patient = Patient.objects.get(id=patient_id)
            except Patient.DoesNotExist:
                return JsonResponse({'error': 'Patient not found'}, status=404)
            
            # Security check: Prevent resubmission if intake is already completed
            if patient.intake_completed:
                return JsonResponse({
                    'error': 'Patient intake has already been completed. Data cannot be modified.'
                }, status=403)
            
            # Handle Current Medications
            medications = data.get('current_medications', [])
            if medications:
                # Delete existing medications
                Medication.objects.filter(patient=patient).delete()
                # Create new medications
                for med in medications:
                    Medication.objects.create(
                        patient=patient,
                        name=med.get('name', ''),
                        dosage=med.get('dosage', ''),
                        frequency=med.get('frequency', '')
                    )
            
            # Handle Allergies
            allergies = data.get('allergies', {})
            if allergies:
                # Delete existing allergies
                PatientAllergy.objects.filter(patient=patient).delete()
                
                # Handle dictionary format: {"Penicillin": "Yes", "Sulfa Drugs": "No", ...}
                if isinstance(allergies, dict):
                    for allergen_name, is_allergic in allergies.items():
                        if allergen_name.lower() == 'other':
                            # Handle other allergies - support both string and array
                            other_allergy = data.get('other_allergy', '')
                            other_allergy_notes = data.get('other_allergy_notes', '')
                            
                            if other_allergy:
                                # Handle array of other allergies
                                if isinstance(other_allergy, list):
                                    for other_item in other_allergy:
                                        if other_item and isinstance(other_item, str):
                                            # Convert to lowercase for consistency
                                            allergen_name_lower = other_item.strip().lower()
                                            if allergen_name_lower:
                                                allergen, _ = Allergen.objects.get_or_create(name=allergen_name_lower)
                                                PatientAllergy.objects.create(
                                                    patient=patient,
                                                    allergen=allergen,
                                                    is_allergic=True,
                                                    notes=other_allergy_notes
                                                )
                                # Handle single string other allergy (backward compatibility)
                                elif isinstance(other_allergy, str) and other_allergy.strip():
                                    allergen_name_lower = other_allergy.strip().lower()
                                    allergen, _ = Allergen.objects.get_or_create(name=allergen_name_lower)
                                    PatientAllergy.objects.create(
                                        patient=patient,
                                        allergen=allergen,
                                        is_allergic=True,
                                        notes=other_allergy_notes
                                    )
                        else:
                            # Convert allergen name to lowercase for consistency
                            allergen_name_lower = allergen_name.strip().lower()
                            allergen, _ = Allergen.objects.get_or_create(name=allergen_name_lower)
                            # Convert string "Yes"/"No" to boolean
                            if isinstance(is_allergic, bool):
                                is_allergic_bool = is_allergic
                            elif isinstance(is_allergic, str):
                                is_allergic_bool = is_allergic.lower() in ['yes', 'true', '1']
                            else:
                                is_allergic_bool = bool(is_allergic)
                            
                            PatientAllergy.objects.create(
                                patient=patient,
                                allergen=allergen,
                                is_allergic=is_allergic_bool
                            )
                # Handle list format: [{"name": "Penicillin", "is_allergic": true}, ...]
                elif isinstance(allergies, list):
                    for allergy_item in allergies:
                        if isinstance(allergy_item, dict):
                            allergen_name = allergy_item.get('name', '')
                            if allergen_name.lower() == 'other':
                                # Handle other allergies from list format
                                other_allergy = data.get('other_allergy', '')
                                if other_allergy:
                                    if isinstance(other_allergy, list):
                                        for other_item in other_allergy:
                                            if other_item and isinstance(other_item, str):
                                                allergen_name_lower = other_item.strip().lower()
                                                if allergen_name_lower:
                                                    allergen, _ = Allergen.objects.get_or_create(name=allergen_name_lower)
                                                    PatientAllergy.objects.create(
                                                        patient=patient,
                                                        allergen=allergen,
                                                        is_allergic=True,
                                                        notes=allergy_item.get('notes', '') or data.get('other_allergy_notes', '')
                                                    )
                                    elif isinstance(other_allergy, str) and other_allergy.strip():
                                        allergen_name_lower = other_allergy.strip().lower()
                                        allergen, _ = Allergen.objects.get_or_create(name=allergen_name_lower)
                                        PatientAllergy.objects.create(
                                            patient=patient,
                                            allergen=allergen,
                                            is_allergic=True,
                                            notes=allergy_item.get('notes', '') or data.get('other_allergy_notes', '')
                                        )
                            else:
                                # Convert allergen name to lowercase
                                allergen_name_lower = allergen_name.strip().lower()
                                allergen, _ = Allergen.objects.get_or_create(name=allergen_name_lower)
                                is_allergic = allergy_item.get('is_allergic', False)
                                PatientAllergy.objects.create(
                                    patient=patient,
                                    allergen=allergen,
                                    is_allergic=bool(is_allergic)
                                )
            
            # Handle Surgical History
            surgeries = data.get('surgical_history', [])
            if surgeries:
                # Delete existing surgeries
                SurgicalHistory.objects.filter(patient=patient).delete()
                # Create new surgeries
                for surgery in surgeries:
                    surgery_date = surgery.get('date')
                    if surgery_date and isinstance(surgery_date, str):
                        surgery_date = parse_date(surgery_date)
                    SurgicalHistory.objects.create(
                        patient=patient,
                        procedure_name=surgery.get('procedure_name', ''),
                        date=surgery_date,
                        notes=surgery.get('notes', '')
                    )
            
            # Handle Family History
            family_history = data.get('family_history', {})
            if family_history:
                # Delete existing family history
                FamilyHistory.objects.filter(patient=patient).delete()
                
                # Handle dictionary format: {"Cancer": true, "Diabetes": false, ...}
                if isinstance(family_history, dict):
                    for condition, has_condition in family_history.items():
                        if condition.lower() != 'other':
                            # Convert condition name to lowercase for consistency
                            condition_lower = condition.strip().lower()
                            # Get or create reusable condition
                            condition_obj, _ = FamilyHistoryCondition.objects.get_or_create(name=condition_lower)
                            # Convert to boolean
                            if isinstance(has_condition, bool):
                                has_condition_bool = has_condition
                            elif isinstance(has_condition, str):
                                has_condition_bool = has_condition.lower() in ['yes', 'true', '1']
                            else:
                                has_condition_bool = bool(has_condition)
                            
                            FamilyHistory.objects.create(
                                patient=patient,
                                condition=condition_obj,
                                has_condition=has_condition_bool
                            )
                        else:
                            # Handle other family history - support both string and array
                            other_condition = data.get('other_family_history', '')
                            if other_condition:
                                # Handle array of other conditions
                                if isinstance(other_condition, list):
                                    for other_item in other_condition:
                                        if other_item and isinstance(other_item, str):
                                            # Convert to lowercase for consistency
                                            condition_lower = other_item.strip().lower()
                                            if condition_lower:
                                                # Get or create reusable condition
                                                condition_obj, _ = FamilyHistoryCondition.objects.get_or_create(name=condition_lower)
                                                FamilyHistory.objects.create(
                                                    patient=patient,
                                                    condition=condition_obj,
                                                    has_condition=True
                                                )
                                # Handle single string other condition (backward compatibility)
                                elif isinstance(other_condition, str) and other_condition.strip():
                                    condition_lower = other_condition.strip().lower()
                                    # Get or create reusable condition
                                    condition_obj, _ = FamilyHistoryCondition.objects.get_or_create(name=condition_lower)
                                    FamilyHistory.objects.create(
                                        patient=patient,
                                        condition=condition_obj,
                                        has_condition=True
                                    )
                # Handle list format: [{"condition": "Cancer", "has_condition": true}, ...]
                elif isinstance(family_history, list):
                    for item in family_history:
                        if isinstance(item, dict):
                            condition = item.get('condition', '')
                            if condition.lower() != 'other':
                                # Convert condition name to lowercase
                                condition_lower = condition.strip().lower()
                                # Get or create reusable condition
                                condition_obj, _ = FamilyHistoryCondition.objects.get_or_create(name=condition_lower)
                                has_condition = item.get('has_condition', False)
                                FamilyHistory.objects.create(
                                    patient=patient,
                                    condition=condition_obj,
                                    has_condition=bool(has_condition)
                                )
                            else:
                                # Handle other family history from list format
                                other_condition = data.get('other_family_history', '') or item.get('other', '')
                                if other_condition:
                                    if isinstance(other_condition, list):
                                        for other_item in other_condition:
                                            if other_item and isinstance(other_item, str):
                                                condition_lower = other_item.strip().lower()
                                                if condition_lower:
                                                    # Get or create reusable condition
                                                    condition_obj, _ = FamilyHistoryCondition.objects.get_or_create(name=condition_lower)
                                                    FamilyHistory.objects.create(
                                                        patient=patient,
                                                        condition=condition_obj,
                                                        has_condition=True
                                                    )
                                    elif isinstance(other_condition, str) and other_condition.strip():
                                        condition_lower = other_condition.strip().lower()
                                        # Get or create reusable condition
                                        condition_obj, _ = FamilyHistoryCondition.objects.get_or_create(name=condition_lower)
                                        FamilyHistory.objects.create(
                                            patient=patient,
                                            condition=condition_obj,
                                            has_condition=True
                                        )
            
            return JsonResponse({
                'message': 'Medical history saved successfully',
                'patient_id': str(patient.id)
            }, status=200)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def submit_health_wellness(request):
    """
    Step 4: Submit health and wellness information
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            patient_id = data.get('patient_id')
            
            if not patient_id:
                return JsonResponse({'error': 'patient_id is required'}, status=400)
            
            try:
                patient = Patient.objects.get(id=patient_id)
            except Patient.DoesNotExist:
                return JsonResponse({'error': 'Patient not found'}, status=404)
            
            # Security check: Prevent resubmission if intake is already completed
            if patient.intake_completed:
                return JsonResponse({
                    'error': 'Patient intake has already been completed. Data cannot be modified.'
                }, status=403)
            
            # Get or create health wellness record
            health_wellness, created = PatientHealthWellness.objects.get_or_create(
                patient=patient,
                defaults={}
            )
            
            # Update health and wellness information
            health_wellness.tobacco_use = data.get('tobacco_use', health_wellness.tobacco_use)
            health_wellness.alcohol_use = data.get('alcohol_use', health_wellness.alcohol_use)
            health_wellness.exercise = data.get('exercise', health_wellness.exercise)
            health_wellness.mental_health = data.get('mental_health', health_wellness.mental_health)
            health_wellness.diet_preferences = data.get('diet_preferences_or_restrictions', health_wellness.diet_preferences)
            health_wellness.current_health_concerns = data.get('current_health_concerns', health_wellness.current_health_concerns)
            
            health_wellness.save()
            
            return JsonResponse({
                'message': 'Health and wellness information saved successfully',
                'patient_id': str(patient.id)
            }, status=200)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def submit_consent_signature(request):
    """
    Step 5: Submit consent and signature information
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            patient_id = data.get('patient_id')
            
            if not patient_id:
                return JsonResponse({'error': 'patient_id is required'}, status=400)
            
            try:
                patient = Patient.objects.get(id=patient_id)
            except Patient.DoesNotExist:
                return JsonResponse({'error': 'Patient not found'}, status=404)
            
            # Security check: Prevent resubmission if intake is already completed
            if patient.intake_completed:
                return JsonResponse({
                    'error': 'Patient intake has already been completed. Data cannot be modified.'
                }, status=403)
            
            # Get or create consent record
            consent, created = PatientConsent.objects.get_or_create(
                patient=patient,
                defaults={}
            )
            
            # Update consent information
            consent.consent_for_treatment = data.get('consent_for_treatment', False)
            consent.authorization_release_medical_info = data.get('authorization_release_medical_info', False)
            consent.assignment_insurance_benefits = data.get('assignment_insurance_benefits', False)
            consent.hipaa_acknowledgment = data.get('hipaa_acknowledgment', False)
            consent.telehealth_consent = data.get('telehealth_consent', False)
            consent.authorization_electronic_communication = data.get('authorization_electronic_communication', False)
            consent.authorization_prescription_history = data.get('authorization_prescription_history', False)
            consent.consent_preventive_health_outreach = data.get('consent_preventive_health_outreach', False)
            
            # Digital signature
            consent.digital_signature_name = data.get('digital_signature_name', consent.digital_signature_name)
            consent.digital_signature = data.get('digital_signature', consent.digital_signature)
            
            dob = data.get('signature_date_of_birth')
            if dob:
                consent.signature_date_of_birth = parse_date(dob) if isinstance(dob, str) else dob
            
            consent.save()
            
            # Mark intake as completed
            patient.intake_completed = True
            patient.save()
            
            return JsonResponse({
                'message': 'Consent and signature saved successfully. Intake form completed.',
                'patient_id': str(patient.id)
            }, status=200)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

