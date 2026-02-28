import json
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from clinics.models import Clinic, ClinicBusinessHours


def _parse_time(s):
    """Parse 'HH:MM' or 'HH:MM:SS' to time. Returns None for empty/None."""
    if s is None or (isinstance(s, str) and not s.strip()):
        return None
    s = str(s).strip()
    for fmt in ('%H:%M', '%H:%M:%S'):
        try:
            return datetime.strptime(s, fmt).time()
        except ValueError:
            continue
    return None


def _business_hours_to_response(clinic):
    """Build business_hours as list of { day_of_week, slots: [ {open_time, close_time}, ... ] } for days 0-6."""
    hours = ClinicBusinessHours.objects.filter(clinic=clinic).order_by('day_of_week', 'open_time')
    by_day = {}
    for h in hours:
        if h.day_of_week not in by_day:
            by_day[h.day_of_week] = []
        by_day[h.day_of_week].append({
            'open_time': h.open_time.strftime('%H:%M'),
            'close_time': h.close_time.strftime('%H:%M'),
        })
    return [
        {'day_of_week': d, 'slots': by_day.get(d, [])}
        for d in range(7)
    ]


@csrf_exempt
def clinic_business_hours(request, clinic_id):
    """
    PUT/POST: Set business days and hours for a clinic.
    (Use GET /clinics/get/<clinic_id>/ to retrieve clinic details including business_hours.)

    PUT/POST body:
    {
      "business_hours": [
        { "day_of_week": 0, "slots": [ {"open_time": "09:00", "close_time": "13:00"}, {"open_time": "15:00", "close_time": "20:00"} ] },
        { "day_of_week": 1, "slots": [ {"open_time": "09:00", "close_time": "17:00"} ] },
        { "day_of_week": 5, "slots": [] },
        { "day_of_week": 6, "slots": [] }
      ]
    }
    day_of_week: 0=Monday, 1=Tuesday, ..., 6=Sunday. Empty slots = closed that day.
    """
    if request.method not in ('PUT', 'POST'):
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        clinic = Clinic.objects.get(id=clinic_id)
    except Clinic.DoesNotExist:
        return JsonResponse({'error': 'Clinic not found'}, status=404)

    try:
        data = json.loads(request.body)
        hours_list = data.get('business_hours')
        if not isinstance(hours_list, list):
            return JsonResponse({'error': 'business_hours must be a list'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    seen_days = set()
    to_save = []  # list of (day_of_week, open_time, close_time)

    for i, item in enumerate(hours_list):
        if not isinstance(item, dict):
            return JsonResponse({'error': f'business_hours[{i}] must be an object'}, status=400)
        day = item.get('day_of_week')
        if day is None:
            return JsonResponse({'error': f'business_hours[{i}] must have day_of_week (0-6)'}, status=400)
        try:
            day = int(day)
        except (TypeError, ValueError):
            return JsonResponse({'error': f'business_hours[{i}] day_of_week must be 0-6'}, status=400)
        if day < 0 or day > 6:
            return JsonResponse({'error': f'business_hours[{i}] day_of_week must be 0-6 (0=Monday, 6=Sunday)'}, status=400)
        if day in seen_days:
            return JsonResponse({'error': f'Duplicate day_of_week {day} in business_hours'}, status=400)
        seen_days.add(day)

        slots = item.get('slots')
        if not isinstance(slots, list):
            return JsonResponse({'error': f'business_hours[{i}] slots must be a list'}, status=400)

        for j, slot in enumerate(slots):
            if not isinstance(slot, dict):
                return JsonResponse({'error': f'business_hours[{i}].slots[{j}] must be an object'}, status=400)
            open_t = _parse_time(slot.get('open_time'))
            close_t = _parse_time(slot.get('close_time'))
            if open_t is None or close_t is None:
                return JsonResponse({
                    'error': f'business_hours[{i}].slots[{j}] must have open_time and close_time (HH:MM or HH:MM:SS)'
                }, status=400)
            if open_t >= close_t:
                return JsonResponse({
                    'error': f'business_hours[{i}].slots[{j}] open_time must be before close_time'
                }, status=400)
            to_save.append((day, open_t, close_t))

    ClinicBusinessHours.objects.filter(clinic=clinic).delete()
    for day, open_t, close_t in to_save:
        ClinicBusinessHours.objects.create(
            clinic=clinic,
            day_of_week=day,
            open_time=open_t,
            close_time=close_t,
        )

    return JsonResponse({
        'message': 'Clinic business hours updated successfully',
        'clinic_id': str(clinic.id),
        'business_hours': _business_hours_to_response(clinic),
    }, status=200)
