from django.db import models

# Create your models here.
from django.db import models
from apps.CustomUser.models import CustomUser

class KYCProfile(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='kyc_profile')
    national_id_number = models.CharField(max_length=50, unique=True, help_text="National ID number from the document")
    id_document = models.FileField(upload_to='kyc_docs/', help_text="Scanned copy of the National ID document")
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    
    # Fields for staff input and admin approval
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='kyc_created')
    approved_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='kyc_approved')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rejection_reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"KYC for {self.user.full_name} - Status: {self.status}"