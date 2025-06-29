# your_app/models.py (e.g., tokens/models.py)
from datetime import datetime, timedelta
from django.db import models
from django.conf import settings # <--- ADD THIS IMPORT!

# Make sure CustomUser model is properly imported or referenced in settings
# If your CustomUser is in a specific app, e.g., 'users', and named 'CustomUser',
# then settings.AUTH_USER_MODEL would be 'users.CustomUser'.

from apps.tokens.utils import calculate_expiry, log_token_expiry # Import from your utils file

class TokenBatch(models.Model):
    """
    Represents a batch of tokens assigned to a user, with an expiration date.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('used', 'Used'), # Optional: if tokens can be 'used up' before expiry
    ]

    # CORRECTED LINE: Use settings.AUTH_USER_MODEL
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='token_batches')
    
    count = models.IntegerField(help_text="Number of tokens in this batch.")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(help_text="The date and time this token batch expires.")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    class Meta:
        verbose_name = "Token Batch"
        verbose_name_plural = "Token Batches"
        ordering = ['expires_at'] # Order by expiration date for easy processing

    def __str__(self):
        # Access owner.username directly. If your CustomUser model doesn't have 'username'
        # or it's named differently, adjust this. Most custom user models retain 'username'.
        return (f"Token Batch for {self.owner.username} ({self.count} tokens) "
                f"Expires: {self.expires_at.strftime('%Y-%m-%d %H:%M UTC')} - Status: {self.status}")

    def save(self, *args, **kwargs):
        """
        Overrides save to set expires_at if it's a new instance and not already provided.
        NOTE: In a real application, the `calculate_expiry` function would be called
        when a new TokenBatch is *awarded*, and the `expires_at` would be explicitly
        passed to the constructor or set before calling save. This default is for
        demonstration if `expires_at` is somehow missing on creation.
        """
        # It's better to use timezone.now() if you have USE_TZ=True in settings.py
        # from django.utils import timezone
        # if not self.pk and not self.expires_at:
        #     self.expires_at = timezone.now() + timedelta(days=30)
        
        # Using datetime.utcnow() for consistency with your existing code,
        # but be aware of timezone implications if your Django project uses TIME_ZONE
        if not self.pk and not self.expires_at:
            self.expires_at = datetime.utcnow() + timedelta(days=30)
        super().save(*args, **kwargs)

    def is_expired(self):
        """
        Checks if the token batch has expired and is still marked as 'active'.
        """
        # Ensure comparison is timezone-aware if using TIME_ZONE in Django,
        # or consistently use UTC as per Celery config.
        # It's highly recommended to use Django's timezone.now() for consistency.
        # from django.utils import timezone
        # return self.expires_at < timezone.now() and self.status == 'active'
        return self.expires_at < datetime.utcnow() and self.status == 'active'

    def mark_as_expired(self, reason=""):
        """
        Marks the token batch as expired if it's active and past its expiry date.
        Logs the expiration event.
        """
        if self.status == 'active' and self.is_expired():
            self.status = 'expired'
            self.save(update_fields=['status']) # Only update the status field
            log_token_expiry(self.owner.id, reason if reason else f"Batch {self.id} expired naturally.")
            return True
        return False

    def get_days_left(self):
        """
        Calculates the number of days remaining until expiration. Returns 0 if already expired.
        """
        if self.status == 'active':
            # Use timezone.now() for accurate comparison if USE_TZ=True
            # from django.utils import timezone
            # time_left = self.expires_at - timezone.now()
            time_left = self.expires_at - datetime.utcnow()
            return max(0, time_left.days)
        return 0