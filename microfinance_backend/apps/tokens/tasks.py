# your_app/tasks.py (e.g., tokens/tasks.py)
from datetime import datetime, timedelta
from celery import shared_task
from django.db import transaction
from django.contrib.auth.models import User # Or your custom User model
from .models import TokenBatch
from .utils import calculate_expiry, log_token_expiry # Import from your utils file

@shared_task(bind=True)
def check_and_expire_tokens_task(self):
    """
    Celery task to check for and mark expired token batches.
    This task should be run periodically (e.g., daily) by Celery Beat.
    """
    task_id = self.request.id
    self.stdout.write(f"[{datetime.utcnow()}] Task {task_id}: Starting token expiration check.")

    now = datetime.utcnow()
    # Find active token batches whose expiration date is less than or equal to now
    expired_batches = TokenBatch.objects.filter(
        status='active',
        expires_at__lte=now
    )

    expired_count = 0
    for batch in expired_batches:
        with transaction.atomic(): # Use a transaction for atomicity per batch
            # Call the model method to handle status change and logging
            if batch.mark_as_expired():
                expired_count += 1
            else:
                # This case should ideally not happen if query filters correctly,
                # but good for robustness (e.g., if status changed between query and mark_as_expired call)
                log_token_expiry(batch.owner.id, f"Failed to mark batch {batch.id} as expired (status not active or already expired).")

    self.stdout.write(f"[{datetime.utcnow()}] Task {task_id}: Completed. {expired_count} token batches expired.")
    return f"Expired {expired_count} token batches."


@shared_task(bind=True)
def redistribute_rewards_task(self):
    """
    Celery task to periodically redistribute rewards (new token batches)
    based on user performance, tier, or other business rules.
    This task should be run periodically (e.g., weekly) by Celery Beat.
    """
    task_id = self.request.id
    self.stdout.write(f"[{datetime.utcnow()}] Task {task_id}: Starting reward redistribution.")

    # --- Placeholder for Reward Redistribution Logic ---
    # This is the core logic where you determine who gets how many new tokens.
    # You'll need to define how you assess user performance, sales, activity, etc.

    awarded_count = 0
    # Example: Iterate through all users (or filter based on criteria)
    # This assumes a UserProfile model linked to the User model, holding tier, sales, etc.
    # If you don't have a UserProfile, you'll need to define how these attributes are stored
    # and accessed for each user.
    for user in User.objects.all(): # Consider filtering users if many
        # Dummy values for demonstration. Replace with actual logic to fetch
        # user's current tier, recent sale status, and commission.
        # Example: user_profile = UserProfile.objects.get(user=user)
        # tier = user_profile.tier
        # has_recent_sale = user_profile.has_recent_sale
        # commission_birr = user_profile.total_commission_last_period
        
        # --- Dummy Data for Demonstration ---
        dummy_tier = 'green' # Replace with actual user tier
        dummy_has_recent_sale = True # Replace with actual recent sale status
        dummy_commission_birr = 750 # Replace with actual commission amount
        # --- End Dummy Data ---

        # Determine how many tokens to award to this user
        tokens_to_award = 0
        if dummy_tier == 'gold' and dummy_commission_birr >= 1000:
            tokens_to_award = 100
        elif dummy_tier == 'silver' and dummy_commission_birr >= 500:
            tokens_to_award = 50
        elif dummy_tier == 'green' and dummy_commission_birr >= 200:
            tokens_to_award = 20
        # Add more complex logic based on your reward system

        if tokens_to_award > 0:
            # Calculate the expiry for this new batch of tokens
            days_to_expire = calculate_expiry(
                tokens_to_award,
                dummy_tier, # Use actual user tier
                dummy_has_recent_sale, # Use actual recent sale status
                dummy_commission_birr # Use actual commission
            )
            
            expires_at = datetime.utcnow() + timedelta(days=days_to_expire)

            with transaction.atomic(): # Ensure batch creation is atomic
                TokenBatch.objects.create(
                    owner=user,
                    count=tokens_to_award,
                    expires_at=expires_at,
                    status='active'
                )
                awarded_count += 1
                self.stdout.write(f"Awarded {tokens_to_award} tokens to {user.username}. Expires in {days_to_expire} days.")
        else:
            self.stdout.write(f"No tokens awarded to {user.username} based on current criteria.")


    self.stdout.write(f"[{datetime.utcnow()}] Task {task_id}: Reward redistribution completed. {awarded_count} batches awarded.")
    return f"Awarded {awarded_count} new token batches."