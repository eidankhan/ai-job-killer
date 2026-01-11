$(document).ready(function () {

    const API_BASE_URL = window.APP_CONFIG.API_BASE_URL;


    // --- MAIN APP MODULE ---
    const mainApp = {

        // --- STATE ---
        currentHoverIndex: -1,
        currentSuggestions: [],

        // --- CACHED ELEMENTS ---
        $jobInput: $('#jobInput'),
        $autocompleteList: $('#autocompleteList'),
        $analyzeForm: $('#analyze-form'),
        $analyzeButton: $('#analyze-button'),
        $alertBox: $('#app-alert'),
        $resultCard: $('#result-card'),
        $actionPlan: $('#action-plan'),
        $outputDetails: $('#output-details'),
        $detailsTableBody: $('#details-table-body'),

        // --- INITIALIZATION ---
        init: function () {
            this.fetchUserProfile();
            this.attachListeners();
        },

        // --- AUTH & HELPERS ---
        getToken: function () {
            return localStorage.getItem('accessToken');
        },
        getAuthHeaders: function () {
            const token = this.getToken();
            if (!token) {
                window.location.href = 'login.html';
                return null;
            }
            return {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            };
        },
        handleLogout: function () {
            localStorage.removeItem('accessToken');
            window.location.href = 'login.html';
        },

        // --- UI & UX ---
        showLoading: function () {
            this.$analyzeButton.find('.btn-text').hide();
            this.$analyzeButton.find('.spinner-border').show();
            this.$analyzeButton.prop('disabled', true);
        },
        hideLoading: function () {
            this.$analyzeButton.find('.btn-text').show();
            this.$analyzeButton.find('.spinner-border').hide();
            this.$analyzeButton.prop('disabled', false);
        },
        showError: function (message) {
            this.$alertBox.text(message).show();
        },
        hideError: function () {
            this.$alertBox.hide();
        },

        // --- API & BUSINESS LOGIC ---
        fetchUserProfile: function () {
            const authHeaders = this.getAuthHeaders();
            if (!authHeaders) return;

            $.ajax({
                url: `${API_BASE_URL}/auth/me`,
                type: 'GET',
                headers: { 'Authorization': authHeaders.Authorization },
                success: function (user) {
                    $('#welcome-message').text(user.name || user.email);
                },
                error: function () {
                    $('#welcome-message').text('Guest');
                }
            });
        },
        attachListeners: function () {
            this.$jobInput.on('keyup', (e) => this.handleKeyup(e));
            this.$analyzeForm.on('submit', (e) => this.handleAnalyzeSubmit(e));
            $('#logout-button').on('click', this.handleLogout);

            $(document).on('click', '.autocomplete-item', (e) => {
                const label = $(e.currentTarget).text().trim();
                this.selectOccupation(label);
            });

            $('#show-details-toggle').on('click', (e) => {
                e.preventDefault();
                this.$outputDetails.slideToggle();
                const text = this.$outputDetails.is(':visible') ? 'Hide Full Breakdown' : 'See Full Technical Breakdown';
                $(e.target).text(text);
            });

            // $('#share-button').on('click', () => {
            //     alert('Sharing to social media... (feature coming soon!)');
            // });

            // --- NEW PDF LISTENER ---
            $('#download-pdf-button').on('click', (e) => {
                e.preventDefault(); // Stop form submit just in case
                this.generatePDF();
            });
        },

        // --- PDF GENERATION FUNCTION ---
        generatePDF: function () {
            // Create a temporary container for PDF content
            const $content = $('<div>').addClass('p-4 bg-white');

            // 1. Add Title
            $content.append('<h2 style="text-align:center; font-family:sans-serif; margin-bottom: 20px;">AI Job Risk Report</h2>');

            // 2. Clone Result Card
            const $clonedCard = $('#result-card').clone().show();
            // Remove buttons from PDF version
            $clonedCard.find('button').remove();
            $clonedCard.css({ 'margin-top': '0', 'box-shadow': 'none' });
            $content.append($clonedCard);

            // 3. Clone Action Plan
            const $clonedPlan = $('#action-plan').clone().show();
            $clonedPlan.find('a').remove(); // Remove "See Technical Breakdown" link
            $clonedPlan.css('margin-top', '20px');
            // IMPORTANT: Expand scrollable areas so all content shows in PDF
            $clonedPlan.find('.skills-list-container').css({
                'max-height': 'none',
                'overflow': 'visible'
            });
            $content.append($clonedPlan);

            // 4. Clone Technical Breakdown (Table)
            const $clonedTable = $('#output-details').clone().show();
            $clonedTable.css('margin-top', '20px');
            // IMPORTANT: Expand table scroller
            $clonedTable.find('.table-container').css({
                'max-height': 'none',
                'overflow': 'visible',
                'border': 'none'
            });
            $content.append($clonedTable);

            // 5. Generate PDF
            const opt = {
                margin: [10, 10, 10, 10],
                filename: `AI-Risk-Report-${Date.now()}.pdf`,
                image: { type: 'jpeg', quality: 0.98 },
                html2canvas: { scale: 2, useCORS: true },
                jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' },
                pagebreak: { mode: ['avoid-all', 'css', 'legacy'] }
            };

            html2pdf().set(opt).from($content[0]).save();
        },

        handleKeyup: async function (e) {
            const query = this.$jobInput.val().trim();
            if (["ArrowDown", "ArrowUp", "Enter"].includes(e.key)) {
                this.handleKeyboardNavigation(e.key);
                return;
            }
            if (query.length < 2) {
                this.$autocompleteList.hide();
                this.currentSuggestions = [];
                return;
            }
            const authHeaders = this.getAuthHeaders();
            if (!authHeaders) return;
            try {
                const res = await fetch(`${API_BASE_URL}/scoring/search?query=${encodeURIComponent(query)}`, {
                    method: 'GET',
                    headers: authHeaders
                });
                if (!res.ok) throw new Error('Error fetching occupations');
                const occupations = await res.json();
                if (!occupations.length) {
                    this.$autocompleteList.hide();
                    return;
                }
                this.currentSuggestions = occupations;
                this.currentHoverIndex = -1;
                const itemsHtml = occupations.map((o, i) => `
                    <div class="autocomplete-item" data-index="${i}">
                        ${o.label || o.name}
                    </div>
                `).join('');
                this.$autocompleteList.html(itemsHtml).show();
            } catch (err) {
                console.error(err);
                this.$autocompleteList.hide();
            }
        },

        handleAnalyzeSubmit: async function (e) {
            e.preventDefault();
            const jobTitle = this.$jobInput.val().trim();
            if (!jobTitle) {
                this.showError('Please enter a job title');
                return;
            }
            this.showLoading();
            this.hideError();
            this.$resultCard.hide();
            this.$actionPlan.hide();
            this.$outputDetails.hide();
            $('#show-details-toggle').text('See Full Technical Breakdown');
            this.$autocompleteList.hide();

            const authHeaders = this.getAuthHeaders();
            if (!authHeaders) return;

            try {
                const apiUrl = `${API_BASE_URL}/scoring/occupation?name=${encodeURIComponent(jobTitle)}`;
                const response = await fetch(apiUrl, {
                    method: 'GET',
                    headers: authHeaders
                });
                if (!response.ok) {
                    const errData = await response.json();
                    throw new Error(errData.detail || 'Could not find or score that occupation.');
                }
                const data = await response.json();
                this.renderResults(data);
            } catch (err) {
                this.showError(err.message);
            } finally {
                this.hideLoading();
            }
        },

        renderResults: function (data) {
            // === 1. Populate the "Viral" Result Card ===
            const score = data.risk_score || 0;
            const verdict = this.getVerdict(score);
            $('#card-occupation-title').text(data.occupation_label || 'Your Job');
            $('#card-score').text(`${score.toFixed(0)}%`);
            $('#card-verdict').text(verdict);
            $('#card-explanation').text(data.explanation || '');
            const cardClass = this.getScoreColorClass(score);
            this.$resultCard.removeClass('card-high card-medium card-low').addClass(cardClass);
            this.$resultCard.fadeIn();

            // === 2. Populate the "Action Plan" (NOW WITH TAGS) ===
            const $safeSkillsList = $('#safe-skills-list');
            const $riskSkillsList = $('#risk-skills-list');
            $safeSkillsList.empty();
            $riskSkillsList.empty();

            let riskCount = 0;
            let safeCount = 0;
            const skills = data.per_skill || [];

            skills.forEach(skill => {
                const vulnerability = (skill.vulnerability || '').toLowerCase();
                if (vulnerability.includes('high') || vulnerability.includes('moderate')) {
                    const item = `
                        <span class="skill-tag skill-risk">
                            <i class="bi bi-exclamation-triangle-fill"></i>
                            ${skill.skill_label}
                        </span>`;
                    $riskSkillsList.append(item);
                    riskCount++;
                } else {
                    const item = `
                        <span class="skill-tag skill-safe">
                            <i class="bi bi-check-circle-fill"></i>
                            ${skill.skill_label}
                        </span>`;
                    $safeSkillsList.append(item);
                    safeCount++;
                }
            });

            if (safeCount === 0) $safeSkillsList.append('<p class="text-muted small w-100 text-center">No specific safe skills identified.</p>');
            if (riskCount === 0) $riskSkillsList.append('<p class="text-muted small w-100 text-center">No specific at-risk skills identified.</p>');

            this.$actionPlan.fadeIn();

            // === 3. Populate the (Hidden) Details Table ===
            this.$detailsTableBody.empty();
            if (skills.length > 0) {
                const tableHtml = skills.map(s => `
                    <tr>
                        <td>${s.skill_label}</td>
                        <td><span class="badge ${this.severityClass(s.vulnerability)}">${s.vulnerability}</span></td>
                    </tr>
                `).join('');
                this.$detailsTableBody.html(tableHtml);
            } else {
                this.$detailsTableBody.html('<tr><td colspan="2" class="text-center text-muted">No technical skill data available.</td></tr>');
            }
        },

        // --- "VIRAL" HELPER FUNCTIONS ---
        getVerdict: function (score) {
            if (score > 80) return "🔥 IN THE FIRING LINE";
            if (score > 60) return "😬 FEELING THE HEAT";
            if (score > 40) return "🤔 TIME TO ADAPT";
            if (score > 20) return "👍 SAFE... FOR NOW";
            return "😎 CHILLING";
        },
        getScoreColorClass: function (score) {
            if (score > 70) return 'card-high';
            if (score > 40) return 'card-medium';
            return 'card-low';
        },

        // --- ORIGINAL HELPER FUNCTIONS ---
        handleKeyboardNavigation: function (key) {
            const $items = this.$autocompleteList.find('.autocomplete-item');
            if (!$items.length) return;
            if (key === "ArrowDown") {
                if (this.currentHoverIndex < $items.length - 1) this.currentHoverIndex++;
            } else if (key === "ArrowUp") {
                if (this.currentHoverIndex > 0) this.currentHoverIndex--;
            } else if (key === "Enter") {
                if (this.currentHoverIndex >= 0 && this.currentHoverIndex < this.currentSuggestions.length) {
                    const selectedLabel = this.currentSuggestions[this.currentHoverIndex].label || this.currentSuggestions[this.currentHoverIndex].name;
                    this.$jobInput.val(selectedLabel);
                    this.$autocompleteList.hide();

                    // <<< CHANGE HERE >>>
                    // We no longer automatically submit the form.
                    // this.$analyzeForm.submit(); 
                }
                return;
            }
            this.highlightItem($items);
        },
        highlightItem: function ($items) {
            $items.removeClass('hover');
            $($items.get(this.currentHoverIndex)).addClass('hover');
        },
        selectOccupation: function (label) {
            this.$jobInput.val(label);
            this.$autocompleteList.hide();

            // <<< CHANGE HERE >>>
            // We no longer automatically submit the form.
            // this.$analyzeForm.submit();
        },
        severityClass: function (vuln) {
            if (!vuln) return 'safe';
            return vuln.toLowerCase().replace(/\s+/g, '-');
        }
    };

    // --- START THE APP ---
    mainApp.init();

});