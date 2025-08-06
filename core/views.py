# core/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import SignUpForm
from core.factories.user_factory import UserFactory
from django.contrib import messages

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            print("✅ Form is valid")
            data = form.cleaned_data
            user = UserFactory.create_user(data['username'], data['email'], data['password1'], data['role'])

            # ✅ Admin code check
            if data['role'] == 'admin' and request.POST.get('admin_code') not in ['1357', '2468', '2357', '9876']:
                messages.error(request, "Invalid admin code")
                user.delete()
                return redirect('signup')

            messages.success(request, "Account created. Please login.")
            return redirect('login')
        else:
            print("❌ Form errors:", form.errors)
            messages.error(request, "Something went wrong. Please fix the errors.")
    else:
        form = SignUpForm()
    return render(request, 'core/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        user = authenticate(request, username=request.POST['email'], password=request.POST['password'])
        if user:
            login(request, user)
            if user.role == 'caregiver':
                return redirect('caregiver_dashboard')
            elif user.role == 'family':
                return redirect('family_dashboard')
            elif user.role == 'admin':
                return redirect('admin_dashboard')
        else:
            messages.error(request, "Invalid credentials")
    return render(request, 'core/login.html')
# core/views.py
from django.shortcuts import redirect

def redirect_to_login(request):
    return redirect('login')
