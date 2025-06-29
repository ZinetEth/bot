// main.js

console.log("main.js script started."); // <<< ADDED LOG

// --- Global Variables and Constants ---
// IMPORTANT: Ensure this is your CURRENT active ngrok URL!
const BACKEND_BASE_URL = 'https://e7d8-102-218-50-67.ngrok-free.app';

// UI Elements (Make sure these IDs match your index.html)
// Ensure these variables are correctly assigned from your HTML
let loadingView = document.getElementById('loading-view');
let registrationView = document.getElementById('registration-view');
let dashboardView = document.getElementById('dashboard-view');
let successMessage = document.getElementById('success-message');
let errorMessage = document.getElementById('error-message');
const initData = Telegram.WebApp.initData || "";
// Defensive checks to ensure elements exist before accessing them
if (!loadingView || !registrationView || !dashboardView || !successMessage || !errorMessage) {
    console.error(
        "One or more required UI elements (loadingView, registrationView, dashboardView, successMessage, errorMessage) were not found in the HTML. Please verify that all element IDs are correct in your index.html."
    );
    // Optionally, you could set these to empty strings or null to avoid further errors     
    loadingView = null;
    registrationView = null;            
}
// Registration Form Elements
const phoneNumberInput = document.getElementById('phone-number-input');
const referralCodeInput = document.getElementById('referral-code-input');
const registerButton = document.getElementById('register-button');

// Dashboard Elements
const dashboardUsername = document.getElementById('dashboard-username');
const dashboardPhoneNumber = document.getElementById('dashboard-phone-number');
const dashboardTelegramUsername = document.getElementById('dashboard-telegram-username');
const dashboardShareBalance = document.getElementById('dashboard-share-balance');
const dashboardReferralCount = document.getElementById('dashboard-referral-count');
const response = await fetch("https://e7d8-102-218-50-67.ngrok-free.app/miniapp/api/register/", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    initData: initData,
    phone_number: phoneNumber, // other fields as needed
    full_name: fullName,
    national_id: nationalId,
  }),
});


// --- UI Helper Functions ---
function showView(viewElement) {
    console.log("showView function called for:", viewElement ? viewElement.id : "null"); // <<< ADDED LOG

    // Defensive check: Ensure elements are not null before accessing style
    if (loadingView) loadingView.style.display = 'none';
    if (registrationView) registrationView.style.display = 'none';
    if (dashboardView) dashboardView.style.display = 'none';

    // Show the desired view, if it's not null
    if (viewElement) {
        viewElement.style.display = 'block';
    } else {
        console.error("showView was called with a null element:", viewElement); // <<< ADDED ERROR LOG
    }
}

function displayMessage(type, message) {
    if (!successMessage || !errorMessage) { // Defensive check
        console.error("Message display elements not found in HTML!");
        return;
    }

    if (type === 'success') {
        successMessage.textContent = message;
        successMessage.style.display = 'block';
        errorMessage.style.display = 'none';
    } else if (type === 'error') {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
        successMessage.style.display = 'none';
    } else {
        successMessage.style.display = 'none';
        errorMessage.style.display = 'none';
    }
    // Automatically hide after a few seconds
    setTimeout(() => {
        if (successMessage) successMessage.style.display = 'none';
        if (errorMessage) errorMessage.style.display = 'none';
    }, 5000);
}


// --- Backend Communication Functions ---

/**
 * Fetches the user's registration status and dashboard data from the backend.
 */
