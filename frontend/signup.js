// signup.js

$(document).ready(function () {

    // --- SETUP ---
    // Initialize the UI helpers for this page
    const ui = setupAuthUI('#signup-button', '#auth-alert');

    // --- EVENT LISTENER ---
    $('#signup-form').on('submit', function (e) {
        e.preventDefault();

        const name = $('#signup-name').val();
        const email = $('#signup-email').val();
        const password = $('#signup-password').val();
        const passwordConfirm = $('#signup-password-confirm').val();

        // 1. Client-side validation
        if (password !== passwordConfirm) {
            ui.showError('Passwords do not match.');
            return;
        }

        // 2. Show loading state
        ui.showLoading();

        // 3. Make API call
        $.ajax({
            url: `${API_BASE_URL}/auth/signup`, // Using global config
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                name: name,
                email: email,
                password: password
            }),

            success: function (data) {
                // 4a. On Success: Show message and redirect to login
                ui.hideLoading();
                ui.showSuccess('Account created! Please log in.');

                $('#signup-form')[0].reset();

                setTimeout(() => {
                    window.location.href = 'login.html';
                }, 2000); // 2-second delay
            },

            error: function (xhr) {
                // 4b. On Error: Hide loading and show error
                ui.hideLoading();
                let errorMsg = 'An error occurred during signup.';
                if (xhr.responseJSON && xhr.responseJSON.detail) {
                    if (typeof xhr.responseJSON.detail === 'string') {
                        errorMsg = xhr.responseJSON.detail;
                    } else if (Array.isArray(xhr.responseJSON.detail)) {
                        errorMsg = xhr.responseJSON.detail[0].msg;
                    }
                }
                ui.showError(errorMsg);
            }
        });
    });

});