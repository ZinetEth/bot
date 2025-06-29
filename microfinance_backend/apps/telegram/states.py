# states.py

# Example: A dictionary to store user states (mapping user_id to their current state)
user_states = {}

# Define your state constants
STATE_NONE = 0
STATE_AWAITING_USERNAME = 1
STATE_AWAITING_PHONE_NUMBER = 2
STATE_AWAITING_PASSWORD = 3
STATE_AWAITING_GF_NAME = 4
STATE_AWAITING_FIRST_NAME =5
STATE_AWAITING_FATHER_NAME = 6
STATE_AWAITING_GRANDFATHER_NAME = 7
STATE_AWAITING_NATIONAL_ID=8 
STATE_AWAITING_PAYMENT_AMOUNT=9
STATE_CONFIRM_PAYMENT=10
STATE_AWAITING_MIFOS_QUERY=11
# Add any other state constants your views.py expects

# You might also have functions or classes related to state management here
# For example:
def set_user_state(user_id, state):
    user_states[user_id] = state

def get_user_state(user_id):
    return user_states.get(user_id, STATE_NONE)