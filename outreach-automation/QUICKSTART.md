# ⚡ Quick Start Guide - 5 Minutes to Explore Your Database

## Step 1: Get Your Airtable Credentials (2 min)

### A. Get API Key
1. Visit: https://airtable.com/account
2. Click "Generate API key"
3. Copy the key

### B. Get Base ID
1. Visit: https://airtable.com/api
2. Click your "Kronos Switzerland" base
3. Copy the Base ID (starts with `app`)

## Step 2: Set Up Credentials (1 min)

```bash
# Navigate to project
cd outreach-automation

# Copy example credentials
cp config/credentials.example.env config/credentials.env

# Edit with your credentials
nano config/credentials.env
```

Add these two lines:
```
AIRTABLE_API_KEY=your_api_key_here
AIRTABLE_BASE_ID=your_base_id_here
```

Save and exit (Ctrl+X, then Y)

## Step 3: Load Credentials
```bash
source config/credentials.env
```

## Step 4: Explore Your Database! (2 min)

```bash
cd scripts
python explore_airtable.py
```

This will:
- ✅ Connect to your Airtable
- ✅ Show all your tables
- ✅ Analyze all fields
- ✅ Check data completeness
- ✅ Identify missing fields
- ✅ Save a detailed schema report

## What You'll See

```
🔍 AIRTABLE DATABASE EXPLORER
================================================

📦 Base ID: appXXXXXXXXXXXXXX

📋 Discovering tables...
✅ Found 1 table(s):
   - Leads

✅ Leads:
   Records sampled: 10
   Fields found: 15

📊 DETAILED DATABASE REPORT
================================================
📋 TABLE: Leads
================================================

Field Name                  Type         Complete   Sample Values
───────────────────────────────────────────────────────────────
Company Name                str          ✅ 95%     Alpine Bakery, Swiss Tech
Email                       str          ✅ 87%     contact@company.ch
Phone Number                str          ⚠️  65%     +41791234567
Industry                    str          ✅ 92%     Food & Beverage, Tech
Location                    str          ✅ 88%     Zurich, Geneva
```

## Understanding the Output

### ✅ Green (80-100%)
**Great!** This field is ready to use for outreach.

### ⚠️  Yellow (50-79%)
**Usable** but could be improved. You can proceed but consider filling gaps.

### ❌ Red (0-49%)
**Needs attention** before launching campaigns. Fill in missing data.

## What Happens Next?

The script creates:
1. **Detailed Console Report** - Shows everything on screen
2. **JSON Schema File** - Saved to `docs/airtable_schema.json`

## Next Steps

### If Data Looks Good (mostly green ✅)
```bash
# Proceed to campaign setup
cd ..
cat docs/setup_guide.md
```

### If Data Needs Work (yellow/red ⚠️❌)
1. Open your Airtable base
2. Fill in missing required fields:
   - Company Name
   - Contact Person
   - Email
   - Industry
   - Location
3. Re-run the explorer
4. Once mostly green, proceed to setup!

## Troubleshooting

### "AIRTABLE_API_KEY not found"
```bash
# Check if set
echo $AIRTABLE_API_KEY

# If empty, set it:
export AIRTABLE_API_KEY='your_key_here'
```

### "Cannot connect to Airtable"
```bash
# Test connection
curl -H "Authorization: Bearer $AIRTABLE_API_KEY" \
     "https://api.airtable.com/v0/$AIRTABLE_BASE_ID/Leads?maxRecords=1"

# Should return JSON data, not an error
```

### "No tables found"
The script will prompt you to enter table names manually.
Common table names: `Leads`, `Companies`, `Contacts`

## Pro Tips

### Quick Re-run After Changes
```bash
# After updating Airtable data, re-explore:
python explore_airtable.py
```

### Check Specific Metrics
```bash
# Validate data quality scores
python mcp_airtable_connector.py --validate-data

# See complete schema
cat ../docs/airtable_schema.json | python -m json.tool
```

### Export Your Data
```bash
# Export all leads to JSON for review
python mcp_airtable_connector.py --export-leads
```

## Need Help?

**Read the full guide:**
```bash
cat ../docs/airtable_exploration_guide.md
```

**Check your setup:**
```bash
cat ../docs/setup_guide.md
```

---

## The Complete Flow

```
┌─────────────────────────────┐
│ 1. Explore Airtable         │ ← YOU ARE HERE
│    (5 minutes)              │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│ 2. Fix Data Issues          │
│    (if needed)              │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│ 3. Set Up n8n Workflows     │
│    (30 minutes)             │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│ 4. Test with 5-10 Leads     │
│    (15 minutes)             │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│ 5. Launch Campaign!         │
│    🚀                        │
└─────────────────────────────┘
```

---

**Ready? Let's explore!**

```bash
cd outreach-automation/scripts
python explore_airtable.py
```

🎯 **Goal**: Understand your data so we can build the perfect outreach system for you!
