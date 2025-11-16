// auth-ui.js

/**
 * Creates a set of UI helper functions for an authentication form.
 * @param {string} buttonSelector The jQuery selector for the submit button (e.g., "#login-button")
 * @param {string} alertSelector The jQuery selector for the alert box (e.g., "#auth-alert")
 * @returns {object} An object with functions: showLoading, hideLoading, showError, showSuccess
 */
function setupAuthUI(buttonSelector, alertSelector) {
    const $button = $(buttonSelector);
    const $alert = $(alertSelector);
    const $btnText = $button.find('.btn-text');
    const $spinner = $button.find('.spinner-border');

    return {
        /**
         * Disables the button, shows the spinner, and hides any alerts.
         */
        showLoading: () => {
            $btnText.hide();
            $spinner.show();
            $button.prop('disabled', true);
            $alert.hide().removeClass('alert-danger alert-success');
        },
        /**
         * Enables the button and hides the spinner.
         */
        hideLoading: () => {
            $btnText.show();
            $spinner.hide();
            $button.prop('disabled', false);
        },
        /**
         * Shows an error message in the alert box.
         * @param {string} message The error message to display
         */
        showError: (message) => {
            $alert.text(message).addClass('alert-danger').show();
        },
        /**
         * Shows a success message in the alert box.
         * @param {string} message The success message to display
         */
        showSuccess: (message) => {
            $alert.text(message).addClass('alert-success').show();
        }
    };
}