# apps/telegram/menus.py
from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from .localization import (
    MAIN_MENU_TEXT, CUSTOMER_MENU_TEXT, STAFF_MENU_TEXT, AUDITOR_MENU_TEXT,
    MY_PROFILE, CHECK_BALANCE, DEPOSIT_MONEY, LOAN_SERVICES, REFERRAL,
    REGISTER_NEW_CUSTOMER, VIEW_PENDING_DEPOSITS, VIEW_CUSTOMER_LIST,
    REVIEW_PENDING_KYC, REVIEW_PENDING_DEPOSITS, # Make sure these are in localization.py
    REVIEW_STAFF_REGISTRATIONS, VIEW_ALL_USERS,
    APPROVE_BUTTON, REJECT_BUTTON, CONFIRM_BUTTON, CANCEL_BUTTON,
    OPERATION_CANCELLED # Ensure OPERATION_CANCELLED is here
)

def get_main_menu(user_obj):
    """Returns the main menu based on user roles."""
    # Ensure user_obj has these attributes. This is a defensive check.
    if hasattr(user_obj, 'is_auditor') and user_obj.is_auditor:
        return get_auditor_menu()
    elif hasattr(user_obj, 'is_staff') and user_obj.is_staff:
        return get_staff_menu()
    else:
        return get_customer_menu()

def get_customer_menu():
    """Returns the keyboard for regular customers."""
    keyboard = [
        [KeyboardButton(MY_PROFILE), KeyboardButton(CHECK_BALANCE)],
        [KeyboardButton(DEPOSIT_MONEY), KeyboardButton(LOAN_SERVICES)],
        [KeyboardButton(REFERRAL)]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

def get_staff_menu():
    """Returns the keyboard for staff members."""
    keyboard = [
        [KeyboardButton(REGISTER_NEW_CUSTOMER)],
        [KeyboardButton(VIEW_PENDING_DEPOSITS), KeyboardButton(VIEW_CUSTOMER_LIST)],
        [KeyboardButton(MY_PROFILE), KeyboardButton(CHECK_BALANCE)] # Staff can also use customer features
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

def get_auditor_menu():
    """Returns the keyboard for auditors."""
    # This is the "approve menu" from a main menu perspective
    keyboard = [
        [KeyboardButton(REVIEW_PENDING_KYC), KeyboardButton(REVIEW_PENDING_DEPOSITS)],
        [KeyboardButton(REVIEW_STAFF_REGISTRATIONS), KeyboardButton(VIEW_ALL_USERS)],
        [KeyboardButton(MY_PROFILE), KeyboardButton(CHECK_BALANCE)] # Auditors can also use customer features
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

def get_yes_no_keyboard():
    """Returns an inline keyboard with Yes/No options for confirmation."""
    keyboard = [
        [
            InlineKeyboardButton(CONFIRM_BUTTON, callback_data='yes'),
            InlineKeyboardButton(CANCEL_BUTTON, callback_data='no')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_confirm_cancel_keyboard():
    """Returns an inline keyboard with Confirm/Cancel options."""
    keyboard = [
        [
            InlineKeyboardButton(CONFIRM_BUTTON, callback_data='confirm'),
            InlineKeyboardButton(CANCEL_BUTTON, callback_data='cancel_operation')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_kyc_review_keyboard(user_id):
    """Returns an inline keyboard for approving/rejecting KYC."""
    # These are the actual "Approve/Reject" buttons for KYC
    keyboard = [
        [
            InlineKeyboardButton(APPROVE_BUTTON, callback_data=f'approve_kyc_{user_id}'),
            InlineKeyboardButton(REJECT_BUTTON, callback_data=f'reject_kyc_{user_id}')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_deposit_review_keyboard(transaction_id):
    """Returns an inline keyboard for approving/rejecting deposits."""
    # These are the actual "Approve/Reject" buttons for Deposits
    keyboard = [
        [
            InlineKeyboardButton(APPROVE_BUTTON, callback_data=f'approve_deposit_{transaction_id}'),
            InlineKeyboardButton(REJECT_BUTTON, callback_data=f'reject_deposit_{transaction_id}')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)