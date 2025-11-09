$(document).ready(function () {

    // --- CONFIGURATION ---
    const API_BASE_URL = 'http://127.0.0.1:8000'; // CHANGE THIS to your FastAPI server URL

    // --- STATE & UI HELPERS (jQuery-based) ---

    function showApp(isLoggedIn, user = null) {
        if (isLoggedIn) {
            $('#auth-container').hide();
            $('#app-container').show();
            if (user && user.name) { // Assuming user object has 'name' from signup
                $('#welcome-message').text(`Welcome, ${user.name}!`);
            } else if (user && user.email) {
                $('#welcome-message').text(`Welcome!`);
            }
        } else {
            $('#auth-container').show();
            $('#app-container').hide();
        }
    }

    function showAlert(type, message) {
        let alertBox = (type === 'auth') ? $('#auth-alert') : $('#app-alert');
        alertBox.text(message).removeClass('alert-danger alert-success').addClass('alert-danger').show();
    }

    function showSuccessAlert(type, message) {
        let alertBox = (type === 'auth') ? $('#auth-alert') : $('#app-alert');
        alertBox.text(message).removeClass('alert-danger alert-success').addClass('alert-success').show();
    }

    function getToken() {
        return localStorage.getItem('accessToken');
    }

    // Helper to get auth headers for fetch
    function getAuthHeaders() {
        const token = getToken();
        if (!token) {
            // Handle expired token case
            console.error("No auth token found, logging out.");
            showApp(false);
            return null;
        }
        return {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };
    }

    // --- AUTHENTICATION LOGIC (jQuery) ---

    function checkLoginStatus() {
        const token = getToken();
        if (token) {
            $.ajax({
                url: `${API_BASE_URL}/auth/me`,
                type: 'GET',
                headers: { 'Authorization': `Bearer ${token}` },
                success: function (user) {
                    showApp(true, user);
                },
                error: function () {
                    localStorage.removeItem('accessToken');
                    showApp(false);
                }
            });
        } else {
            showApp(false);
        }
    }

    $('#signup-form').on('submit', function (e) {
        e.preventDefault();
        const name = $('#signup-name').val();
        const email = $('#signup-email').val();
        const password = $('#signup-password').val();

        $.ajax({
            url: `${API_BASE_URL}/auth/signup`,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ name: name, email: email, password: password }),
            success: function (data) {
                showSuccessAlert('auth', 'Signup successful! Please log in.');
                // Clear form
                $('#signup-form')[0].reset();
            },
            error: function (xhr) {
                let errorMsg = 'An error occurred during signup.';
                if (xhr.responseJSON && xhr.responseJSON.detail) {
                    if (typeof xhr.responseJSON.detail === 'string') {
                        errorMsg = xhr.responseJSON.detail;
                    } else if (Array.isArray(xhr.responseJSON.detail)) {
                        errorMsg = xhr.responseJSON.detail[0].msg;
                    }
                }
                showAlert('auth', errorMsg);
            }
        });
    });

    $('#login-form').on('submit', function (e) {
        e.preventDefault();
        const email = $('#login-email').val();
        const password = $('#login-password').val();

        $.ajax({
            url: `${API_BASE_URL}/auth/login`,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ email: email, password: password }),
            success: function (data) {
                localStorage.setItem('accessToken', data.access_token);
                checkLoginStatus();
            },
            error: function () {
                showAlert('auth', 'Invalid email or password.');
            }
        });
    });

    $('#logout-btn').on('click', function () {
        // Optional: Call /auth/logout if you need server-side revocation
        localStorage.removeItem('accessToken');
        showApp(false);
        // Clear results when logging out
        $('#output').hide().empty();
        $('#jobInput').val('');
    });

    // --- CORE APP LOGIC (Your Vanilla JS, modified for Auth) ---

    const jobInput = document.getElementById('jobInput');
    const autocompleteList = document.getElementById('autocompleteList');
    let currentHoverIndex = -1;
    let currentSuggestions = [];

    jobInput.addEventListener('keyup', async (e) => {
        const query = jobInput.value.trim();
        if (!query) {
            autocompleteList.style.display = 'none';
            currentSuggestions = [];
            currentHoverIndex = -1;
            return;
        }

        if (["ArrowDown", "ArrowUp", "Enter"].includes(e.key)) {
            handleKeyboardNavigation(e.key);
            return;
        }

        const authHeaders = getAuthHeaders();
        if (!authHeaders) return; // Stop if no token

        try {
            // *** MODIFIED to use API_BASE_URL and auth headers ***
            const res = await fetch(`${API_BASE_URL}/scoring/search?query=${encodeURIComponent(query)}`, {
                method: 'GET',
                headers: authHeaders
            });

            if (res.status === 401) { // Handle unauthorized
                showAlert('app', 'Session expired. Please log out and log in again.');
                return;
            }
            if (!res.ok) throw new Error('Error fetching occupations');

            const occupations = await res.json();

            // Assuming occupations is an array of objects with 'label'
            // If your API returns objects with 'name', change 'o.label' to 'o.name'
            if (!occupations.length) {
                autocompleteList.style.display = 'none';
                currentSuggestions = [];
                currentHoverIndex = -1;
                return;
            }

            currentSuggestions = occupations;
            currentHoverIndex = -1;

            autocompleteList.innerHTML = occupations.map((o, i) => `
                <div class="autocomplete-item" data-index="${i}" onclick="selectOccupation('${o.label || o.name}')">
                    ${o.label || o.name}
                </div>
            `).join('');
            autocompleteList.style.display = 'block';
        } catch (err) {
            console.error(err);
            showAlert('app', err.message);
            autocompleteList.style.display = 'none';
        }
    });

    function handleKeyboardNavigation(key) {
        const items = autocompleteList.querySelectorAll('.autocomplete-item');
        if (!items.length) return;

        if (key === "ArrowDown") {
            if (currentHoverIndex < items.length - 1) currentHoverIndex++;
            highlightItem(items);
        } else if (key === "ArrowUp") {
            if (currentHoverIndex > 0) currentHoverIndex--;
            highlightItem(items);
        } else if (key === "Enter") {
            if (currentHoverIndex >= 0 && currentHoverIndex < currentSuggestions.length) {
                jobInput.value = currentSuggestions[currentHoverIndex].label || currentSuggestions[currentHoverIndex].name;
                autocompleteList.style.display = 'none';
            }
        }
    }

    function highlightItem(items) {
        items.forEach((item, i) => {
            item.classList.toggle('hover', i === currentHoverIndex);
        });
    }

    // Made this function available to the window scope so onclick="" can find it
    window.selectOccupation = function (label) {
        jobInput.value = label;
        autocompleteList.style.display = 'none';
    }

    function severityClass(vuln) {
        if (!vuln) return 'safe'; // Default
        return vuln.toLowerCase().replace(/\s+/g, '-'); // converts "Very High" -> "very-high"
    }

    // Made this function available to the window scope so onclick="" can find it
    window.analyzeJob = async function () {
        const jobTitle = jobInput.value.trim();
        const output = document.getElementById('output');
        output.style.display = 'none';
        output.innerHTML = '';
        $('#app-alert').hide(); // Hide any old alerts

        if (!jobTitle) {
            showAlert('app', 'Please enter a job title');
            return;
        }

        output.innerHTML = '<p>Analyzing... please wait.</p>';
        output.style.display = 'block';

        const authHeaders = getAuthHeaders();
        if (!authHeaders) return; // Stop if no token

        try {
            // *** MODIFIED to use API_BASE_URL and auth headers ***
            const apiUrl = `${API_BASE_URL}/scoring/occupation?name=${encodeURIComponent(jobTitle)}`;
            const response = await fetch(apiUrl, {
                method: 'GET',
                headers: authHeaders
            });

            if (response.status === 401) { // Handle unauthorized
                showAlert('app', 'Session expired. Please log out and log in again.');
                return;
            }
            if (!response.ok) throw new Error('Error calling scoring API');

            const data = await response.json();

            // Check if data is valid (adjust based on your API)
            if (!data || data.risk_score === undefined) {
                throw new Error('Could not find or score that occupation.');
            }

            output.innerHTML = `
                <div class="occupation-card">
                    <h2 class="occupation-title">${data.occupation_label || 'N/A'}</h2>
                    <div class="risk-stats">
                        <div class="stat">
                            <span class="stat-label">Risk Level</span>
                            <span>${data.level || 'N/A'}</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Risk Score</span>
                            <span class="stat-value">${(data.risk_score || 0).toFixed(2)}%</span>
                        </div>
                    </div>
                    <div class="explanation">
                        <h4>Explanation</h4>
                        <p>${data.explanation || 'No explanation available.'}</p>
                    </div>
                    <hr/>
                    <h3>Top Skills Analyzed (${data.skills_analyzed || 0})</h3>
                </div>
                <table>
                    <thead>
                        <tr><th>Skill</th><th>Vulnerability</th></tr>
                    </thead>
                    <tbody>
                        ${(data.per_skill || []).slice(0, 10).map(s => `
                            <tr>
                                <td>${s.skill_label}</td>
                                <td><span class="badge ${severityClass(s.vulnerability)}">${s.vulnerability}</span></td>
                            </tr>`).join('')}
                    </tbody>
                </table>
            `;
        } catch (err) {
            console.error(err);
            output.innerHTML = '';
            output.style.display = 'none';
            showAlert('app', `Error: ${err.message}`);
        }
    }

    // --- INITIALIZATION ---
    checkLoginStatus(); // Check login status when the page loads

});