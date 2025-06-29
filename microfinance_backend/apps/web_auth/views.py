from django.shortcuts import render

# Create your views here.
# C:\Users\u\Desktop\New folder\microfinance_backend\apps\web_auth\views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm
from apps.CustomUser.models import UserRoles # Import UserRoles for default setting

def register_view(request):
    """
    Handles user registration.
    Displays a form and creates a new CustomUser upon valid submission.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False) # Don't save yet, we need to set role
            user.role = UserRoles.CUSTOMER # Assign default role upon registration
            user.kyc_status = 'PENDING' # Set default KYC status
            user.is_active = True # New users are active by default
            # You might want to auto-generate a strong password here or during account activation
            # For simplicity, if using UserCreationForm, it handles password.
            user.save()
            
            # Log the user in immediately after registration (optional)
            login(request, user)
            return redirect('home') # Redirect to a 'home' page after successful registration
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})