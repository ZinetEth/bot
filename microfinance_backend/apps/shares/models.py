from django.db import models

# Create your models here.
from django.db import models
from apps.CustomUser.models import CustomUser
from apps.payments.models import Transaction

class SharePurchase(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='share_purchases')
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Amount of share purchased")
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name='share_purchase',
                                       help_text="Associated payment transaction")
    created_at = models.DateTimeField(auto_now_add=True)
    commission_distributed = models.BooleanField(default=False, help_text="True if MLM commission has been distributed for this purchase")

    def __str__(self):
        return f"Share Purchase by {self.user.full_name} for {self.amount} on {self.created_at.strftime('%Y-%m-%d')}"

class Commission(models.Model):
    # Model to track individual commission payments for auditing
    payer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='commissions_paid')
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='commissions_received')
    share_purchase = models.ForeignKey(SharePurchase, on_delete=models.CASCADE, related_name='commissions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    tier = models.IntegerField(help_text="MLM tier (1-5)")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Commission for {self.receiver.full_name} (Tier {self.tier}) from {self.share_purchase.id} - {self.amount}"