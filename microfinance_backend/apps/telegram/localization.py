# apps/telegram/localization.py

# Bot-wide
BOT_USERNAME = "@YourMicrofinanceBot" # REMEMBER TO REPLACE THIS WITH YOUR BOT'S ACTUAL USERNAME
DEFAULT_CURRENCY = "ETB" # Ethiopian Birr, or change to your preferred currency

# General Messages
START_MESSAGE = "Welcome to the Microfinance Bot!"
WELCOME_BACK = "Welcome back, {username}!"
UNAUTHORIZED_ACCESS = "You are not authorized to access this feature."
INVALID_INPUT = "Invalid input. Please try again."
BACK_TO_MAIN_MENU = "Returning to main menu."
OPERATION_CANCELLED = "🚫 Operation Cancelled."
FEATURE_UNDER_DEVELOPMENT = "🚧 This feature is currently under development. Please check back later!"

# Main Menu Options
MAIN_MENU_TEXT = "Please choose an option from the menu below:"
CUSTOMER_MENU_TEXT = "Customer Menu" # <--- This line is definitely here
STAFF_MENU_TEXT = "Staff Menu"
AUDITOR_MENU_TEXT = "Auditor Menu"

MY_PROFILE = "👤 My Profile"
CHECK_BALANCE = "💰 Check Balance"
DEPOSIT_MONEY = "💸 Deposit Money"
LOAN_SERVICES = "🏦 Loan Services"
REFERRAL = "🤝 Referral"

# Staff Specific Menu Options
REGISTER_NEW_CUSTOMER = "➕ Register New Customer"
VIEW_PENDING_DEPOSITS = "📥 View Pending Deposits" # Staff can see, Auditor approves
VIEW_CUSTOMER_LIST = "📋 View Customer List"

# Auditor Specific Menu Options
REVIEW_PENDING_KYC = "📝 Review Pending KYC"
REVIEW_PENDING_DEPOSITS = "✅ Review Pending Deposits"
REVIEW_STAFF_REGISTRATIONS = "📊 Review Staff Registrations"
VIEW_ALL_USERS = "👥 View All Users"

# KYC Flow Messages (Customer Self-Registration)
REQUEST_FULL_NAME = "Please send me your full name (as per your ID):"
REQUEST_NATIONAL_ID = "Please send me your National ID number:"
KYC_SUBMITTED = "✅ Your KYC details have been submitted for review. You will be notified once it's approved."
KYC_APPROVED_SUCCESS = "🎉 Your KYC has been approved! You can now access all customer features."
KYC_REJECTED_MESSAGE = "❌ Your KYC application has been rejected. Please contact support for more details."
KYC_ALREADY_APPROVED = "Your KYC is already approved! You can use all customer features."
KYC_PROFILE_EXISTS = "You already have a pending or approved KYC profile."

# Staff-Assisted Registration Flow Messages
STAFF_REGISTER_START = "Initiating new customer registration. Please provide the following details for the new customer."
STAFF_REGISTER_NAME = "Enter the full name of the new customer:"
STAFF_REGISTER_NATIONAL_ID = "Enter the National ID of the new customer:"
STAFF_REGISTER_USERNAME = "Enter a unique Telegram username for the new customer (or a unique identifier if they don't have a Telegram username):"
STAFF_REGISTER_PHONE = "Enter the phone number for the new customer (e.g., +2519...):"
STAFF_REGISTER_CONFIRM = """
Please confirm the details for the new customer:
Full Name: {full_name}
National ID: {national_id}
Username: {username}
Phone Number: {phone_number}

Is this correct?
"""
STAFF_REGISTER_SUCCESS = "✅ Customer '{username}' successfully registered and approved."
STAFF_REGISTER_CANCEL = "Customer registration cancelled."

# Profile & Balance Messages
YOUR_PROFILE_DETAILS = """
--- 👤 Your Profile ---
Username: {username}
Full Name: {full_name}
National ID: {national_id}
Phone Number: {phone_number}
KYC Status: {kyc_status}
Registration Method: {reg_method}
Mifos Client ID: {mifos_client_id}
---------------------
"""




