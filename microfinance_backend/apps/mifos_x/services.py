import requests
import json
from decouple import config

class MifosService:

    # Get Mifos X base URL and API credentials from environment variables
    # Make sure to set these in your .env file
    MIFOS_BASE_URL = config('MIFOS_BASE_URL', default='http://localhost:8080/fineract-provider/api/v1')
    MIFOS_API_KEY = config('MIFOS_API_KEY', default='YOUR_MIFOS_API_KEY')
    MIFOS_TENANT_ID = config('MIFOS_TENANT_ID', default='default') # Or your specific tenant ID

    HEADERS = {
        'Content-Type': 'application/json',
        'Fineract-Platform-TenantId': MIFOS_TENANT_ID,
        'Authorization': f'Basic {MIFOS_API_KEY}' # Using Basic Auth, replace if Mifos uses Bearer Token or other
    }

    @classmethod
    def _make_api_call(cls, method, endpoint, data=None):
        url = f"{cls.MIFOS_BASE_URL}/{endpoint}"
        try:
            if method == 'GET':
                response = requests.get(url, headers=cls.HEADERS)
            elif method == 'POST':
                response = requests.post(url, headers=cls.HEADERS, data=json.dumps(data))
            elif method == 'PUT':
                response = requests.put(url, headers=cls.HEADERS, data=json.dumps(data))
            elif method == 'DELETE':
                response = requests.delete(url, headers=cls.HEADERS)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error during Mifos API call: {e.response.status_code} - {e.response.text}")
            raise
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error to Mifos API: {e}")
            raise
        except Exception as e:
            print(f"An unexpected error occurred during Mifos API call: {e}")
            raise

    @classmethod
    def get_client_by_external_id(cls, external_id):
        """
        Fetches a Mifos client by their external ID (e.g., Telegram ID or National ID).
        """
        endpoint = f"clients?externalId={external_id}"
        return cls._make_api_call('GET', endpoint)

    @classmethod
    def create_client(cls, client_data):
        """
        Creates a new client in Mifos X.
        `client_data` should be a dictionary matching Mifos's client creation payload.
        """
        endpoint = "clients"
        return cls._make_api_call('POST', endpoint, data=client_data)

    @classmethod
    def deposit_to_savings(cls, client_id, savings_account_id, amount, transaction_date):
        """
        Posts a deposit to a client's savings account in Mifos X.
        `transaction_date` should be in 'DD MMMM YYYY' format (e.g., '15 June 2025').
        """
        endpoint = f"savingsaccounts/{savings_account_id}/transactions?command=deposit"
        data = {
            "locale": "en",
            "dateFormat": "dd MMMM yyyy",
            "transactionDate": transaction_date,
            "transactionAmount": str(amount),
            "paymentTypeId": 1 # Example payment type ID, configure as needed in Mifos
        }
        return cls._make_api_call('POST', endpoint, data=data)

    @classmethod
    def apply_for_loan(cls, loan_application_data):
        """
        Submits a loan application in Mifos X.
        `loan_application_data` should be a dictionary matching Mifos's loan application payload.
        """
        endpoint = "loans"
        return cls._make_api_call('POST', endpoint, data=loan_application_data)

    @classmethod
    def purchase_shares(cls, client_id, share_product_id, quantity, transaction_date):
        """
        Records a share purchase for a client in Mifos X.
        This might be a custom integration or via a journal entry if direct API is not available.
        (Mifos X has a Shares API, but exact endpoint depends on your setup)
        """
        # Placeholder: This is a simplified example. You might need to adjust
        # based on your specific Mifos X Shares API or use Journal Entries.
        endpoint = f"clients/{client_id}/sharesproducts/{share_product_id}/purchases"
        data = {
            "locale": "en",
            "dateFormat": "dd MMMM yyyy",
            "submittedDate": transaction_date,
            "requestedShares": quantity,
            # Add other required fields like share price, payment type, etc.
        }
        return cls._make_api_call('POST', endpoint, data=data)