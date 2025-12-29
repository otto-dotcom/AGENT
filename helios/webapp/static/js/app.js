// HELIOS Web App JavaScript

// Tab switching
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
        // Remove active class from all tabs and panes
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));

        // Add active class to clicked tab
        tab.classList.add('active');

        // Show corresponding pane
        const tabName = tab.dataset.tab;
        document.getElementById(`${tabName}-tab`).classList.add('active');
    });
});

// Toast notifications
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type}`;
    toast.classList.add('show');

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Load secrets status on page load
async function loadSecretsStatus() {
    try {
        const response = await fetch('/api/secrets');
        const data = await response.json();

        // Update Airtable status
        const airtableStatus = document.getElementById('airtable-status');
        if (data.airtable_configured) {
            airtableStatus.classList.add('configured');
            airtableStatus.querySelector('.status-text').textContent = 'Configured ✓';
        }

        // Update Supabase status
        const supabaseStatus = document.getElementById('supabase-status');
        if (data.supabase_configured) {
            supabaseStatus.classList.add('configured');
            supabaseStatus.querySelector('.status-text').textContent = 'Configured ✓';
        }
    } catch (error) {
        console.error('Failed to load secrets status:', error);
    }
}

// Save secrets
document.getElementById('save-secrets').addEventListener('click', async () => {
    const data = {
        airtable_api_key: document.getElementById('airtable-key').value,
        airtable_base_id: document.getElementById('airtable-base').value,
        airtable_table_name: document.getElementById('airtable-table').value,
        supabase_url: document.getElementById('supabase-url').value,
        supabase_key: document.getElementById('supabase-key').value,
        supabase_table_name: document.getElementById('supabase-table').value,
    };

    try {
        const response = await fetch('/api/secrets', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (result.success) {
            showToast('Credentials saved successfully!', 'success');
            loadSecretsStatus();
        } else {
            showToast('Failed to save credentials', 'error');
        }
    } catch (error) {
        showToast('Error saving credentials: ' + error.message, 'error');
    }
});

// Test Airtable connection
document.getElementById('test-airtable').addEventListener('click', async () => {
    const btn = document.getElementById('test-airtable');
    btn.disabled = true;
    btn.textContent = 'Testing...';

    try {
        const response = await fetch('/api/test-airtable', { method: 'POST' });
        const result = await response.json();

        if (result.success) {
            showToast('Airtable connection successful!', 'success');
        } else {
            showToast('Airtable connection failed: ' + result.error, 'error');
        }
    } catch (error) {
        showToast('Error testing Airtable: ' + error.message, 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Test Connection';
    }
});

// Test Supabase connection
document.getElementById('test-supabase').addEventListener('click', async () => {
    const btn = document.getElementById('test-supabase');
    btn.disabled = true;
    btn.textContent = 'Testing...';

    try {
        const response = await fetch('/api/test-supabase', { method: 'POST' });
        const result = await response.json();

        if (result.success) {
            showToast('Supabase connection successful!', 'success');
        } else {
            showToast('Supabase connection failed: ' + result.error, 'error');
        }
    } catch (error) {
        showToast('Error testing Supabase: ' + error.message, 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Test Connection';
    }
});

// Show Airtable schema
document.getElementById('show-airtable-schema').addEventListener('click', async () => {
    const schemaBox = document.getElementById('airtable-schema');
    const fieldsList = document.getElementById('airtable-fields');

    try {
        const response = await fetch('/api/create-airtable-structure', { method: 'POST' });
        const result = await response.json();

        fieldsList.innerHTML = '';
        result.fields.forEach(field => {
            const li = document.createElement('li');
            li.innerHTML = `<strong>${field.name}</strong>: ${field.type}`;
            fieldsList.appendChild(li);
        });

        schemaBox.style.display = 'block';
    } catch (error) {
        showToast('Error loading schema: ' + error.message, 'error');
    }
});

// Show Supabase schema
document.getElementById('show-supabase-schema').addEventListener('click', async () => {
    const schemaBox = document.getElementById('supabase-schema');
    const sqlPre = document.getElementById('supabase-sql');

    try {
        const response = await fetch('/api/create-supabase-structure', { method: 'POST' });
        const result = await response.json();

        if (result.success) {
            sqlPre.textContent = result.sql;
            schemaBox.style.display = 'block';
        }
    } catch (error) {
        showToast('Error loading schema: ' + error.message, 'error');
    }
});

// Copy SQL
document.getElementById('copy-sql').addEventListener('click', () => {
    const sql = document.getElementById('supabase-sql').textContent;
    navigator.clipboard.writeText(sql).then(() => {
        showToast('SQL copied to clipboard!', 'success');
    });
});

// Inspect page
document.getElementById('inspect-btn').addEventListener('click', async () => {
    const btn = document.getElementById('inspect-btn');
    const resultsDiv = document.getElementById('inspection-results');
    const contentDiv = document.getElementById('inspection-content');

    btn.disabled = true;
    btn.textContent = 'Inspecting...';
    resultsDiv.style.display = 'block';
    contentDiv.innerHTML = '<p>Loading page and analyzing structure...</p>';

    try {
        const response = await fetch('/api/inspect-page', { method: 'POST' });
        const result = await response.json();

        if (result.success) {
            const structure = result.structure;

            let html = '<div class="info-grid">';
            html += `<div class="info-item"><span class="info-label">Page Title:</span> ${structure.title}</div>`;
            html += `<div class="info-item"><span class="info-label">URL:</span> ${structure.url}</div>`;
            html += `<div class="info-item"><span class="info-label">Tables Found:</span> ${structure.tables_found}</div>`;
            html += `<div class="info-item"><span class="info-label">Lists Found:</span> ${structure.lists_found}</div>`;
            html += `<div class="info-item"><span class="info-label">Data Attributes:</span> ${structure.data_attributes_found}</div>`;
            html += `<div class="info-item"><span class="info-label">Buttons Found:</span> ${structure.buttons_found}</div>`;
            html += `<div class="info-item"><span class="info-label">iFrames Found:</span> ${structure.iframes_found}</div>`;
            html += `<div class="info-item"><span class="info-label">Screenshot:</span> ${structure.screenshot_saved}</div>`;
            html += `<div class="info-item"><span class="info-label">Source Saved:</span> ${structure.source_saved}</div>`;
            html += '</div>';

            // Show sample data if found
            if (structure.sample_data && structure.sample_data.length > 0) {
                html += '<h4 style="margin-top: 20px;">Sample Data from First Table:</h4>';
                html += '<table>';
                structure.sample_data.forEach((row, index) => {
                    html += '<tr>';
                    row.forEach(cell => {
                        const tag = index === 0 ? 'th' : 'td';
                        html += `<${tag}>${cell || '-'}</${tag}>`;
                    });
                    html += '</tr>';
                });
                html += '</table>';
            }

            // Show page source preview
            if (structure.page_source_preview) {
                html += '<h4 style="margin-top: 20px;">Page Source Preview:</h4>';
                html += `<pre style="max-height: 300px; overflow-y: auto; background: #f3f4f6; padding: 15px; border-radius: 6px; font-size: 0.8em;">${escapeHtml(structure.page_source_preview)}</pre>`;
            }

            contentDiv.innerHTML = html;
            showToast('Page inspection complete!', 'success');
        } else {
            contentDiv.innerHTML = `<p style="color: red;">Inspection failed: ${result.error}</p>`;
            showToast('Inspection failed', 'error');
        }
    } catch (error) {
        contentDiv.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
        showToast('Error inspecting page: ' + error.message, 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Inspect Page Structure';
    }
});

// Run scraper
document.getElementById('run-scraper').addEventListener('click', async () => {
    const btn = document.getElementById('run-scraper');
    const progressDiv = document.getElementById('scrape-progress');
    const resultsDiv = document.getElementById('scrape-results');
    const statsDiv = document.getElementById('scrape-stats');

    const target = document.getElementById('scrape-target').value;
    const dryRun = document.getElementById('dry-run').checked;

    btn.disabled = true;
    progressDiv.style.display = 'block';
    resultsDiv.style.display = 'none';

    try {
        const response = await fetch('/api/scrape', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ target, dry_run: dryRun })
        });

        const result = await response.json();

        if (result.success) {
            const stats = result.stats;

            let html = '<div class="stats-grid">';
            html += `<div class="stat-item"><strong>Leads Scraped:</strong> ${stats.scraped}</div>`;
            html += `<div class="stat-item"><strong>Synced to Airtable:</strong> ${stats.synced_airtable}</div>`;
            html += `<div class="stat-item"><strong>Synced to Supabase:</strong> ${stats.synced_supabase}</div>`;
            html += `<div class="stat-item"><strong>Duplicates Skipped:</strong> ${stats.duplicates}</div>`;
            html += `<div class="stat-item"><strong>Errors:</strong> ${stats.errors}</div>`;
            html += '</div>';

            statsDiv.innerHTML = html;
            resultsDiv.style.display = 'block';
            progressDiv.style.display = 'none';

            showToast(result.message, 'success');
        } else {
            showToast('Scraping failed: ' + result.error, 'error');
            progressDiv.style.display = 'none';
        }
    } catch (error) {
        showToast('Error running scraper: ' + error.message, 'error');
        progressDiv.style.display = 'none';
    } finally {
        btn.disabled = false;
    }
});

// Load results
async function loadResults() {
    const resultsDiv = document.getElementById('results-list');
    resultsDiv.innerHTML = '<p>Loading...</p>';

    try {
        const response = await fetch('/api/results');
        const data = await response.json();

        if (data.results.length === 0) {
            resultsDiv.innerHTML = '<p>No results yet. Run the scraper first!</p>';
            return;
        }

        let html = '';
        data.results.forEach(result => {
            html += '<div class="result-item">';
            html += `<h4>📄 ${result.filename}</h4>`;
            html += '<div class="result-meta">';
            html += `<span>📅 ${new Date(result.scraped_at).toLocaleString()}</span>`;
            html += `<span>📊 ${result.total_leads} leads</span>`;
            html += `<span>🔗 ${result.source}</span>`;
            html += '</div>';

            if (result.leads && result.leads.length > 0) {
                html += '<div class="result-leads">';
                html += '<h5>Sample Leads:</h5>';
                result.leads.forEach(lead => {
                    html += '<div class="lead-card">';
                    html += `<h5>${lead.company_name || 'Unknown'}</h5>`;
                    if (lead.address) html += `<p>📍 ${lead.address}</p>`;
                    if (lead.email) html += `<p>📧 ${lead.email}</p>`;
                    if (lead.phone) html += `<p>📞 ${lead.phone}</p>`;
                    if (lead.region) html += `<p>🌍 ${lead.region}</p>`;
                    html += '</div>';
                });
                html += '</div>';
            }

            html += '</div>';
        });

        resultsDiv.innerHTML = html;
    } catch (error) {
        resultsDiv.innerHTML = `<p style="color: red;">Error loading results: ${error.message}</p>`;
    }
}

// Refresh results button
document.getElementById('refresh-results').addEventListener('click', loadResults);

// Helper function to escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadSecretsStatus();
});