async function fetchUserStatus() {
    console.log("fetchUserStatus function started."); // <<< ADDED LOG

    // Ensure loadingView is not null before passing to showView
    if (loadingView) {
        showView(loadingView);
    } else {
        console.error("loadingView element is null, cannot show loading view."); // <<< ADDED ERROR LOG
        // Fallback: If loading view not found, perhaps show registration directly
        showView(registrationView);
        window.Telegram.WebApp.ready();
        window.Telegram.WebApp.expand();
        return; // Exit if initial view cannot be set
    }
    
    displayMessage(null); // Clear previous messages

    const initData = window.Telegram.WebApp.initData;
    console.log("Fetching status with InitData:", initData);

    try {
        console.log(`Attempting to fetch from backend URL: ${BACKEND_BASE_URL}/miniapp/api/status/`); // <<< ADDED LOG
        const response = await fetch(`${BACKEND_BASE_URL}/miniapp/api/status/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'microfinance_backend-Telegram-Init-Data': initData, 
            },
            body: JSON.stringify({ initData: initData }) 
        });

        if (!response.ok) {
            const errorText = await response.text(); // Read as plain text
            console.error(`HTTP error! Status: ${response.status}`, errorText);
            throw new Error(`Server responded with ${response.status}: ${errorText}`);
        }

        const data = await response.json(); // Try to parse as JSON only if response.ok is true
        console.log("User Status Response:", data);

        if (data.is_registered) {
            // User is registered, show dashboard
            if (dashboardUsername) dashboardUsername.textContent = data.username || 'N/A';
            if (dashboardPhoneNumber) dashboardPhoneNumber.textContent = data.phone_number || 'N/A';
            if (dashboardTelegramUsername) dashboardTelegramUsername.textContent = data.telegram_username || 'N/A';
            if (dashboardShareBalance) dashboardShareBalance.textContent = data.share_balance || '0.00 ETB';
            if (dashboardReferralCount) dashboardReferralCount.textContent = data.referral_count !== undefined ? data.referral_count : '0';
            
            showView(dashboardView);
            window.Telegram.WebApp.ready(); // Signal WebApp is ready and fully loaded
            window.Telegram.WebApp.expand(); // Expand mini app to full height
        } else {
            // User not registered, show registration form
            showView(registrationView);
            window.Telegram.WebApp.ready(); // Signal WebApp is ready and fully loaded
            window.Telegram.WebApp.expand(); // Expand mini app to full height
        }

    } catch (error) {
        console.error("Error fetching user status:", error);
        displayMessage('error', `Error loading status: ${error.message}. Please try again.`);
        // Fallback to registration view if status check fails
        showView(registrationView); 
        window.Telegram.WebApp.ready();
        window.Telegram.WebApp.expand();
    }
}

/**
 * Handles the user registration process.
 */
async function registerUser() {
    displayMessage(null); // Clear previous messages
    if (registerButton) registerButton.disabled = true; // Disable button to prevent multiple submissions

    const phoneNumber = phoneNumberInput ? phoneNumberInput.value.trim() : '';
    const referralCode = referralCodeInput ? referralCodeInput.value.trim() : '';
    const initData = window.Telegram.WebApp.initData;
    const telegramUser = window.Telegram.WebApp.initDataUnsafe?.user;

    if (!phoneNumber) {
        displayMessage('error', 'Please enter your phone number.');
        if (registerButton) registerButton.disabled = false;
        return;
    }

    if (!telegramUser || !telegramUser.id) {
        displayMessage('error', 'Could not retrieve Telegram user ID. Please try again later.');
        if (registerButton) registerButton.disabled = false;
        return;
    }

    const requestBody = {
        telegram_id: telegramUser.id,
        phone_number: phoneNumber,
        // Only include referral_code if it's not empty
        ...(referralCode && { referral_code: referralCode }), 
    };

    console.log("Registering user with payload:", requestBody);
    console.log("Sending InitData for registration:", initData);

    try {
        const response = await fetch(`${BACKEND_BASE_URL}/miniapp/api/register/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'microfinance_backend-Telegram-Init-Data': initData, // Send InitData in header
            },
            body: JSON.stringify(requestBody),
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error(`HTTP error! Status: ${response.status}`, errorText);
            throw new Error(`Server responded with ${response.status}: ${errorText}`);
        }

        const data = await response.json();
        console.log("Registration Response:", data);

        if (data.success) {
            displayMessage('success', data.message);
            // After successful registration, re-fetch status to show dashboard
            await fetchUserStatus(); 
        } else {
            displayMessage('error', data.message || 'Registration failed. Please try again.');
        }

    } catch (error) {
        console.error("Error during registration:", error);
        displayMessage('error', `Registration error: ${error.message}.`);
    } finally {
        if (registerButton) registerButton.disabled = false; // Re-enable button
    }
}


// --- Event Listeners and Initialization ---

// Initial view: show loading (This runs immediately when the script is parsed)
console.log("Calling showView(loadingView) initially."); // <<< ADDED LOG
showView(loadingView);

// Initialize Telegram WebApp when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log("DOMContentLoaded event fired."); // <<< ADDED LOG
    // Ensure Telegram WebApp object is available
    if (window.Telegram && window.Telegram.WebApp) {
        window.Telegram.WebApp.ready(); // Signal that the WebApp is ready
        window.Telegram.WebApp.expand(); // Expand the Mini App to full height

        // Log InitData for debugging (will be visible in browser console)
        console.log("Telegram WebApp Initialized.");
        console.log("InitData:", window.Telegram.WebApp.initData);
        console.log("InitDataUnsafe (user object, etc.):", window.Telegram.WebApp.initDataUnsafe);

        // Fetch user status immediately after WebApp is ready
        fetchUserStatus();

        // Optional: Show a "Main Button" if your app uses it
        // window.Telegram.WebApp.MainButton.setText("Submit");
        // window.Telegram.WebApp.MainButton.onClick(() => alert("Main button clicked!"));
        // window.Telegram.WebApp.MainButton.show();

    } else {
        console.error("Telegram WebApp object not found. Are you running in Telegram?");
        // Fallback for development outside Telegram (e.g., directly in browser)
        // You might mock initData for testing purposes here
        showView(registrationView); // Show registration form by default if not in Telegram
        displayMessage('error', 'Not running in Telegram. Features might be limited.');
    }

    // Attach event listener to the register button
    if (registerButton) {
        registerButton.addEventListener('click', registerUser);
    } else {
        console.warn("Register button element not found. Registration functionality might not work.");
    }
});