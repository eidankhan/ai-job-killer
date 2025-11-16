// login.js

$(document).ready(function () {

    // --- SETUP ---
    // Initialize the UI helpers for this page
    const ui = setupAuthUI('#login-button', '#auth-alert');

    // --- EVENT LISTENER ---
    $('#login-form').on('submit', function (e) {
        e.preventDefault();

        const email = $('#login-email').val();
        const password = $('#login-password').val();

        // 1. Show loading state
        ui.showLoading();

        // 2. Make API call
        $.ajax({
            url: `${API_BASE_URL}/auth/login`, // Using global config
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ email: email, password: password }),

            success: function (data) {
                // 3a. On Success: Store token and redirect
                localStorage.setItem('accessToken', data.access_token);

                // Redirect to the main app page (e.g., app.html or index.html)
                window.location.href = 'analyzer.html'; // <<< MAKE SURE THIS FILENAME IS CORRECT
            },

            error: function (xhr) {
                // 3b. On Error: Hide loading and show error
                ui.hideLoading();
                let errorMsg = 'Invalid email or password.';
                if (xhr.responseJSON && xhr.responseJSON.detail) {
                    if (typeof xhr.responseJSON.detail === 'string') {
                        errorMsg = xhr.responseJSON.detail;
                    }
                }
                ui.showError(errorMsg);
            }
        });
    });

});