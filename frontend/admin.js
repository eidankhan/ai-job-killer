$(document).ready(function () {

    // --- CONFIGURATION ---


    // --- EXACT API MAPPINGS ---
    const ENDPOINTS = {
        // Step 1 & 3 Operations
        'init': '/admin/ops/init-staging',
        'swap': '/admin/ops/swap-live',

        // Step 2 Loaders
        'occupation': '/occupations/load',
        'skill': '/skills/load',
        'skill_group': '/skillgroups/load',
        'skill_hierarchy': '/skill-hierarchy/load',
        'relations': '/occupation-skill-relations/load',

        // Bulk Loader
        'load_all': '/bulk-import/load-all'
    };

    // --- AUTH CHECK ---
    const token = localStorage.getItem('accessToken');
    if (!token) window.location.href = 'login.html';

    // --- STATE ---
    let isStagingReady = false;

    // --- HELPERS ---
    function getHeaders() {
        return {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };
    }

    function log(msg, type = 'info') {
        const time = new Date().toLocaleTimeString();
        let cls = '';
        if (type === 'error') cls = 'console-err';
        if (type === 'warn') cls = 'console-warn';
        if (type === 'success') cls = 'console-success';

        const line = `<div class="console-line ${cls}"><span class="text-muted">[${time}]</span> ${msg}</div>`;
        const $con = $('#console-output');
        $con.append(line);
        $con.scrollTop($con[0].scrollHeight);
    }

    function updateLastUpdateTime() {
        $('#last-update-time').text(new Date().toLocaleString());
    }

    /**
     * Gets the target schema name from the input field.
     */
    function getTargetSchema() {
        const val = $('#schema-name-input').val().trim();
        if (!val) {
            alert("Please enter a valid Schema Name (e.g., import_staging)");
            return null;
        }
        return val;
    }

    // --- STEP 1: INITIALIZE STAGING SCHEMA ---
    $('#btn-init-staging').on('click', function () {
        const schemaName = getTargetSchema();
        if (!schemaName) return;

        const $btn = $(this);
        $btn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm"></span> Creating...');

        log("------------------------------------------");
        log(`🚀 STEP 1: Initializing Schema '${schemaName}'...`, 'warn');

        // Parameter name: 'schema_name' (matches admin_ops.py)
        const url = `${window.APP_CONFIG.API_BASE_URL}${ENDPOINTS.init}?schema_name=${schemaName}`;

        $.ajax({
            url: url,
            type: 'POST',
            headers: getHeaders(),
            success: function (res) {
                log(`✅ Schema '${schemaName}' created successfully.`);
                log(`ℹ️ Tables structure initialized.`);

                isStagingReady = true;

                // UI Updates: LOCK the input so user doesn't change it mid-process
                $('#schema-name-input').prop('disabled', true);
                $('#staging-status-text').text(schemaName).removeClass('text-secondary').addClass('text-primary');
                $('#staging-icon').removeClass('text-secondary').addClass('text-primary');

                // Enable Next Steps
                $('.upload-trigger').prop('disabled', false).removeClass('btn-outline-secondary').addClass('btn-outline-primary');
                $('#btn-load-all-staging').prop('disabled', false);
                $('#btn-swap-live').prop('disabled', false).removeClass('btn-secondary').addClass('btn-success');

                $btn.html('<i class="bi bi-check-circle"></i> Schema Ready').addClass('btn-success').removeClass('btn-primary');
                // alert("Step 1 Complete: Schema Created.");
            },
            error: function (xhr) {
                log(`❌ Init Failed. Server says:`, 'error');
                log(xhr.responseText || xhr.statusText, 'error');
                $btn.prop('disabled', false).html('<i class="bi bi-1-circle me-2"></i>Initialize Staging');
            }
        });
    });

    // --- STEP 2: GRANULAR LOAD ---
    $('.upload-trigger').on('click', function () {
        if (!isStagingReady) return;

        // We use the value from the locked input
        const schemaName = $('#schema-name-input').val();
        const type = $(this).data('type');
        const $btn = $(this);
        const originalText = $btn.html();

        if (!confirm(`Load ${type.toUpperCase()} into '${schemaName}'?`)) return;

        $btn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm"></span>');
        log(`⏳ Loading ${type} data into '${schemaName}'...`);

        // Parameter name: 'target_schema' (matches your Refactored Loaders)
        const endpoint = ENDPOINTS[type];
        const url = `${window.APP_CONFIG.API_BASE_URL}${endpoint}?target_schema=${schemaName}`;

        $.ajax({
            url: url,
            type: 'POST',
            headers: getHeaders(),
            success: function (res) {
                log(`✅ ${type} loaded successfully.`);
                $btn.html('<i class="bi bi-check"></i> Loaded').removeClass('btn-outline-primary').addClass('btn-success');
                updateLastUpdateTime();
            },
            error: function (xhr) {
                log(`❌ Error loading ${type}.`, 'error');
                log(`Server says: ${xhr.responseText || xhr.statusText}`, 'error');
                $btn.prop('disabled', false).html(originalText);
            }
        });
    });

    // --- STEP 2: BULK LOAD (Helper) ---
    $('#btn-load-all-staging').on('click', function () {
        if (!isStagingReady) return;
        const schemaName = $('#schema-name-input').val();

        if (!confirm(`Load ALL datasets sequentially into '${schemaName}'? This may take time.`)) return;

        const $btn = $(this);
        $btn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm"></span> Processing...');
        log(`🚀 STEP 2: Starting Bulk Load into '${schemaName}'...`, 'warn');

        const url = `${window.APP_CONFIG.API_BASE_URL}${ENDPOINTS.load_all}?target_schema=${schemaName}`;

        $.ajax({
            url: url,
            type: 'POST',
            headers: getHeaders(),
            success: function (res) {
                log(`✅ Bulk Load Complete.`, 'success');
                log(`ℹ️ All tables populated in staging.`);
                $('.upload-trigger').html('<i class="bi bi-check"></i> OK').addClass('btn-success').removeClass('btn-outline-primary');
                $btn.html('<i class="bi bi-check-all"></i> Bulk Load Done').addClass('btn-success').removeClass('btn-outline-primary');
            },
            error: function (xhr) {
                log(`❌ Bulk Load Failed.`, 'error');
                log(xhr.responseText, 'error');
                $btn.prop('disabled', false).html('<i class="bi bi-collection-play me-2"></i>Bulk Load All into Staging');
            }
        });
    });

    // --- STEP 3: SWAP LIVE ---
    $('#btn-swap-live').on('click', function () {
        if (!isStagingReady) return;
        const schemaName = $('#schema-name-input').val();

        if (!confirm(`⚠️ FINAL STEP: Swap '${schemaName}' to PUBLIC? \n\nLive traffic will instantly see new data.`)) return;

        const $btn = $(this);
        $btn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm"></span> Swapping...');
        log("------------------------------------------");
        log("🔄 STEP 3: Initiating Atomic Schema Swap...", 'warn');

        // Parameter name: 'staging_schema' (matches admin_ops.py)
        const url = `${window.APP_CONFIG.API_BASE_URL}${ENDPOINTS.swap}?staging_schema=${schemaName}`;

        $.ajax({
            url: url,
            type: 'POST',
            headers: getHeaders(),
            success: function (res) {
                log("✨ SUCCESS: System Update Complete!", 'success');
                log("ℹ️ Live traffic is now served from the new dataset.");
                alert("SUCCESS! The system has been updated.");

                $btn.html('<i class="bi bi-rocket-takeoff"></i> Live').addClass('btn-success').removeClass('btn-secondary');
                // Allow user to reset UI to start over with a new schema name
                setTimeout(() => {
                    if (confirm("Reload page to start a new deployment?")) location.reload();
                }, 1000);
            },
            error: function (xhr) {
                log(`❌ Swap Failed: ${xhr.responseText}`, 'error');
                $btn.prop('disabled', false).html('<i class="bi bi-rocket-takeoff me-2"></i>Go Live (Swap)');
            }
        });
    });

    // --- GLOBAL ---
    $('#clear-console').on('click', function () {
        $('#console-output').html('<div class="console-line text-muted">// Console cleared.</div>');
    });

    $('#logout-btn').on('click', function () {
        localStorage.removeItem('accessToken');
        window.location.href = 'login.html';
    });

});