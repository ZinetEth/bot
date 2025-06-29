from django.db import transaction
from apps.shares.models import SharePurchase, Commission
from apps.MLM.models import Referral
from apps.CustomUser.models import CustomUser
from decimal import Decimal

class ShareService:
    MLM_COMMISSION_PERCENTAGE = Decimal('0.05') # 5% total commission
    MLM_TIER_PERCENTAGES = { # Example distribution across tiers
        1: Decimal('0.50'),  # 50% of 5% = 2.5% of purchase
        2: Decimal('0.25'),  # 25% of 5% = 1.25% of purchase
        3: Decimal('0.15'),  # 15% of 5% = 0.75% of purchase
        4: Decimal('0.07'),  # 7% of 5% = 0.35% of purchase
        5: Decimal('0.03'),  # 3% of 5% = 0.15% of purchase
    }
    MAX_MLM_TIERS = 5

    @classmethod
    def process_share_purchase_from_transaction(cls, transaction_obj):
        """
        Processes a share purchase from an APPROVED or POSTED transaction.
        Distributes MLM commissions if applicable.
        """
        if transaction_obj.status not in ['APPROVED', 'POSTED']:
            # Only process if the transaction is approved or already posted to Mifos
            return

        with transaction.atomic():
            # Create the SharePurchase record
            share_purchase, created = SharePurchase.objects.get_or_create(
                transaction=transaction_obj,
                defaults={
                    'user': transaction_obj.user,
                    'amount': transaction_obj.amount,
                }
            )

            if not created and share_purchase.commission_distributed:
                # Share purchase already processed and commission distributed
                return

            if share_purchase.commission_distributed:
                # Already processed. This could happen if called multiple times.
                # Consider logging or raising an error if this should not happen.
                return

            # Distribute MLM commissions
            cls._distribute_mlm_commission(share_purchase)

            # Mark commission as distributed
            share_purchase.commission_distributed = True
            share_purchase.save()

    @classmethod
    def _distribute_mlm_commission(cls, share_purchase):
        """
        Calculates and distributes MLM commission for a share purchase.
        """
        purchaser = share_purchase.user
        
        # Start with the direct referrer (Tier 1)
        current_user = purchaser
        for tier in range(1, cls.MAX_MLM_TIERS + 1):
            try:
                referral = Referral.objects.get(referee=current_user)
                referrer = referral.referrer

                if referral.is_expired:
                    # Referral has expired, stop distributing commissions up this chain
                    break
                
                # Calculate commission for this tier
                base_commission_amount = share_purchase.amount * cls.MLM_COMMISSION_PERCENTAGE
                tier_commission_percentage = cls.MLM_TIER_PERCENTAGES.get(tier, Decimal('0.00'))
                commission_amount = base_commission_amount * tier_commission_percentage

                if commission_amount > 0:
                    Commission.objects.create(
                        payer=purchaser, # The user who made the share purchase is effectively the payer
                        receiver=referrer,
                        share_purchase=share_purchase,
                        amount=commission_amount,
                        tier=tier
                    )
                
                # Move up the referral chain
                current_user = referrer
            except Referral.DoesNotExist:
                # No more referrers in the chain, stop
                break
            except Exception as e:
                # Log any errors during commission distribution but don't stop the overall process
                print(f"Error distributing MLM commission for share purchase {share_purchase.id} at tier {tier}: {e}")
                break # Stop processing this chain on error