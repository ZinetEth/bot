# your_app/utils.py (e.g., tokens/utils.py)
from datetime import datetime, timedelta

# --- Enhanced Expiration Logic (7 Stages + Logging + Warnings) ---
def calculate_expiry(token_count, tier, has_recent_sale, commission_birr):
    """
    Calculates the expiry duration in days for a token batch based on various factors.
    """
    # Stage-based base expiry in days
    if token_count <= 5:
        base = 5
    elif token_count <= 15:
        base = 7
    elif token_count <= 30:
        base = 10
    elif token_count <= 50:
        base = 15
    elif token_count <= 75:
        base = 20
    elif token_count <= 120:
        base = 25
    else:
        base = 30 # For token_count > 120

    # Tier bonuses
    if tier == 'green':
        base += 3
    elif tier == 'silver':
        base += 5
    elif tier == 'gold':
        base += 7
    elif tier in ['white', 'gray']:
        base = 0  # No reward for these tiers

    # Commission performance bonus
    if commission_birr >= 1000:
        base += 5
    elif commission_birr >= 500:
        base += 3
    elif commission_birr >= 200:
        base += 1

    # Inactivity penalty
    if not has_recent_sale:
        base -= 2

    # Ensure expiry is between 3 and 45 days.
    return max(3, min(base, 45))

# Token Expiry Logger
# IMPORTANT: In a production environment, this should be a Django model (e.g., TokenLog)
# to store expiry events persistently in the database for auditing and debugging.
expired_token_logs = []

def log_token_expiry(user_id, reason):
    """
    Logs a token batch expiration event.
    """
    now = datetime.utcnow().isoformat()
    # In production, save to a database model:
    # TokenExpirationLog.objects.create(user_id=user_id, date=now, reason=reason)
    expired_token_logs.append({"user": user_id, "date": now, "reason": reason})
    print(f"[LOG] User {user_id} token batch expired on {now} with reason: {reason}")

# Token Expiry Warning
# This function would typically be called from a view or another task that
# checks upcoming expirations and sends notifications (e.g., via a messaging service).
def warn_token_expiry(chat_id, token_count, days_left, send_func):
    """
    Sends a warning message to a user about impending token expiration.
    `send_func` would be a function like `telegram_bot.send_message`.
    """
    if days_left in [3, 2, 1]:
        message = f"⚠️ You have {token_count} tokens expiring in {days_left} days."
        send_func(chat_id, message)
    elif days_left == 0:
        message = f"🛑 Your {token_count} tokens have expired today!"
        send_func(chat_id, message)


# Token Visual Bar (optional placeholder)
def get_token_bar(days_left):
    """
    Generates a simple visual bar representing days left for tokens.
    """
    full = int(days_left / 3) # Each '█' represents 3 days
    return '█' * full + '░' * (15 - full) # Max 15 blocks (45 days / 3 days/block)