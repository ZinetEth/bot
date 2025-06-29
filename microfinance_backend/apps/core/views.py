from django.shortcuts import render

# Create your views here.
# core/views.py
# apps/core/views.py
from django.shortcuts import render

def home_view(request):
    return render(request, 'core/home.html', {}) # Or just 'home.html' if templates configured globally