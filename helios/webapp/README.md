# HELIOS Web Application

Web interface for managing the HELIOS solar lead scraping pipeline.

## Features

### 🔍 Page Inspector
- **Inspect live page structure** before scraping
- See what data elements are actually available
- View tables, lists, and data attributes
- Save screenshots and HTML source for analysis

### 🔐 API Configuration
- Securely store Airtable and Supabase credentials
- Test database connections before running
- Credentials saved in encrypted local storage

### 🗄️ Database Setup
- View required Airtable field specifications
- Get SQL schema for Supabase table creation
- Copy SQL to clipboard for easy setup

### 🚀 Scraper Execution
- Run scraper with visual feedback
- Choose target database (Airtable, Supabase, or both)
- Dry-run mode for testing
- Real-time progress updates
- View scraping statistics

### 📊 Results Viewer
- Browse recent scraping results
- View sample leads from each run
- Export data in CSV/JSON formats

## Quick Start

### 1. Install Dependencies

```bash
cd helios
pip install -r requirements.txt
```

### 2. Start the Web App

```bash
./start_webapp.sh
```

Or manually:

```bash
cd webapp
python3 app.py
```

### 3. Access the Application

Open your browser to: **http://localhost:5000**

## Usage Workflow

### First Time Setup

1. **Inspect the Page**
   - Go to "Page Inspector" tab
   - Click "Inspect Page Structure"
   - Review the actual page structure
   - Check sample data extraction

2. **Configure API Keys**
   - Go to "API Configuration" tab
   - Enter your Airtable credentials:
     - API Key (from Airtable account)
     - Base ID (from your base URL)
     - Table Name
   - Enter your Supabase credentials:
     - Project URL
     - API Key (anon/public key)
     - Table Name
   - Click "Save All Credentials"
   - Test each connection

3. **Setup Databases**
   - Go to "Database Setup" tab
   - **Airtable**: Click "Show Required Fields" and create the table manually
   - **Supabase**: Click "Show SQL Schema", copy the SQL, and run it in Supabase SQL Editor

4. **Run Scraper**
   - Go to "Run Scraper" tab
   - Select target database
   - (Optional) Enable "Dry Run" for testing
   - Click "Start Scraping"
   - View results and statistics

5. **View Results**
   - Go to "Results" tab
   - Browse recent scraping runs
   - View sample leads
   - Export data as needed

## API Endpoints

### GET /api/secrets
Get configured secrets status (not values)

### POST /api/secrets
Save API credentials

```json
{
  "airtable_api_key": "pat...",
  "airtable_base_id": "app...",
  "airtable_table_name": "Solar_Leads",
  "supabase_url": "https://...supabase.co",
  "supabase_key": "eyJ...",
  "supabase_table_name": "solar_leads"
}
```

### POST /api/inspect-page
Inspect GSE.it page structure

Returns:
```json
{
  "success": true,
  "structure": {
    "title": "Page title",
    "tables_found": 5,
    "sample_data": [...]
  }
}
```

### POST /api/test-airtable
Test Airtable connection

### POST /api/test-supabase
Test Supabase connection

### POST /api/scrape
Run the scraper

```json
{
  "target": "both",    // "airtable", "supabase", or "both"
  "dry_run": false
}
```

### GET /api/results
Get recent scraping results

## Security

- API keys are stored in `secrets.json` with 0600 permissions (owner-only)
- Credentials never sent to client
- Flask session secured with secret key
- In production, use environment variables or proper secret management

## File Structure

```
webapp/
├── app.py                 # Flask application
├── secrets.json           # Encrypted credentials (git-ignored)
├── templates/
│   └── index.html        # Main UI
└── static/
    ├── css/
    │   └── style.css     # Styles
    └── js/
        └── app.js        # Frontend logic
```

## Development

### Run in Debug Mode

```bash
cd webapp
export FLASK_ENV=development
python3 app.py
```

### Custom Port

```bash
export FLASK_PORT=8080
python3 app.py
```

## Production Deployment

For production use:

1. Set a secure secret key:
   ```bash
   export FLASK_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
   ```

2. Use a production WSGI server:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

3. Use environment variables for secrets instead of `secrets.json`

4. Set up HTTPS with reverse proxy (nginx/Apache)

5. Enable CORS if needed for API access

## Troubleshooting

### "Flask not found"
```bash
pip install flask werkzeug
```

### "Permission denied" for secrets.json
```bash
chmod 600 webapp/secrets.json
```

### Browser can't connect
- Check firewall settings
- Ensure port 5000 is not blocked
- Try accessing via 127.0.0.1:5000 instead of localhost

### Page inspection fails
- Ensure Selenium and ChromeDriver are installed
- Check browser compatibility
- Review logs in exports/ directory

## Tips

- Always use **Page Inspector** first to see actual data structure
- Use **Dry Run** mode to test scraping without database sync
- **Test connections** before running full scrape
- Check **Results** tab for sample data quality
- Review screenshots in exports/ if scraping fails

## Support

For issues:
1. Check page structure with Inspector
2. Verify API credentials
3. Review browser console (F12) for errors
4. Check Flask logs in terminal
5. Examine debug files in exports/

---

**Version**: 1.0.0
**Port**: 5000
**License**: MIT
