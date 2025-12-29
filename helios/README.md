# 🌞 HELIOS - Solar Lead Scraping & Pipeline

**Automated pipeline for scraping solar installer leads from GSE.it and syncing to Airtable & Supabase**

## 📖 Overview

HELIOS is a complete lead generation pipeline that:
1. ✅ Scrapes solar installer data from [GSE.it](https://www.gse.it/servizi-per-te/fotovoltaico/reddito-energetico/mappa-realizzatori-impianti-fotovoltaici)
2. ✅ Extracts company information, contact details, and locations
3. ✅ Syncs leads to **Airtable** and **Supabase** databases
4. ✅ Prevents duplicates automatically
5. ✅ Exports data to CSV and JSON formats

## 🏗️ Project Structure

```
helios/
├── README.md                       # This file
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
├── helios_pipeline.py             # Main pipeline orchestrator
├── config/                        # Configuration files
├── scrapers/                      # Web scrapers
│   ├── __init__.py
│   └── gse_scraper.py            # GSE.it scraper
├── integrations/                  # Database integrations
│   ├── __init__.py
│   ├── airtable_client.py        # Airtable client
│   └── supabase_client.py        # Supabase client
├── exports/                       # CSV/JSON exports
└── logs/                          # Debug logs and screenshots
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd helios
pip install -r requirements.txt
```

### 2. Install Chrome/Chromium (for Selenium)

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y chromium-browser chromium-chromedriver

# macOS
brew install --cask google-chrome
brew install chromedriver
```

### 3. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
nano .env
```

Required environment variables:
```env
# Airtable
AIRTABLE_API_KEY=your_airtable_api_key
AIRTABLE_BASE_ID=your_base_id
AIRTABLE_TABLE_NAME=Solar_Leads

# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
SUPABASE_TABLE_NAME=solar_leads
```

### 4. Run the Pipeline

```bash
# Dry run (scrape only, no database sync)
python helios_pipeline.py --dry-run

# Sync to both Airtable and Supabase
python helios_pipeline.py --target both

# Sync to Airtable only
python helios_pipeline.py --target airtable

# Sync to Supabase only
python helios_pipeline.py --target supabase
```

## 📊 Database Schema

### Airtable Schema

Create a table in Airtable with these fields:

| Field Name      | Type          | Description                    |
|----------------|---------------|--------------------------------|
| Company Name   | Single line   | Company/Installer name         |
| Address        | Long text     | Full address                   |
| City           | Single line   | City                           |
| Region         | Single select | Italian region                 |
| Phone          | Phone         | Contact phone number           |
| Email          | Email         | Contact email                  |
| Website        | URL           | Company website                |
| PEC            | Email         | Italian certified email        |
| VAT Number     | Single line   | Partita IVA                    |
| Source         | Single line   | Data source (GSE.it)           |
| Industry       | Single line   | Solar/Photovoltaic Installation|
| Status         | Single select | New Lead, Contacted, etc.      |
| Scraped Date   | Date          | When lead was scraped          |
| Notes          | Long text     | Additional information         |

### Supabase Schema

```sql
CREATE TABLE solar_leads (
  id BIGSERIAL PRIMARY KEY,
  company_name TEXT NOT NULL,
  address TEXT,
  city TEXT,
  region TEXT,
  phone TEXT,
  email TEXT,
  website TEXT,
  pec TEXT,
  vat_number TEXT,
  source TEXT DEFAULT 'GSE.it',
  industry TEXT DEFAULT 'Solar/Photovoltaic Installation',
  status TEXT DEFAULT 'new_lead',
  scraped_date TIMESTAMP DEFAULT NOW(),
  notes TEXT,
  contact_person TEXT,
  metadata JSONB,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Create index for duplicate checking
CREATE UNIQUE INDEX idx_solar_leads_company ON solar_leads(company_name);
```

## 🛠️ Usage Examples

### Basic Usage

```python
from helios_pipeline import HeliosPipeline

# Initialize pipeline
pipeline = HeliosPipeline(target='both', dry_run=False)

# Run complete pipeline
stats = pipeline.run()

print(f"Scraped: {stats['scraped']} leads")
print(f"Synced to Airtable: {stats['synced_airtable']}")
print(f"Synced to Supabase: {stats['synced_supabase']}")
```

### Scrape Only

```python
from scrapers.gse_scraper import GSEScraper

# Scrape leads
scraper = GSEScraper(headless=True)
leads = scraper.scrape()

print(f"Found {len(leads)} leads")
```

### Airtable Integration

```python
from integrations.airtable_client import AirtableClient

# Initialize client
airtable = AirtableClient()

# Create single lead
lead = {
    'company_name': 'Solar Solutions SRL',
    'email': 'info@solarsolutions.it',
    'region': 'Lombardia'
}
airtable.create_lead(lead)

# Batch create
airtable.create_leads_batch(leads)
```

### Supabase Integration

```python
from integrations.supabase_client import SupabaseClient

# Initialize client
supabase = SupabaseClient()

# Create single lead
supabase.create_lead(lead)

# Create or update (upsert)
supabase.create_or_update(lead)

# Get all leads
all_leads = supabase.get_all_leads()
```

## 🔧 Configuration

### Scraper Settings

Edit in `.env`:
```env
HEADLESS_BROWSER=true      # Run browser in headless mode
SCRAPE_DELAY=2            # Delay between requests (seconds)
MAX_RETRIES=3             # Max retry attempts
```

### Custom Selectors

If the GSE.it page structure changes, update selectors in `scrapers/gse_scraper.py`:

```python
# Example: Update table selector
tables = self.driver.find_elements(By.CSS_SELECTOR, "table.installers")

# Example: Update company name selector
company_name = element.find_element(By.CLASS_NAME, "company-name").text
```

## 📈 Workflow Integration

### n8n Integration

HELIOS integrates with the existing outreach automation system:

```
┌─────────────┐
│   HELIOS    │ ← Scrapes GSE.it
│   Pipeline  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Airtable   │ ← Stores leads
│             │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ n8n Workflow│ ← Lead enrichment
│  Enrichment │
└─────────────┘
```

### Schedule Scraping

Use cron to run HELIOS daily:

```bash
# Add to crontab
crontab -e

# Run every day at 2 AM
0 2 * * * cd /path/to/helios && python helios_pipeline.py --target both
```

## 🧪 Testing

### Dry Run

Test scraping without syncing to databases:

```bash
python helios_pipeline.py --dry-run --verbose
```

### Debug Mode

Enable verbose logging and save debug screenshots:

```bash
python helios_pipeline.py --target both --verbose
```

Debug files saved to `logs/`:
- `gse_page_TIMESTAMP.png` - Screenshot of scraped page
- `gse_source_TIMESTAMP.html` - Page HTML source

## 🔒 Security Notes

- ✅ Never commit `.env` file to git
- ✅ Use read-only API keys where possible
- ✅ Rotate API keys regularly
- ✅ Respect website scraping policies
- ✅ Add delays between requests

## 📝 Data Fields Extracted

The scraper attempts to extract:

- ✅ **Company Name** - Business name
- ✅ **Address** - Full address
- ✅ **City** - Municipality
- ✅ **Region** - Italian region
- ✅ **Phone** - Contact number
- ✅ **Email** - Contact email
- ✅ **PEC** - Certified email (Italian)
- ✅ **VAT Number** - Partita IVA
- ✅ **Website** - Company URL

## 🐛 Troubleshooting

### Selenium Issues

```bash
# Install Chrome/Chromium
sudo apt-get install chromium-browser chromium-chromedriver

# Or install Chrome manually
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
```

### No Leads Found

1. Check debug screenshots in `logs/` folder
2. Run with `--verbose` flag
3. Verify GSE.it page structure hasn't changed
4. Update selectors in `gse_scraper.py`

### Database Sync Errors

1. Verify API credentials in `.env`
2. Check database schema matches expected format
3. Test database connection manually

## 📚 Resources

- [GSE.it Solar Installers Map](https://www.gse.it/servizi-per-te/fotovoltaico/reddito-energetico/mappa-realizzatori-impianti-fotovoltaici)
- [Airtable API Documentation](https://airtable.com/developers/web/api)
- [Supabase Python Client](https://supabase.com/docs/reference/python)
- [Selenium Documentation](https://selenium-python.readthedocs.io/)

## 📞 Support

For issues or questions:
1. Check debug logs in `logs/` folder
2. Review page screenshots
3. Verify environment configuration
4. Update scraper selectors if needed

## 🗺️ Roadmap

- [ ] Add more Italian solar installer sources
- [ ] Implement webhook notifications
- [ ] Add email validation
- [ ] Implement lead scoring
- [ ] Add automatic follow-up integration
- [ ] Support for other EU countries

---

**Version**: 1.0.0
**Last Updated**: 2025-12-29
**Project**: HELIOS Solar Lead Pipeline
