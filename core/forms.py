# core/forms.py
from django import forms
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm
from .models import CaregiverProfile, ElderlyProfile, Schedule
from .models import CareSchedule
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
import re


class SignUpForm(UserCreationForm):
    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'role']

    def clean_password1(self):
        password = self.cleaned_data.get('password1')

        # Check for uppercase and lowercase
        if not re.search(r'[A-Z]', password) or not re.search(r'[a-z]', password):
            raise ValidationError("Password must contain both uppercase and lowercase letters.")

        # Check for at least one number
        if not re.search(r'\d', password):
            raise ValidationError("Password must contain at least one number.")

        # Check for special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError("Password must contain at least one special character.")

        return password

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

