# C:\Users\u\Desktop\New folder\microfinance_backend\apps\payments\models.py
# (Assuming this is the content of your apps/payments/models.py)

from django.db import models
from django.conf import settings

class Transaction(models.Model):
    METHOD_CHOICES = [
        ('telebirr', 'Telebirr'),
        ('cbe', 'CBE'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    # ADD related_name='payment_transactions' here
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payment_transactions')
    amount = models.DecimalField(max_digits=13, decimal_places=2)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    reference = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    auto_posted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} - {self.amount} {self.method} ({self.status})"