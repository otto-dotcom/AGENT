# 🚀 Automated Outreach System - Complete Setup Guide

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Airtable Configuration](#airtable-configuration)
4. [n8n Setup](#n8n-setup)
5. [API Credentials Configuration](#api-credentials-configuration)
6. [Workflow Import](#workflow-import)
7. [Testing](#testing)
8. [Production Launch](#production-launch)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Accounts & Services

- ✅ **Airtable Account** (Kronos database access)
- ✅ **n8n Instance** (https://fagiolinosssssss.app.n8n.cloud/)
- ✅ **OpenAI API Key** (for AI personalization)
- ✅ **Twilio Account** (for SMS)
- ✅ **Mailchimp Account** (for email campaigns)
- ✅ **Python 3.8+** (for local scripts)

### Required Packages

```bash
pip install requests openai python-dotenv airtable-python-wrapper
```

---

## Environment Setup

### 1. Clone and Navigate to Project

```bash
cd outreach-automation
```

### 2. Create Environment File

```bash
cp config/credentials.example.env config/credentials.env
```

### 3. Fill in API Credentials

Edit `config/credentials.env`:

```env
# Airtable Configuration
AIRTABLE_API_KEY=your_airtable_api_key
AIRTABLE_BASE_ID=your_kronos_base_id

# n8n Configuration
N8N_API_URL=https://fagiolinosssssss.app.n8n.cloud
N8N_API_KEY=your_n8n_api_key

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4-turbo-preview

# Twilio Configuration
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=+41_your_number

# Mailchimp Configuration
MAILCHIMP_API_KEY=your_mailchimp_key
MAILCHIMP_SERVER_PREFIX=us1
MAILCHIMP_LIST_ID=your_list_id

# Safety
DRY_RUN_MODE=true
TEST_EMAIL=your_test@email.com
TEST_PHONE=+41_your_test_phone
```

---

## Airtable Configuration

### 1. Get Your Airtable Base ID

1. Go to [Airtable API](https://airtable.com/api)
2. Select your "Kronos Switzerland" base
3. Copy the Base ID (starts with `app...`)

### 2. Get Your API Key

1. Go to [Account Settings](https://airtable.com/account)
2. Click "Generate API key"
3. Copy and save securely

### 3. Document Your Database Schema

Run the schema documentation script:

```bash
cd scripts
python mcp_airtable_connector.py --document-schema
```

This will create `docs/airtable_schema.json` with your complete database structure.

### 4. Required Airtable Fields

Ensure your Leads table has these fields:

**Required Fields:**
- Company Name (Single line text)
- Contact Person (Single line text)
- Email (Email)
- Phone Number (Phone number)
- Industry (Single select)
- Location (Single line text)
- Status (Single select)

**Auto-populated Fields:**
- AI Insight (Long text)
- Pain Point (Long text)
- Enriched Date (Date)
- Email Sent Date (Date)
- SMS Sent Date (Date)
- Campaign ID (Single line text)
- Response Date (Date)
- Response Type (Single select)
- Response Content (Long text)
- Response Sentiment (Single select)
- Followup Count (Number)
- Last Followup Date (Date)

**Status Options:**
- New Lead
- Ready for Outreach
- Enriched
- Email Sent
- SMS Sent
- Responded - Interested
- Responded - Not Interested
- Meeting Booked
- Closed - No Response

---

## n8n Setup

### 1. Access Your n8n Instance

Navigate to: https://fagiolinosssssss.app.n8n.cloud

### 2. Get Your API Key

1. Click your profile icon (top right)
2. Go to "Settings" → "API"
3. Generate new API key
4. Copy to `credentials.env`

### 3. Configure Credentials in n8n

For each service, add credentials in n8n:

#### Airtable Credentials
1. Click "Credentials" in left sidebar
2. Click "Add Credential"
3. Select "Airtable API"
4. Enter your API Key
5. Save as "Airtable API"

#### OpenAI Credentials
1. Add new credential
2. Select "OpenAI API"
3. Enter your API Key
4. Save as "OpenAI API"

#### Twilio Credentials
1. Add new credential
2. Select "Twilio API"
3. Enter Account SID and Auth Token
4. Save as "Twilio API"

#### Mailchimp Credentials
1. Add new credential
2. Select "Mailchimp API"
3. Enter API Key
4. Save as "Mailchimp API"

---

## Workflow Import

### Import All 5 Workflows

1. Go to "Workflows" in n8n
2. Click "Import Workflow"
3. Upload each workflow JSON file from `n8n_workflows/`:
   - `01_lead_enrichment.json`
   - `02_email_campaign.json`
   - `03_sms_campaign.json`
   - `04_response_tracker.json`
   - `05_auto_followup.json`

### Configure Each Workflow

After importing, for each workflow:

1. **Open the workflow**
2. **Update credential references** (if needed)
3. **Update Airtable Base ID** in all Airtable nodes:
   - Replace `${AIRTABLE_BASE_ID}` with your actual Base ID
4. **Update email/phone numbers** in notification nodes
5. **Save the workflow**

### Workflow-Specific Configuration

#### 1. Lead Enrichment Pipeline
- Test with Manual Trigger first
- Verify OpenAI integration works
- Check Airtable updates

#### 2. Email Campaign Launcher
- Configure sender email
- Test rate limiter (2 seconds between emails)
- Verify Mailchimp integration

#### 3. SMS Campaign Launcher
- Configure Twilio phone number
- Set schedule (default: daily at 2 PM)
- Test with small batch first

#### 4. Response Tracker
- **IMPORTANT**: This workflow should be ACTIVE
- Configure webhook URL
- Set up Mailchimp/Twilio webhook forwarding
- Test with sample response

#### 5. Auto Follow-up
- Set schedule (default: weekly on Wednesday at 10 AM)
- Configure timezone (Europe/Zurich)
- Test with test leads

---

## Testing

### Test Mode (Dry Run)

Always test in dry run mode first:

```bash
# Set dry run mode
export DRY_RUN_MODE=true

# Test campaign orchestrator
cd scripts
python campaign_orchestrator.py --health

# Test lead enrichment
python campaign_orchestrator.py --enrich

# Test email personalization
python personalization_engine.py --test
```

### Test with Sample Data

1. **Create 5-10 test leads** in Airtable
   - Use your test email and phone number
   - Set Status to "Ready for Outreach"

2. **Run enrichment workflow**
   ```bash
   python campaign_orchestrator.py --enrich
   ```

3. **Verify enrichment in Airtable**
   - Check "AI Insight" field populated
   - Status changed to "Enriched"

4. **Run email campaign (dry run)**
   ```bash
   python campaign_orchestrator.py --email
   ```

5. **Check output** - should show what would be sent

### Full Integration Test

Once dry run passes:

1. Set `DRY_RUN_MODE=false` in `credentials.env`
2. Send to 3 test leads:
   ```bash
   python campaign_orchestrator.py --full-cycle
   ```
3. Verify:
   - ✅ Emails received
   - ✅ SMS received (if applicable)
   - ✅ Airtable updated correctly
   - ✅ No errors in n8n execution logs

---

## Production Launch

### Pre-Launch Checklist

- [ ] All workflows tested successfully
- [ ] Test emails/SMS received correctly
- [ ] Airtable updates working
- [ ] Response tracker webhook configured
- [ ] Compliance elements in place:
  - [ ] Unsubscribe links in emails
  - [ ] SMS opt-out instructions
  - [ ] Sender identification
  - [ ] Privacy policy link

### Launch Strategy

#### Week 1: Soft Launch (50 leads)
```bash
# Set production mode
export DRY_RUN_MODE=false

# Run for 50 leads
python campaign_orchestrator.py --full-cycle
```

Monitor:
- Delivery rates
- Bounce rates
- Response rates
- Any errors

#### Week 2: Scale Up (100 leads)
- Increase daily volume
- Monitor metrics
- Optimize templates based on responses

#### Week 3+: Full Scale
- Roll out to entire database
- Set up automated scheduling
- Monitor analytics daily

### Automated Scheduling

#### Using Cron (Linux/Mac)

Create cron job for daily campaigns:

```bash
crontab -e
```

Add:
```bash
# Run enrichment daily at 9 AM
0 9 * * * cd /path/to/outreach-automation/scripts && python campaign_orchestrator.py --enrich

# Run email campaign daily at 10 AM
0 10 * * * cd /path/to/outreach-automation/scripts && python campaign_orchestrator.py --email

# Generate analytics weekly
0 18 * * 5 cd /path/to/outreach-automation/scripts && python campaign_orchestrator.py --analytics
```

#### Using n8n Schedule Triggers

- n8n workflows 3 (SMS) and 5 (Follow-up) have built-in schedules
- Simply activate the workflows in n8n
- They'll run automatically based on configured schedule

---

## Monitoring & Analytics

### Daily Monitoring

```bash
# Check system health
python campaign_orchestrator.py --health

# Get campaign analytics
python campaign_orchestrator.py --analytics
```

### Key Metrics to Track

1. **Delivery Rates**
   - Email: Should be > 95%
   - SMS: Should be > 98%

2. **Response Rates**
   - Target: > 5%
   - Interested responses: > 50% of responses

3. **Meeting Booking Rate**
   - Target: > 1% of contacted leads

4. **Data Quality**
   ```bash
   python mcp_airtable_connector.py --validate-data
   ```

### Review n8n Execution Logs

1. Go to n8n → "Executions"
2. Review any failed executions
3. Check error messages
4. Adjust workflows as needed

---

## Troubleshooting

### Common Issues

#### 1. "Airtable API Key Invalid"

**Solution:**
- Regenerate API key in Airtable
- Update `credentials.env`
- Restart scripts

#### 2. "n8n Workflow Not Found"

**Solution:**
```bash
# List all workflows
python scripts/n8n_workflow_manager.py --list-workflows

# Verify workflow names match config
```

#### 3. "OpenAI Rate Limit Exceeded"

**Solution:**
- Add delay between AI calls
- Reduce batch size
- Upgrade OpenAI plan

#### 4. "Twilio SMS Sending Failed"

**Solution:**
- Verify phone number format (+41...)
- Check Twilio balance
- Ensure phone number is registered for A2P

#### 5. "Email Deliverability Issues"

**Solution:**
- Warm up sender email (start with 10-20/day)
- Check spam score
- Add SPF/DKIM records
- Use Mailchimp's sending domain

### Getting Help

1. **Check logs:**
   ```bash
   tail -f outreach_automation.log
   ```

2. **Run health check:**
   ```bash
   python campaign_orchestrator.py --health
   ```

3. **Test individual components:**
   ```bash
   # Test Airtable
   python mcp_airtable_connector.py --validate-data

   # Test n8n
   python n8n_workflow_manager.py --health-check

   # Test personalization
   python personalization_engine.py --test
   ```

---

## Next Steps

After successful setup:

1. **Read**: [Best Practices Guide](best_practices.md)
2. **Optimize**: Test different message templates
3. **Scale**: Gradually increase daily volume
4. **Analyze**: Review analytics weekly
5. **Iterate**: Improve based on response data

---

## Support & Resources

- **Airtable API Docs**: https://airtable.com/api
- **n8n Documentation**: https://docs.n8n.io
- **Twilio Docs**: https://www.twilio.com/docs
- **OpenAI API**: https://platform.openai.com/docs

---

**Built by Otto | Version 1.0.0 | Last Updated: 2025-12-17**
