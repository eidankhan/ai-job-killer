// --- 1. HARDCODED CONFIG (Standalone) ---
const API_BASE_URL = 'http://127.0.0.1:8000';

// --- 2. HARDCODED AUTH-UI HELPER (Standalone) ---
function setupAuthUI(buttonSelector, alertSelector) {
    const $button = $(buttonSelector);
    const $alert = $(alertSelector);
    const $btnText = $button.find('.btn-text');
    const $spinner = $button.find('.spinner-border');

    return {
        showLoading: () => {
            $btnText.hide();
            $spinner.show();
            $button.prop('disabled', true);
            $alert.hide().removeClass('alert-danger alert-success');
        },
        hideLoading: () => {
            $btnText.show();
            $spinner.hide();
            $button.prop('disabled', false);
        },
        showError: (message) => {
            $alert.text(message).addClass('alert-danger').show();
        },
        showSuccess: (message) => {
            $alert.text(message).addClass('alert-success').show();
        }
    };
}

// --- 3. PAGE LOGIC (This runs after the page loads) ---
$(document).ready(function () {

    // --- STATE ---
    let userEmail = '';

    // --- SETUP ---
    const requestUI = setupAuthUI('#request-button', '#request-alert');
    const resetUI = setupAuthUI('#reset-button', '#reset-alert');

    // --- EVENT LISTENERS ---

    // This is the pattern from your working signup.js
    $('#request-form').on('submit', function (e) {
        // This is the critical line that stops the reload
        e.preventDefault();
        handleRequestCode();
    });

    // This is the pattern from your working signup.js
    $('#reset-form').on('submit', function (e) {
        // This is the critical line that stops the reload
        e.preventDefault();
        handleResetPassword();
    });


    /**
     * Handles STEP 1: Requesting the password reset code
     */
    function handleRequestCode() {
        const email = $('#forgot-email').val();

        if (!email) {
            requestUI.showError('Please enter your email address.');
            return;
        }

        requestUI.showLoading();
        userEmail = email; // Store email for next step

        $.ajax({
            url: `${API_BASE_URL}/auth/send-forgot-password-code`,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ email: email }),

            success: function (data) {
                // Store in case of page refresh
                localStorage.setItem('passwordResetEmail', email);

                requestUI.hideLoading();
                $('#user-email-placeholder').text(userEmail);
                $('#request-card').hide();
                $('#reset-card').fadeIn();
            },

            error: function (xhr) {
                requestUI.hideLoading();
                let errorMsg = 'Could not send reset code. Please check your email.';
                if (xhr.responseJSON && xhr.responseJSON.detail) {
                    if (typeof xhr.responseJSON.detail === 'string') {
                        errorMsg = xhr.responseJSON.detail;
                    }
                }
                requestUI.showError(errorMsg);
            }
        });
    }

    /**
     * Handles STEP 2: Submitting the code and new password
     */
    function handleResetPassword() {
        const code = $('#reset-code').val();
        const newPassword = $('#reset-password').val();
        const confirmPassword = $('#reset-password-confirm').val();

        // Check for email in state, then localStorage (if user refreshed)
        if (!userEmail) {
            userEmail = localStorage.getItem('passwordResetEmail');
            if (!userEmail) {
                resetUI.showError("Session expired. Please start over.");
                return;
            }
        }

        if (newPassword !== confirmPassword) {
            resetUI.showError('Passwords do not match.');
            return;
        }

        resetUI.showLoading();

        $.ajax({
            url: `${API_BASE_URL}/auth/reset-password`,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                email: userEmail,
                code: code,
                new_password: newPassword
            }),

            success: function (data) {
                localStorage.removeItem('passwordResetEmail'); // Clean up
                resetUI.hideLoading();
                resetUI.showSuccess('Password reset! Redirecting to login...');

                setTimeout(() => {
                    // *** THIS IS THE RECOMMENDED ALTERNATIVE ***
                    // It's better than .href because it prevents user
                    // from clicking "Back" and seeing this page again.
                    window.location.replace("login.html");
                }, 2000);
            },

            error: function (xhr) {
                resetUI.hideLoading();
                let errorMsg = 'Invalid code or expired request.';
                if (xhr.responseJSON && xhr.responseJSON.detail) {
                    if (typeof xhr.responseJSON.detail === 'string') {
                        errorMsg = xhr.responseJSON.detail;
                    }
                }
                resetUI.showError(errorMsg);
            }
        });
    }

    // --- Pre-fill Step 2 if user reloads ---
    const storedEmail = localStorage.getItem('passwordResetEmail');
    if (storedEmail) {
        userEmail = storedEmail;
        $('#user-email-placeholder').text(userEmail);
        $('#request-card').hide();
        $('#reset-card').show();
    }
});