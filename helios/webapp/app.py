#!/usr/bin/env python3
"""
HELIOS Web Application
======================

Web interface for managing solar lead scraping pipeline
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(32))

# Storage for secrets (in production, use proper secret management)
SECRETS_FILE = Path(__file__).parent / 'secrets.json'


def load_secrets():
    """Load stored API keys from encrypted storage"""
    if SECRETS_FILE.exists():
        with open(SECRETS_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_secrets(secrets_data):
    """Save API keys to encrypted storage"""
    with open(SECRETS_FILE, 'w') as f:
        json.dump(secrets_data, f, indent=2)
    # Set file permissions to owner-only
    os.chmod(SECRETS_FILE, 0o600)


@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@app.route('/api/secrets', methods=['GET'])
def get_secrets():
    """Get list of configured secrets (not values)"""
    secrets_data = load_secrets()

    # Return only which keys are configured, not the values
    configured = {
        'airtable_configured': 'AIRTABLE_API_KEY' in secrets_data,
        'supabase_configured': 'SUPABASE_URL' in secrets_data and 'SUPABASE_KEY' in secrets_data,
    }

    return jsonify(configured)


@app.route('/api/secrets', methods=['POST'])
def save_secrets_endpoint():
    """Save API keys"""
    data = request.json

    secrets_data = load_secrets()

    # Update secrets
    if 'airtable_api_key' in data and data['airtable_api_key']:
        secrets_data['AIRTABLE_API_KEY'] = data['airtable_api_key']

    if 'airtable_base_id' in data and data['airtable_base_id']:
        secrets_data['AIRTABLE_BASE_ID'] = data['airtable_base_id']

    if 'airtable_table_name' in data and data['airtable_table_name']:
        secrets_data['AIRTABLE_TABLE_NAME'] = data['airtable_table_name']

    if 'supabase_url' in data and data['supabase_url']:
        secrets_data['SUPABASE_URL'] = data['supabase_url']

    if 'supabase_key' in data and data['supabase_key']:
        secrets_data['SUPABASE_KEY'] = data['supabase_key']

    if 'supabase_table_name' in data and data['supabase_table_name']:
        secrets_data['SUPABASE_TABLE_NAME'] = data['supabase_table_name']

    save_secrets(secrets_data)

    return jsonify({'success': True, 'message': 'Secrets saved successfully'})


@app.route('/api/inspect-page', methods=['POST'])
def inspect_page():
    """Inspect the GSE.it page to see actual structure"""
    try:
        from scrapers.gse_scraper import GSEScraper

        # Create scraper in non-headless mode to see what we're scraping
        scraper = GSEScraper(headless=True)

        if not scraper.setup_driver():
            return jsonify({'error': 'Failed to initialize browser'}), 500

        try:
            logger.info("Loading GSE.it page...")
            scraper.driver.get(scraper.url)

            import time
            time.sleep(5)  # Wait for page to load

            # Get page info
            page_title = scraper.driver.title
            page_url = scraper.driver.current_url

            # Save screenshot
            screenshot_dir = Path(__file__).parent.parent / 'exports'
            screenshot_dir.mkdir(exist_ok=True)
            screenshot_path = screenshot_dir / 'page_inspection.png'
            scraper.driver.save_screenshot(str(screenshot_path))

            # Get page source snippet
            page_source = scraper.driver.page_source

            # Save full page source
            source_path = screenshot_dir / 'page_source.html'
            with open(source_path, 'w', encoding='utf-8') as f:
                f.write(page_source)

            # Analyze structure
            from selenium.webdriver.common.by import By

            tables = scraper.driver.find_elements(By.TAG_NAME, "table")
            lists = scraper.driver.find_elements(By.TAG_NAME, "ul")
            divs_with_data = scraper.driver.find_elements(By.CSS_SELECTOR, "[data-company], [data-name], [data-installer]")

            # Look for interactive elements
            buttons = scraper.driver.find_elements(By.TAG_NAME, "button")
            iframes = scraper.driver.find_elements(By.TAG_NAME, "iframe")

            structure_info = {
                'title': page_title,
                'url': page_url,
                'tables_found': len(tables),
                'lists_found': len(lists),
                'data_attributes_found': len(divs_with_data),
                'buttons_found': len(buttons),
                'iframes_found': len(iframes),
                'screenshot_saved': str(screenshot_path),
                'source_saved': str(source_path),
                'page_source_preview': page_source[:2000] + '...' if len(page_source) > 2000 else page_source
            }

            # Try to find specific installer data
            sample_data = []

            # Check for table data
            if tables:
                first_table = tables[0]
                rows = first_table.find_elements(By.TAG_NAME, "tr")
                for i, row in enumerate(rows[:5]):  # First 5 rows
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if not cells:
                        cells = row.find_elements(By.TAG_NAME, "th")
                    sample_data.append([cell.text for cell in cells])

            structure_info['sample_data'] = sample_data

            scraper.driver.quit()

            return jsonify({
                'success': True,
                'structure': structure_info
            })

        except Exception as e:
            if scraper.driver:
                scraper.driver.quit()
            raise e

    except Exception as e:
        logger.error(f"Page inspection failed: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/test-airtable', methods=['POST'])
def test_airtable():
    """Test Airtable connection"""
    try:
        secrets_data = load_secrets()

        # Set environment variables temporarily
        os.environ['AIRTABLE_API_KEY'] = secrets_data.get('AIRTABLE_API_KEY', '')
        os.environ['AIRTABLE_BASE_ID'] = secrets_data.get('AIRTABLE_BASE_ID', '')
        os.environ['AIRTABLE_TABLE_NAME'] = secrets_data.get('AIRTABLE_TABLE_NAME', 'Solar_Leads')

        from integrations.airtable_client import AirtableClient

        client = AirtableClient()

        # Try to fetch records
        records = client.table.all(max_records=1)

        return jsonify({
            'success': True,
            'message': 'Airtable connection successful',
            'base_id': secrets_data.get('AIRTABLE_BASE_ID'),
            'table_name': secrets_data.get('AIRTABLE_TABLE_NAME'),
            'sample_record_count': len(records)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/test-supabase', methods=['POST'])
def test_supabase():
    """Test Supabase connection"""
    try:
        secrets_data = load_secrets()

        # Set environment variables temporarily
        os.environ['SUPABASE_URL'] = secrets_data.get('SUPABASE_URL', '')
        os.environ['SUPABASE_KEY'] = secrets_data.get('SUPABASE_KEY', '')
        os.environ['SUPABASE_TABLE_NAME'] = secrets_data.get('SUPABASE_TABLE_NAME', 'solar_leads')

        from integrations.supabase_client import SupabaseClient

        client = SupabaseClient()

        # Try to fetch records
        response = client.client.table(client.table_name).select("*").limit(1).execute()

        return jsonify({
            'success': True,
            'message': 'Supabase connection successful',
            'url': secrets_data.get('SUPABASE_URL'),
            'table_name': secrets_data.get('SUPABASE_TABLE_NAME'),
            'sample_record_count': len(response.data) if response.data else 0
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/create-airtable-structure', methods=['POST'])
def create_airtable_structure():
    """Instructions for creating Airtable structure"""

    fields = [
        {'name': 'Company Name', 'type': 'Single line text'},
        {'name': 'Address', 'type': 'Long text'},
        {'name': 'City', 'type': 'Single line text'},
        {'name': 'Region', 'type': 'Single select'},
        {'name': 'Phone', 'type': 'Phone number'},
        {'name': 'Email', 'type': 'Email'},
        {'name': 'Website', 'type': 'URL'},
        {'name': 'PEC', 'type': 'Email'},
        {'name': 'VAT Number', 'type': 'Single line text'},
        {'name': 'Source', 'type': 'Single line text'},
        {'name': 'Industry', 'type': 'Single line text'},
        {'name': 'Status', 'type': 'Single select'},
        {'name': 'Scraped Date', 'type': 'Date'},
        {'name': 'Notes', 'type': 'Long text'},
        {'name': 'Contact Person', 'type': 'Single line text'},
    ]

    return jsonify({
        'success': True,
        'message': 'Airtable cannot be created via API. Please create manually.',
        'instructions': 'Create a new table in Airtable with the following fields:',
        'fields': fields
    })


@app.route('/api/create-supabase-structure', methods=['POST'])
def create_supabase_structure():
    """Get SQL to create Supabase structure"""

    schema_path = Path(__file__).parent.parent / 'config' / 'supabase_schema.sql'

    if schema_path.exists():
        with open(schema_path, 'r') as f:
            sql = f.read()

        return jsonify({
            'success': True,
            'message': 'Run this SQL in your Supabase SQL Editor',
            'sql': sql
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Schema file not found'
        }), 404


@app.route('/api/scrape', methods=['POST'])
def scrape():
    """Run the scraper"""
    data = request.json
    target = data.get('target', 'both')
    dry_run = data.get('dry_run', False)

    try:
        # Load secrets and set environment variables
        secrets_data = load_secrets()

        for key, value in secrets_data.items():
            os.environ[key] = value

        # Import and run pipeline
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from helios_pipeline import HeliosPipeline

        pipeline = HeliosPipeline(target=target, dry_run=dry_run)
        stats = pipeline.run()

        return jsonify({
            'success': True,
            'stats': stats,
            'message': f'Scraping complete! Found {stats["scraped"]} leads'
        })

    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/results', methods=['GET'])
def get_results():
    """Get recent scraping results"""
    exports_dir = Path(__file__).parent.parent / 'exports'

    if not exports_dir.exists():
        return jsonify({'results': []})

    # Get recent JSON exports
    json_files = sorted(exports_dir.glob('gse_leads_*.json'), reverse=True)[:10]

    results = []
    for json_file in json_files:
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                results.append({
                    'filename': json_file.name,
                    'scraped_at': data.get('scraped_at'),
                    'total_leads': data.get('total_leads', 0),
                    'source': data.get('source'),
                    'leads': data.get('leads', [])[:5]  # First 5 leads only
                })
        except Exception as e:
            logger.error(f"Failed to load {json_file}: {e}")

    return jsonify({'results': results})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
