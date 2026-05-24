from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CustomUser


def home(request):
    """
    Home page view.
    """
    return render(request, 'home.html')


def register(request):
    """
    User registration view.
    Handles both GET (display form) and POST (process registration).
    """
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validation
        if not all([full_name, email, password, confirm_password]):
            messages.error(request, 'All fields are required.')
            return redirect('register')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')
        
        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return redirect('register')
        
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return redirect('register')
        
        try:
            user = CustomUser.objects.create_user(
                email=email,
                password=password,
                full_name=full_name
            )
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return redirect('register')
    
    return render(request, 'register.html')


def user_login(request):
    """
    User login view.
    Authenticates user with email and password.
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not email or not password:
            messages.error(request, 'Email and password are required.')
            return redirect('login')
        
        try:
            user = CustomUser.objects.get(email=email)
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.full_name}!')
                return redirect('home')  # Change 'home' to your home page URL name
            else:
                messages.error(request, 'Invalid email or password.')
        except CustomUser.DoesNotExist:
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'login.html')


@login_required(login_url='login')
def user_logout(request):
    """
    User logout view.
    """
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


@login_required(login_url='login')
def profile(request):
    """
    User profile view.
    Displays the logged-in user's profile information.
    """
    user = request.user
    return render(request, 'profile.html', {'user': user})

