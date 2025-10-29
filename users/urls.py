from django.urls import path
from users.user_logic.login import login
from users.user_logic.signup import signup
from users.user_logic.get_details import get_doctor_details, get_patient_details

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('login/', login, name='signin'),
    path('get_doctor_details', get_doctor_details, name='get_user_details'),
    path('get_patient_details', get_patient_details, name='get_patient_details'),
]