// signup.js

$(document).ready(function () {

    // --- STATE ---
    // We need to store the email from step 1 to use it in step 2
    let userEmail = '';

    // --- SETUP ---
    // We need two separate UI helpers, one for each form
    const signupUI = setupAuthUI('#signup-button', '#signup-alert');
    const verifyUI = setupAuthUI('#verify-button', '#verify-alert');

    // --- EVENT LISTENERS ---
    $('#signup-form').on('submit', handleSignup);
    $('#verify-form').on('submit', handleVerify);
    $(document).on('click', '#resend-link', handleResend); // For the resend link


    /**
     * Handles STEP 1: Creating the account
     */
    function handleSignup(e) {
        e.preventDefault();

        const name = $('#signup-name').val();
        const email = $('#signup-email').val();
        const password = $('#signup-password').val();
        const passwordConfirm = $('#signup-password-confirm').val();

        // 1. Client-side validation
        if (password !== passwordConfirm) {
            signupUI.showError('Passwords do not match.');
            return;
        }

        // 2. Show loading state
        signupUI.showLoading();

        // 3. Store the email for the next step
        userEmail = email;

        // 4. Make API call
        $.ajax({
            url: `${API_BASE_URL}/auth/signup`,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                name: name,
                email: email,
                password: password
            }),

            success: function (data) {
                // 5a. On Success: Hide signup card, show verify card
                signupUI.hideLoading();
                $('#user-email-placeholder').text(userEmail); // Update email placeholder
                $('#signup-card').hide();
                $('#verify-card').fadeIn();
            },

            error: function (xhr) {
                // 5b. On Error: Hide loading and show error
                signupUI.hideLoading();
                let errorMsg = 'An error occurred during signup.';
                if (xhr.responseJSON && xhr.responseJSON.detail) {
                    if (typeof xhr.responseJSON.detail === 'string') {
                        errorMsg = xhr.responseJSON.detail;
                    } else if (Array.isArray(xhr.responseJSON.detail)) {
                        errorMsg = xhr.responseJSON.detail[0].msg;
                    }
                }
                signupUI.showError(errorMsg);
            }
        });
    }

    /**
     * Handles STEP 2: Verifying the code
     */
    function handleVerify(e) {
        e.preventDefault();

        const code = $('#verify-code').val();

        if (!userEmail) {
            verifyUI.showError("Email not found. Please refresh and try again.");
            return;
        }

        // 1. Show loading state
        verifyUI.showLoading();

        // 2. Make API call
        $.ajax({
            url: `${API_BASE_URL}/auth/verify-email`,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                email: userEmail,
                code: code
            }),

            success: function (data) {
                // 3a. On Success: Show success and redirect to login
                verifyUI.hideLoading();
                verifyUI.showSuccess('Account verified! Redirecting to login...');

                setTimeout(() => {
                    window.location.href = 'login.html';
                }, 2000); // 2-second delay
            },

            error: function (xhr) {
                // 3b. On Error: Hide loading and show error
                verifyUI.hideLoading();
                let errorMsg = 'Invalid verification code.';
                if (xhr.responseJSON && xhr.responseJSON.detail) {
                    if (typeof xhr.responseJSON.detail === 'string') {
                        errorMsg = xhr.responseJSON.detail;
                    }
                }
                verifyUI.showError(errorMsg);
            }
        });
    }

    /**
     * Handles the "Resend Code" link
     */
    function handleResend(e) {
        e.preventDefault();

        if (!userEmail) {
            verifyUI.showError("Email not found. Please refresh and try again.");
            return;
        }

        // Disable link to prevent spam
        const $resendLink = $('#resend-link');
        $resendLink.text('Sending...').css('pointer-events', 'none');

        $.ajax({
            url: `${API_BASE_URL}/auth/resend-verification-code`,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ email: userEmail }),

            success: function () {
                verifyUI.showSuccess('A new code has been sent.');
                // Re-enable link after a delay
                setTimeout(() => {
                    $resendLink.text('Resend').css('pointer-events', 'auto');
                }, 10000); // 10-second cooldown
            },
            error: function () {
                verifyUI.showError('Could not send a new code. Please try again in a moment.');
                // Re-enable link
                $resendLink.text('Resend').css('pointer-events', 'auto');
            }
        });
    }

});