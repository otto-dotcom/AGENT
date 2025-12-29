# 🌞 HELIOS Web App - Quick Start Guide

## You're absolutely right - I hadn't seen the actual page!

The new **Page Inspector** feature lets you see exactly what's on the GSE.it page before scraping.

## 🚀 Launch the Web App

```bash
cd helios
./start_webapp.sh
```

Then open: **http://localhost:5000**

## 📋 Step-by-Step Workflow

### 1. **First: Inspect the Page** 🔍

**This is the KEY feature you asked for!**

1. Go to the **"Page Inspector"** tab
2. Click **"Inspect Page Structure"**
3. Wait for it to load the GSE.it page
4. You'll see:
   - How many tables are on the page
   - How many lists and data attributes
   - **Sample data** from the first table
   - **Screenshot** saved to `helios/exports/`
   - **HTML source** saved for analysis

**Why this matters:**
- You can see the ACTUAL structure before running anything
- The scraper uses multiple strategies (tables, lists, JSON, data attributes)
- If the page structure doesn't match, you can customize the scraper
- Screenshots help you verify what's being loaded

### 2. **Configure Your API Keys** 🔐

1. Go to **"API Configuration"** tab

**For Airtable:**
- API Key: Get from https://airtable.com/create/tokens
- Base ID: Found in your Airtable URL (starts with "app")
- Table Name: Name of your table (default: "Solar_Leads")

**For Supabase:**
- Project URL: From your Supabase project settings
- API Key: The "anon public" key from project settings
- Table Name: Name of your table (default: "solar_leads")

3. Click **"Save All Credentials"**
4. Click **"Test Connection"** for each to verify

### 3. **Set Up Your Databases** 🗄️

1. Go to **"Database Setup"** tab

**For Airtable:**
- Click "Show Required Fields"
- Create these fields manually in your Airtable base
- Fields include: Company Name, Address, Email, Phone, etc.

**For Supabase:**
- Click "Show SQL Schema"
- Click "Copy SQL"
- Open Supabase SQL Editor
- Paste and run the SQL

### 4. **Run the Scraper** 🚀

1. Go to **"Run Scraper"** tab
2. Choose target database:
   - **Both** (recommended) - Syncs to both Airtable and Supabase
   - **Airtable Only**
   - **Supabase Only**
3. Optional: Check "Dry Run" to test without syncing
4. Click **"Start Scraping"**
5. View results and statistics

### 5. **View Results** 📊

1. Go to **"Results"** tab
2. See recent scraping runs
3. View sample leads from each run
4. Check data quality

## 🎯 Addressing Your Concerns

### "Did you take a good look at how data is extracted?"

**Honest answer:** No, I couldn't access the page directly (got a 403 error).

**That's why I built the Page Inspector!** Now YOU can:
1. See exactly what's on the page
2. View the HTML structure
3. Check sample data extraction
4. Verify the scraper strategies work

### The Scraper Uses Multiple Strategies:

```python
# Strategy 1: HTML Tables
tables = driver.find_elements(By.TAG_NAME, "table")

# Strategy 2: Lists
lists = driver.find_elements(By.TAG_NAME, "ul")

# Strategy 3: Data Attributes
elements = driver.find_elements(By.CSS_SELECTOR, "[data-company]")

# Strategy 4: JSON in Scripts
# Looks for JSON data embedded in page

# Strategy 5: Card/Div Containers
cards = driver.find_elements(By.CSS_SELECTOR, "div.installer")
```

### What to Do If Data Extraction Fails:

1. **Use Page Inspector** to see the structure
2. Open `helios/exports/page_source.html` in a text editor
3. Search for company names or contact info
4. Identify the HTML structure they're in
5. Update `helios/scrapers/gse_scraper.py` with the correct selectors

Example customization:
```python
# If companies are in a specific class
installers = driver.find_elements(By.CLASS_NAME, "actual-class-name")

# If they're in a specific table
table = driver.find_element(By.ID, "actual-table-id")
```

## 🔧 Features You Asked For

✅ **Web app** - Flask application with modern UI
✅ **Save API keys as secrets** - Encrypted storage, never exposed
✅ **Create database structures** - SQL generation for Supabase, field specs for Airtable
✅ **See actual page structure** - Page Inspector with screenshots and HTML analysis

## 📸 Understanding the Page Inspector Output

When you inspect the page, you'll see:

```
Page Title: [Title of the GSE page]
URL: [Current URL]
Tables Found: X
Lists Found: Y
Data Attributes: Z
Buttons Found: N
iFrames Found: M
```

**Sample Data from First Table:**
Shows the first 5 rows from the first table found on the page.

**If you see:**
- **Many tables (5+)**: Data likely in table format
- **Many data attributes**: Data in custom HTML elements
- **iFrames**: Content might be loaded from another source
- **Buttons but no data**: Data might load via JavaScript interaction

## 🐛 Troubleshooting

### "No data found after inspection"
1. The page might use JavaScript to load data after page load
2. Try increasing wait time in `gse_scraper.py`
3. Check if data is behind a button click or form submission

### "Different structure than expected"
1. Use the saved HTML source to find the actual selectors
2. Update the scraper's CSS selectors
3. The web app makes it easy to test changes

### "Scraper finds 0 leads"
1. **Run Page Inspector first!**
2. Check the sample data output
3. Review the screenshot to see what loaded
4. Adjust scraper selectors based on findings

## 🎓 Pro Tips

1. **Always inspect first** - Don't assume the page structure
2. **Use dry-run mode** - Test scraping without database sync
3. **Check sample data** - Verify quality before full sync
4. **Save screenshots** - Visual reference for troubleshooting
5. **Test connections** - Verify API keys work before scraping

## 📚 Next Steps

1. Launch the web app: `./start_webapp.sh`
2. Inspect the GSE.it page structure
3. Configure your API keys
4. Set up databases
5. Run a dry-run test
6. Run the full scrape
7. Check results quality

## 🔗 Files to Check After Inspection

- `helios/exports/page_inspection.png` - Screenshot of loaded page
- `helios/exports/page_source.html` - Full HTML source
- `helios/logs/gse_page_*.png` - Additional debug screenshots
- `helios/logs/gse_source_*.html` - Debug HTML sources

---

**The web app gives you full visibility into what's happening before, during, and after scraping!**
