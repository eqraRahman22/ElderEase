# core/forms.py
from django import forms
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm
from .models import CaregiverProfile, ElderlyProfile, Schedule
from .models import CareSchedule


class SignUpForm(UserCreationForm):
    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'role']

class CaregiverProfileForm(forms.ModelForm):
    class Meta:
        model = CaregiverProfile
        fields = ['name', 'phone', 'address', 'dob', 'gender', 'emergency_contact']
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
        }

class ElderlyProfileForm(forms.ModelForm):
    class Meta:
        model = ElderlyProfile
        fields = ['name', 'dob', 'gender', 'med_condition', 'location']
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
        }

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['elderly', 'date', 'start_time', 'end_time', 'location', 'task_list', 'hourly_rate']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

      

class CareScheduleForm(forms.ModelForm):
    class Meta:
        model = CareSchedule
        fields = ['elderly', 'date', 'start_time', 'end_time', 'location', 'task_list', 'hourly_rate']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

