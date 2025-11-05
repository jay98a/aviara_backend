import json
from django.http import JsonResponse
from appointments.models import DoctorNote
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def create_doctor_note(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        doctor_id = data.get('doctor_id')
        note = data.get('note')

        doctor_note = DoctorNote.objects.create(doctor_id=doctor_id, note=note)
        doctor_note.save()

        return JsonResponse({'message': 'Doctor note created successfully'}, status=200)

@csrf_exempt
def get_doctor_notes(request):
    if request.method == 'GET':
        doctor_id = request.GET.get('doctor_id')
        doctor_notes = DoctorNote.objects.filter(doctor_id=doctor_id)
        doctor_notes_list = []
        for doctor_note in doctor_notes:
            doctor_notes_list.append({
                'doctor_note_id': doctor_note.id,
                'doctor_note': doctor_note.note,
                'created_at': doctor_note.created_at
            })
        return JsonResponse({'doctor_notes': doctor_notes_list}, status=200)

@csrf_exempt
def remove_doctor_note(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        doctor_id = data.get('doctor_id')
        doctor_note_id = data.get('doctor_note_id')
        
        doctor_note = DoctorNote.objects.filter(id=doctor_note_id).first()
        if not doctor_note:
            return JsonResponse({'error': 'Doctor note not found'}, status=404)
        doctor_note.delete()
        return JsonResponse({'message': 'Doctor note removed successfully'}, status=200)