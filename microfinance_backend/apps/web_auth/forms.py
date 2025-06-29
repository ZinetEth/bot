# C:\Users\u\Desktop\New folder\microfinance_backend\apps\web_auth\forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from apps.CustomUser.models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    """
    A custom form for creating new CustomUser instances.
    It includes all the fields required by CustomUser.
    """
    class Meta:
        model = CustomUser
        # Include all fields you want to be visible and editable on registration
        # username is inherited from AbstractUser
        fields = (
            'username', 'telegram_id', 'phone_number', 'first_name',
            'father_name', 'grand_father_name', 'preferred_language',
            'email', # Include if you use email
            # Do NOT include 'role' or 'kyc_status' here, as these are typically set by the system/admin
        )
        # You can add widgets for better UI control, e.g.:
        widgets = {
            'phone_number': forms.TextInput(attrs={'placeholder': '+2519... or 09...'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'Your First Name'}),
            # ... add more as needed
        }

    # Optional: Add clean methods for custom validation if needed, e.g., phone number format
    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        # Add a more robust validation here, similar to what we discussed for the bot
        # For simplicity, let's just check for digits and length for now
        if not phone_number.replace('+', '').isdigit() or len(phone_number) < 9: # Basic check
            raise forms.ValidationError("Please enter a valid phone number.")
        return phone_number

class CustomUserChangeForm(UserChangeForm):
    """
    A custom form for updating CustomUser instances in the admin.
    """
    class Meta:
        model = CustomUser
        fields = (
            'username', 'telegram_id', 'phone_number', 'first_name',
            'father_name', 'grand_father_name', 'preferred_language',
            'email', 'role', 'kyc_status', 'is_active', 'is_staff', 'is_superuser',
            'last_login', 'date_joined', 'groups', 'user_permissions'
        )