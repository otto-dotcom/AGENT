# 🔍 Airtable Database Exploration Guide

## Quick Start: Explore Your Kronos Database

### Step 1: Get Your Credentials

#### Get Airtable API Key

1. Go to https://airtable.com/account
2. Scroll to the "API" section
3. Click "Generate API key" (if you don't have one)
4. Copy your API key

#### Get Your Base ID

1. Go to https://airtable.com/api
2. Select your "Kronos Switzerland" base
3. The Base ID is shown in the introduction (starts with `app`)
4. Example: `appXXXXXXXXXXXXXX`

### Step 2: Set Environment Variables

**Option A: Export in terminal (temporary)**
```bash
export AIRTABLE_API_KEY='your_api_key_here'
export AIRTABLE_BASE_ID='your_base_id_here'
```

**Option B: Add to credentials file (permanent)**
```bash
cd outreach-automation

# Edit the credentials file
nano config/credentials.env

# Add these lines:
AIRTABLE_API_KEY=your_api_key_here
AIRTABLE_BASE_ID=your_base_id_here

# Load the credentials
source config/credentials.env
```

### Step 3: Run the Explorer

```bash
cd outreach-automation/scripts
python explore_airtable.py
```

## What the Explorer Does

The explorer will:

1. ✅ **Connect to your Airtable base**
2. ✅ **Discover all tables** in your database
3. ✅ **Analyze each table's structure**:
   - Field names
   - Field types
   - Data completeness %
   - Sample values
4. ✅ **Check outreach readiness**:
   - Required fields present?
   - Data quality sufficient?
5. ✅ **Generate a detailed report**
6. ✅ **Save schema to JSON** for reference

## Understanding the Output

### Table Overview
```
📋 TABLE: Leads
Records sampled: 10
Fields found: 15
```

### Field Analysis
```
Field Name                  Type         Complete   Sample Values
─────────────────────────────────────────────────────────────────
Company Name                str          ✅ 95%     Alpine Bakery, Swiss Tech AG
Email                       str          ✅ 87%     hans@company.ch
Phone Number                str          ⚠️  65%     +41791234567
Industry                    str          ✅ 92%     Food & Beverage, Technology
Location                    str          ✅ 88%     Zurich, Geneva
Status                      str          ❌ 45%     New Lead, Ready for Outreach
```

### Completeness Legend
- ✅ **80-100%**: Excellent! Ready to use
- ⚠️ **50-79%**: Usable but needs improvement
- ❌ **0-49%**: Critical issue, needs attention

## Required Fields for Outreach

### Essential Fields (Must Have)
1. **Company Name** - Business name
2. **Contact Person** - Primary contact name
3. **Email** - For email campaigns
4. **Status** - Lead tracking (New, Ready, Contacted, etc.)

### Highly Recommended
5. **Phone Number** - For SMS campaigns
6. **Industry** - For personalization
7. **Location** - For geographic targeting

### Auto-populated (Added by System)
- AI Insight
- Pain Point
- Enriched Date
- Email Sent Date
- SMS Sent Date
- Response Date
- Campaign ID

## Common Issues & Solutions

### Issue 1: "Field X is Missing"

**Solution:**
1. Open your Airtable base
2. Add the missing field to your table
3. Choose appropriate field type:
   - Company Name → Single line text
   - Email → Email field
   - Phone Number → Phone number
   - Status → Single select
4. Re-run the explorer

### Issue 2: "Field X only 50% complete"

**Solution:**
1. Review records in Airtable
2. Fill in missing data where possible
3. Consider these options:
   - Manual data entry
   - Import from another source
   - Use enrichment services
   - Mark incomplete records as "Not Ready"

### Issue 3: "No Status field"

**Solution:**
1. Create a "Status" field (Single Select type)
2. Add these options:
   - New Lead
   - Ready for Outreach
   - Enriched
   - Email Sent
   - SMS Sent
   - Responded - Interested
   - Responded - Not Interested
   - Meeting Booked
   - Closed - No Response

### Issue 4: "Can't connect to Airtable"

**Solution:**
```bash
# Verify credentials are set
echo $AIRTABLE_API_KEY
echo $AIRTABLE_BASE_ID

# Should not be empty. If empty, set them:
export AIRTABLE_API_KEY='your_key'
export AIRTABLE_BASE_ID='your_base_id'

# Test connection
curl -H "Authorization: Bearer $AIRTABLE_API_KEY" \
     https://api.airtable.com/v0/$AIRTABLE_BASE_ID/Leads?maxRecords=1
```

## Interpreting the Schema File

After exploration, you'll have `docs/airtable_schema.json`:

```json
{
  "base_id": "appXXXXXXXXXXXXXX",
  "explored_at": "2025-12-17T10:30:00",
  "tables": {
    "Leads": {
      "record_count": 10,
      "fields": {
        "Company Name": {
          "type": "str",
          "completeness": 95.0,
          "sample_values": ["Alpine Bakery", "Swiss Tech AG"]
        }
      }
    }
  }
}
```

## Next Steps After Exploration

### If Data Quality is Good (>80%)
✅ You're ready to proceed!

1. Continue with workflow setup
2. Test with a small batch (5-10 leads)
3. Launch campaigns

### If Data Quality Needs Work (50-80%)
⚠️ Improve data first

1. Focus on required fields
2. Fill in missing data
3. Re-run explorer to verify
4. Start with smaller batches

### If Data Quality is Poor (<50%)
❌ Data cleanup required

1. Prioritize essential fields only
2. Create data improvement plan
3. Consider:
   - Data enrichment services
   - Manual data collection
   - Importing from other sources
4. Re-assess after improvements

## Advanced: Querying Your Data

### Count Records by Status
```python
from scripts.mcp_airtable_connector import MCPAirtableConnector

connector = MCPAirtableConnector()

# Get all leads
all_leads = connector.get_leads(max_records=1000)

# Count by status
status_counts = {}
for lead in all_leads:
    status = lead['fields'].get('Status', 'Unknown')
    status_counts[status] = status_counts.get(status, 0) + 1

print("Leads by Status:")
for status, count in status_counts.items():
    print(f"  {status}: {count}")
```

### Find Incomplete Records
```python
# Find leads missing email
no_email = connector.get_leads(
    filter_formula="NOT({Email})",
    max_records=100
)

print(f"Found {len(no_email)} leads without email")
```

### Check Ready for Outreach
```python
# Get leads ready to contact
ready = connector.get_ready_for_outreach(limit=50)

print(f"{len(ready)} leads ready for outreach")
for lead in ready[:5]:
    print(f"  - {lead['fields']['Company Name']}")
```

## Troubleshooting Commands

```bash
# Full exploration with verbose output
python explore_airtable.py --verbose

# Check specific table only
python explore_airtable.py --table "Leads"

# Validate data quality
python mcp_airtable_connector.py --validate-data

# Export all data for review
python mcp_airtable_connector.py --export-leads
```

## Support

If you encounter issues:

1. Check the output messages carefully
2. Verify your API credentials
3. Ensure Airtable base is accessible
4. Check your network connection
5. Review Airtable API documentation: https://airtable.com/api

---

**Ready to explore? Run:**
```bash
cd outreach-automation/scripts
python explore_airtable.py
```
