# C:\Users\u\Desktop\New folder\microfinance_backend\apps\telegram\handlers.py

import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes # Assuming ContextTypes is needed for type hints

logger = logging.getLogger(__name__)

# --- Your existing handler functions (async def ...) should remain here ---
# Each handler receives 'update' and 'context'. If you need the bot or application,
# you can access it via context.bot or context.application (after initialization).

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Start command received from user {update.effective_user.id}")
    # Example: If you needed the bot instance, you'd use context.bot
    # bot = context.bot
    await update.message.reply_text("Hello! Welcome to the bot. How can I help you today?")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Help command received from user {update.effective_user.id}")
    await update.message.reply_text("This is the help message. You can use /start to begin.")

async def echo_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Echo message received from user {update.effective_user.id}: {update.message.text}")
    await update.message.reply_text(f"You said: {update.message.text}")

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer() # Acknowledge the callback query
    logger.info(f"Callback query received from user {query.from_user.id}: {query.data}")
    await query.edit_message_text(text=f"You chose: {query.data}")

async def send_user_specific_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Sending user specific menu to user {update.effective_user.id}")
    keyboard = [
        [InlineKeyboardButton("Option 1", callback_data='option_1')],
        [InlineKeyboardButton("Option 2", callback_data='option_2')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Please choose an option:", reply_markup=reply_markup)

async def unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Unknown message received from user {update.effective_user.id}: {update.message.text}")
    await update.message.reply_text("Sorry, I didn't understand that command or message.")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error caught by error_handler: {context.error}")
    # You might want to send a message to the user or log more details
    if update.effective_message:
        await update.effective_message.reply_text("An error occurred. Please try again later.")

# --- If you have ConversationHandler states or other functions, they should remain here ---
# Make sure any states like REGISTER_PHONE etc. are defined directly in this file
# or imported from a utility file that does NOT import from apps.telegram.apps