# REFrale:
REFERRAL_MESSAGE = "You can earn rewards by referring new users! Share your referral code: `{referral_code}`\n\nIf you came here via a referral link, you're all set! Otherwise, you can skip this."
REFERRAL_SUCCESS = "Thank you for using the referral code! Your account has been linked."
NOT_REGISTERED_PROMPT = "It seems you are not registered yet. Please use the /start command to begin."
ACCOUNT_CREATION_FAILED = "Failed to create account. Please try again or contact support."

# ... (any other localization strings below this) ...
YOUR_BALANCE = "💰 Your current balance: {balance} {currency}"
NO_BALANCE_RECORD = "You currently have no balance record. Your balance is 0.00 {currency}."

# Deposit Flow Messages
REQUEST_DEPOSIT_AMOUNT = "Please enter the amount you wish to deposit (e.g., 100.50):"
DEPOSIT_CONFIRMATION = "You are about to deposit {amount} {currency}. Confirm?"
DEPOSIT_SUBMITTED = "✅ Your deposit request for {amount} {currency} has been submitted for review. You will be notified when it's approved."
DEPOSIT_APPROVED_CUSTOMER_MSG = "🎉 Your deposit of {amount} {currency} has been approved and added to your balance!"
DEPOSIT_REJECTED_CUSTOMER_MSG = "❌ Your deposit of {amount} {currency} has been rejected. Please contact support."
DEPOSIT_ALREADY_COMPLETED = "This deposit request has already been processed."

# Loan Flow Messages
LOAN_WELCOME = "Welcome to Loan Services. How can we assist you today?"
APPLY_LOAN = "✍️ Apply for a Loan"
VIEW_LOANS = "📜 View My Loans"
REQUEST_LOAN_AMOUNT = "Please enter the loan amount you wish to apply for:"
LOAN_APPLY_CONFIRM = "You are applying for a loan of {amount} {currency}. Confirm?"
LOAN_APPLIED_SUCCESS = "✅ Your loan application for {amount} {currency} has been submitted for review. You will be notified when it's approved."
LOAN_APPROVED_CUSTOMER_MSG = "🎉 Your loan of {amount} {currency} has been approved and credited to your account!"
LOAN_REJECTED_CUSTOMER_MSG = "❌ Your loan application for {amount} {currency} has been rejected. Please contact support."

# Auditor Review Messages
NO_PENDING_KYC = "No pending KYC applications to review at this time."
REVIEW_KYC_DETAILS = """
--- 📝 KYC Review ---
User: {username}
Full Name: {full_name}
National ID: {national_id}
---------------------
"""
KYC_APPROVED_AUDITOR_CONFIRM = "✅ KYC for {username} (ID: {user_id}) has been approved."
KYC_REJECTED_AUDITOR_CONFIRM = "❌ KYC for {username} (ID: {user_id}) has been rejected."

NO_PENDING_DEPOSITS = "No pending deposit requests to review at this time."
REVIEW_DEPOSIT_DETAILS = """
--- 📥 Deposit Review ---
User: {username} (ID: {user_id})
Amount: {amount} {currency}
Status: {status}
---------------------
"""
DEPOSIT_APPROVED_AUDITOR_CONFIRM = "✅ Deposit for Txn ID {transaction_id} by {username} has been approved."
DEPOSIT_REJECTED_AUDITOR_CONFIRM = "❌ Deposit for Txn ID {transaction_id} by {username} has been rejected."

STAFF_REGISTRATIONS_HEADER = "📊 Recent Staff-Assisted Registrations"
NO_STAFF_REGISTRATIONS = "No staff-assisted registrations found."
STAFF_REG_ENTRY = """
User: {username} (ID: {user_id})
Registered by: {staff_username}
Date: {reg_date}
KYC Status: {kyc_status}
Mifos Client ID: {mifos_client_id}
---
"""

ALL_USERS_HEADER = "👥 All System Users"
NO_USERS_FOUND = "No users found in the system."
USER_ENTRY = """
User: {username} (ID: {user_id})
KYC Status: {kyc_status}
Reg Method: {reg_method}
Mifos Client ID: {mifos_client_id}
---
"""

# Button Labels
APPROVE_BUTTON = "✅ Approve"
REJECT_BUTTON = "❌ Reject"
CONFIRM_BUTTON = "✔️ Confirm"
CANCEL_BUTTON = "✖️ Cancel"