from django.urls import path
from clinics.clinics_logic.create_clinic import create_clinic
from clinics.clinics_logic.get_clinic import get_clinic
from clinics.clinics_logic.update_clinic import update_clinic
from clinics.clinics_logic.delete_clinic import delete_clinic

urlpatterns = [
    path('create/', create_clinic, name='create_clinic'),
    path('get_all/', get_clinic, name='get_all_clinics'),
    path('get/<str:clinic_id>/', get_clinic, name='get_clinic'),
    path('update/<str:clinic_id>/', update_clinic, name='update_clinic'),
    path('delete/<str:clinic_id>/', delete_clinic, name='delete_clinic'),
]