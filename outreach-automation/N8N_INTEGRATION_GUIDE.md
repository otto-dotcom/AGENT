# 🔗 n8n Integration Guide - Connect Your Web App to n8n Workflows

## 🎯 Overview

This guide shows you how to make your web app **trigger n8n workflows** instead of running campaigns directly. This gives you:

✅ **Visual workflow editor** - Modify campaigns in n8n's UI
✅ **Better monitoring** - See execution logs in n8n
✅ **Easier debugging** - Step-by-step workflow execution
✅ **More flexibility** - Add nodes, change logic visually
✅ **Centralized control** - All automation in one place

---

## 🏗️ Architecture

### **Before (Direct Execution):**
```
Web App → Python Scripts → Airtable/OpenAI/Twilio/Mailchimp
```

### **After (n8n Powered):**
```
Web App → JSON Payload → n8n Webhook → n8n Workflow → Services → Response
```

---

## 📦 What's Included

### **1. Updated Backend** (`webapp/backend/main_n8n.py`)
- Routes all campaigns through n8n
- Creates n8n-compatible JSON payloads
- Triggers workflows via webhooks
- Receives status updates from n8n

### **2. n8n Integration Module** (`webapp/backend/n8n_integration.py`)
- JSON schema definitions
- Payload formatters
- Workflow triggers
- Webhook response handlers

### **3. Updated n8n Workflows** (`n8n_workflows/WEBAPP_*.json`)
- Accept web app JSON input
- Process campaigns
- Send results back to web app

---

## 🚀 Setup Steps

### **Step 1: Update Your Backend**

Replace the main backend file:

```bash
cd outreach-automation/webapp/backend

# Backup current file
mv main.py main_old.py

# Use n8n-powered version
cp main_n8n.py main.py
```

### **Step 2: Import n8n Workflows**

1. Go to your n8n instance: https://fagiolinosssssss.app.n8n.cloud
2. Click "Workflows" → "Import from File"
3. Import these files:
   - `n8n_workflows/WEBAPP_email_campaign.json`
   - `n8n_workflows/WEBAPP_sms_campaign.json` (create similarly)
   - `n8n_workflows/WEBAPP_lead_enrichment.json` (create similarly)

### **Step 3: Configure Webhooks in n8n**

For each imported workflow:

1. Click the **Webhook node**
2. Note the webhook URL (e.g., `https://your-n8n.cloud/webhook/email-campaign`)
3. Keep workflows **ACTIVE** ✅

### **Step 4: Update Environment Variables**

Add to `config/credentials.env`:

```env
# n8n Configuration
N8N_API_URL=https://fagiolinosssssss.app.n8n.cloud
N8N_API_KEY=your_n8n_api_key_here
N8N_WEBHOOK_BASE=https://fagiolinosssssss.app.n8n.cloud/webhook
```

### **Step 5: Restart Your Web App**

```bash
cd ../
./start.sh
```

---

## 📊 JSON Payload Structure

### **Email Campaign Payload**

This is what the web app sends to n8n:

```json
{
  "metadata": {
    "source": "web_app",
    "timestamp": "2025-12-17T10:00:00Z",
    "campaign_id": "campaign-001",
    "version": "1.0"
  },
  "campaign": {
    "name": "Q4 Tech Outreach",
    "type": "email",
    "template_id": "email_v1_discovery",
    "dry_run": true,
    "schedule_time": null
  },
  "leads": [
    {
      "record_id": "rec123abc",
      "source": "airtable",
      "status": "pending"
    }
  ],
  "settings": {
    "rate_limit": {
      "max_per_minute": 1,
      "max_per_hour": 20,
      "max_per_day": 50,
      "delay_between_sends": 2
    },
    "retry_on_failure": true,
    "notification_webhook": "http://localhost:8000/api/webhooks/campaign-complete"
  }
}
```

### **Lead Enrichment Payload**

```json
{
  "action": "enrich_leads",
  "leads": [
    {
      "record_id": "rec123abc",
      "company_name": "Alpine Bakery GmbH",
      "industry": "Food & Beverage",
      "location": "Zurich",
      "website": "https://alpinebakery.ch"
    }
  ],
  "enrichment_config": {
    "generate_ai_insight": true,
    "generate_pain_point": true,
    "update_airtable": true
  }
}
```

---

## 🔄 How It Works

### **Campaign Launch Flow:**

1. **User clicks "Launch Campaign"** in web app
2. **Web app creates JSON payload** with campaign data
3. **Web app POSTs to n8n webhook**: `https://your-n8n.cloud/webhook/email-campaign`
4. **n8n workflow executes**:
   - Parses web app JSON
   - Checks dry run mode
   - Fetches lead details from Airtable
   - Generates personalized emails with AI
   - Sends emails (or simulates if dry run)
   - Updates Airtable status
   - Sends results back to web app
5. **Web app receives response** and shows user

### **Sequence Diagram:**

```
Web App          Backend          n8n Workflow          Airtable
   |                |                    |                  |
   |--Launch------->|                    |                  |
   |                |--JSON Payload----->|                  |
   |                |                    |--Get Leads------>|
   |                |                    |<--Lead Data------|
   |                |                    |                  |
   |                |                    |--AI Generate---->|
   |                |                    |                  |
   |                |                    |--Send Emails---->|
   |                |                    |                  |
   |                |                    |--Update Status-->|
   |                |<--Results----------|                  |
   |<--Success------|                    |                  |
```

---

## 🎯 Testing the Integration

### **Step 1: Get Example Payload**

Visit in your browser:
```
http://localhost:8000/api/n8n/example-payload?workflow_type=email_campaign
```

