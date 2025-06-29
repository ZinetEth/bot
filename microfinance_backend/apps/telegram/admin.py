from django.contrib import admin
from .models import TelegramUser, BotInteractionLog # Only import models defined in this app's models.py

@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'username', 'first_name', 'last_name', 'linked_custom_user', 'created_at', 'updated_at')
    search_fields = ('user_id', 'username', 'first_name', 'last_name')
    list_filter = ('is_bot', 'created_at')
    raw_id_fields = ('linked_custom_user',) # Use raw_id_fields for ForeignKey/OneToOneField to improve performance for many users

@admin.register(BotInteractionLog)
class BotInteractionLogAdmin(admin.ModelAdmin):
    list_display = ('telegram_user', 'command_used', 'timestamp', 'message_text_snippet')
    list_filter = ('command_used', 'timestamp')
    search_fields = ('telegram_user__username', 'telegram_user__first_name', 'message_text', 'command_used')
    readonly_fields = ('telegram_user', 'message_text', 'command_used', 'response_text', 'timestamp') # Logs should be read-only

    def message_text_snippet(self, obj):
        return obj.message_text[:50] + '...' if obj.message_text and len(obj.message_text) > 50 else obj.message_text
    message_text_snippet.short_description = "Message"
    message_text_snippet.admin_order_field = 'message_text' # Allow sorting by message text snippet 