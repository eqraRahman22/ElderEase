# core/views.py

from django.shortcuts import render
from .models import CaregiverProfile, ElderlyProfile, Schedule
from .forms import CaregiverProfileForm, ElderlyProfileForm, ScheduleForm
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from .forms import SignUpForm
from core.factories.user_factory import UserFactory
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import CareScheduleForm
from .models import CareSchedule, ElderlyProfile, CaregiverAssignment
from .strategies import AllSchedulesStrategy


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            print("✅ Form is valid")
            data = form.cleaned_data
            user = UserFactory.create_user(
                data['username'], data['email'], data['password1'], data['role'])

            if data['role'] == 'admin' and request.POST.get('admin_code') not in ['1357', '2468', '2357', '9876']:
                messages.error(request, "Invalid admin code")
                user.delete()
                return redirect('signup')

            messages.success(request, "Account created. Please login.")
            return redirect('login')
        else:
            print("❌ Form errors:", form.errors)
            messages.error(
                request, "Something went wrong. Please fix the errors.")
    else:
        form = SignUpForm()
    return render(request, 'core/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        user = authenticate(
            request, username=request.POST['email'], password=request.POST['password'])
        if user:
            login(request, user)
            if user.role == 'caregiver':
                return redirect('caregiver_dashboard')
            elif user.role == 'family':
                return redirect('family_dashboard')
            elif user.role == 'admin':
                # Ensure admin users can access Django Admin without re-authenticating
                changed_flags = False
                if not user.is_staff:
                    user.is_staff = True
                    changed_flags = True
                if not user.is_superuser:
                    user.is_superuser = True
                    changed_flags = True
                if changed_flags:
                    user.save(update_fields=['is_staff', 'is_superuser'])
                # Send directly to Django admin site
                return redirect('admin:index')
        else:
            messages.error(request, "Invalid credentials")
    return render(request, 'core/login.html')

# core/views.py


def redirect_to_login(request):
    return redirect('login')

# core/views.py


@login_required
def caregiver_dashboard(request):
    try:
        profile = request.user.caregiverprofile
    except CaregiverProfile.DoesNotExist:
        profile = None
    elderly_list = ElderlyProfile.objects.all()

    return render(request, 'core/caregiver_dashboard.html', {
        'profile': profile,
        'elderly_list': elderly_list,
    })


@login_required
def create_caregiver_profile(request):
    try:
        existing_profile = request.user.caregiverprofile
        return redirect('caregiver_dashboard')
    except CaregiverProfile.DoesNotExist:
        pass

    if request.method == 'POST':
        form = CaregiverProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, 'Profile created successfully.')
            return redirect('caregiver_dashboard')
    else:
        form = CaregiverProfileForm()
    return render(request, 'core/create_caregiver_profile.html', {'form': form})


@login_required
def confirm_caregiving(request, elderly_id):
    elderly = get_object_or_404(ElderlyProfile, id=elderly_id)
    messages.success(request, f'Caregiving for {elderly.name} confirmed.')
    return redirect('caregiver_dashboard')


@login_required
def family_dashboard(request):
    elderly_list = ElderlyProfile.objects.filter(family_member=request.user)
    return render(request, 'core/family_dashboard.html', {'elderly_list': elderly_list})


@login_required
def create_elderly_profile(request):
    if request.method == 'POST':
        form = ElderlyProfileForm(request.POST)
        if form.is_valid():
            elderly = form.save(commit=False)
            elderly.family_member = request.user
            elderly.save()
            messages.success(request, 'Elderly profile created.')
            return redirect('family_dashboard')
    else:
        form = ElderlyProfileForm()
    return render(request, 'core/create_elderly_profile.html', {'form': form})


@login_required
def set_schedule(request):
    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Schedule set successfully.')
            return redirect('family_dashboard')
    else:
        form = ScheduleForm()
    form.fields['elderly'].queryset = ElderlyProfile.objects.filter(
        family_member=request.user)
    return render(request, 'core/set_schedule.html', {'form': form})


@login_required
def set_schedule(request):
    if request.method == "POST":
        form = CareScheduleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("family_dashboard")
    else:
        form = CareScheduleForm()
        form.fields["elderly"].queryset = ElderlyProfile.objects.filter(
            family_member=request.user)
    return render(request, "core/set_schedule.html", {"form": form})


@login_required
def list_of_people_with_schedules(request):
    strategy = AllSchedulesStrategy()  # Strategy Pattern in use
    schedules = strategy.get_schedules()
    return render(request, "core/list_of_people_with_schedules.html", {"schedules": schedules})


@login_required
def confirm_caregiving(request, schedule_id):
    schedule = get_object_or_404(CareSchedule, id=schedule_id)
    CaregiverAssignment.objects.create(
        schedule=schedule, caregiver=request.user, confirmed=True)
    return redirect("list_of_people_with_schedules")


def admin_dashboard(request):
    return render(request, 'core/admin_dashboard.html')
