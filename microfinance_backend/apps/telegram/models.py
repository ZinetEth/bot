from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.CustomUser.models import CustomUser # Import your CustomUser model

class TelegramUser(models.Model):
    """
    Stores information about a Telegram user interacting with the bot/Mini App.
    Linked to a CustomUser if they register.
    """
    user_id = models.BigIntegerField(
        unique=True,
        primary_key=True, # Telegram user_id is unique and can serve as PK
        help_text=_("Unique Telegram user ID.")
    )
    first_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text=_("Telegram user's first name.")
    )
    last_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text=_("Telegram user's last name.")
    )
    username = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text=_("Telegram user's username (if set).")
    )
    is_bot = models.BooleanField(
        default=False,
        help_text=_("True if this Telegram user is a bot.")
    )
    language_code = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text=_("Language code of the Telegram client.")
    )
    # Link to your CustomUser model after registration
    linked_custom_user = models.OneToOneField(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='telegram_profile',
        help_text=_("The CustomUser account linked to this Telegram profile.")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username or self.first_name} ({self.user_id})"

    class Meta:
        verbose_name = _("Telegram User")
        verbose_name_plural = _("Telegram Users")

class BotInteractionLog(models.Model):
    """
    Logs interactions with the Telegram bot for auditing and debugging.
    """
    telegram_user = models.ForeignKey(
        TelegramUser,
        on_delete=models.CASCADE,
        related_name='interactions',
        help_text=_("The Telegram user involved in this interaction.")
    )
    message_text = models.TextField(
        blank=True,
        null=True,
        help_text=_("The text of the incoming message or command.")
    )
    command_used = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text=_("The specific command used (e.g., /start, /help).")
    )
    response_text = models.TextField(
        blank=True,
        null=True,
        help_text=_("The text of the bot's response.")
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text=_("Timestamp of the interaction.")
    )

    def __str__(self):
        return f"Interaction by {self.telegram_user.username} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        verbose_name = _("Bot Interaction Log")
        verbose_name_plural = _("Bot Interaction Logs")
        ordering = ['-timestamp']