You'll see the exact JSON format n8n expects.

### **Step 2: Test n8n Workflow Manually**

1. Go to n8n
2. Open "WEBAPP_EMAIL_CAMPAIGN" workflow
3. Click "Execute Workflow" button
4. Paste the example payload
5. Click "Execute"
6. Watch it run!

### **Step 3: Test from Web App**

1. Open web app: http://localhost:3000
2. Click "Launch Campaign"
3. Select 1-2 test leads
4. Enable **Dry Run Mode** ✅
5. Launch campaign
6. Check n8n execution logs

---

## 📡 Available Endpoints

### **Web App → n8n:**

```bash
# Email Campaign
POST https://your-n8n.cloud/webhook/email-campaign

# SMS Campaign
POST https://your-n8n.cloud/webhook/sms-campaign

# Lead Enrichment
POST https://your-n8n.cloud/webhook/lead-enrichment
```

### **n8n → Web App (Callbacks):**

```bash
# Campaign Complete
POST http://localhost:8000/api/webhooks/campaign-complete

# Lead Updated
POST http://localhost:8000/api/webhooks/lead-updated
```

### **Get Schemas:**

```bash
# Get all JSON schemas
GET http://localhost:8000/api/n8n/schemas

# Get example payload
GET http://localhost:8000/api/n8n/example-payload?workflow_type=email_campaign
```

---

## 🔧 Customizing n8n Workflows

### **In n8n Visual Editor:**

1. **Add OpenAI Node** for better personalization
2. **Add Conditional Logic** for A/B testing
3. **Add HTTP Request Nodes** for external APIs
4. **Add Delay Nodes** for rate limiting
5. **Add Error Handling** with fallback paths

### **Example: Add A/B Testing**

1. After "Parse Web App Input" node
2. Add "Switch" node
3. Route 50% to Template A, 50% to Template B
4. Track which performs better

### **Example: Add Retry Logic**

1. After "Send Email" node
2. Add "IF" node: Check if email failed
3. Add "Wait" node: Wait 5 minutes
4. Loop back to "Send Email"
5. Limit to 3 retries

---

## 📊 Monitoring

### **In n8n:**
1. Click "Executions" in sidebar
2. See all workflow runs
3. Click to see detailed logs
4. View success/failure rates

### **In Web App:**
1. Go to "Campaigns" page
2. See all launched campaigns
3. Click for details
4. View n8n execution ID

---

## 🐛 Troubleshooting

### **Campaign launches but n8n doesn't execute:**

```bash
# Check webhook URL
curl -X POST https://your-n8n.cloud/webhook/email-campaign \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'

# Should return workflow execution data
```

### **n8n workflow fails:**

1. Open n8n execution log
2. Click failed node
3. See error message
4. Common issues:
   - Invalid Airtable credentials
   - Missing OpenAI API key
   - Malformed JSON input

### **Web app shows error:**

```bash
# Check backend logs
cd webapp
docker-compose logs backend

# Test n8n integration directly
python
>>> from n8n_integration import N8nIntegration
>>> n8n = N8nIntegration()
>>> result = n8n.trigger_email_campaign({...})
>>> print(result)
```

---

## ✨ Benefits of n8n Integration

### **1. Visual Campaign Builder**
Modify campaigns in n8n's drag-and-drop editor - no code!

### **2. Better Error Handling**
See exactly which node failed and why

### **3. Easy A/B Testing**
Add switch nodes to test different templates

### **4. Centralized Monitoring**
All executions in one place with detailed logs

### **5. Flexible Workflows**
Add/remove nodes without changing code

### **6. Webhook Support**
Connect to any external service easily

### **7. Rate Limiting**
Visual delay nodes between actions

### **8. Conditional Logic**
IF nodes for smart routing

---

## 🎓 Next Steps

### **1. Create More Workflows**

Copy `WEBAPP_email_campaign.json` and modify for:
- SMS campaigns
- Lead enrichment
- Auto follow-ups
- Response handling

### **2. Add More Nodes**

Enhance workflows with:
- Slack notifications
- Google Sheets logging
- Custom webhooks
- Database inserts

### **3. Build Dashboard**

Use n8n's execution data to:
- Show real-time campaign progress
- Display success rates
- Track response rates

### **4. Schedule Campaigns**

Use n8n's Schedule Trigger:
- Daily email batches
- Weekly follow-ups
- Monthly reports

---

## 📚 Resources

### **Documentation:**
- n8n Docs: https://docs.n8n.io
- n8n Workflows: https://n8n.io/workflows
- Web App API: http://localhost:8000/docs

### **Example Payloads:**
```bash
# Get all examples
curl http://localhost:8000/api/n8n/example-payload?workflow_type=email_campaign
curl http://localhost:8000/api/n8n/example-payload?workflow_type=lead_enrichment
```

### **JSON Schemas:**
```bash
# Get all schemas
curl http://localhost:8000/api/n8n/schemas
```

---

## 🎉 Summary

**You now have:**

✅ Web app that triggers n8n workflows
✅ n8n-compatible JSON payloads
✅ Webhook-based communication
✅ Visual workflow editor
✅ Better monitoring and debugging
✅ More flexibility

**To use:**

1. Update backend to use n8n integration
2. Import workflows to n8n
3. Configure webhooks
4. Launch campaigns from web app
5. Monitor in n8n!

**Start now:**

```bash
cd outreach-automation/webapp/backend
cp main_n8n.py main.py
cd ..
./start.sh
```

Then launch a campaign and watch it execute in n8n! 🚀
