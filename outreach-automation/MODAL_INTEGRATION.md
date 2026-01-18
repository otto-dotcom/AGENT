# Modal Integration Guide

## Overview

This guide explains how to use Modal Labs serverless platform to run outreach campaigns at scale. Modal allows you to execute compute-intensive tasks like AI personalization and bulk messaging without managing infrastructure.

## What is Modal?

[Modal](https://modal.com) is a serverless compute platform that lets you run Python functions in the cloud. With Modal, you can:

- **Scale automatically**: Run thousands of parallel tasks without provisioning servers
- **Pay per use**: Only pay for compute time actually used
- **Deploy easily**: Deploy with a single command
- **Integrate seamlessly**: Call Modal functions from your existing FastAPI backend

## Architecture

```
Web App (React)
    ↓ HTTP
FastAPI Backend
    ↓ Modal Client SDK
Modal Cloud Platform
    ├── Personalization Functions (OpenAI GPT-4)
    ├── Email Sending (Mailchimp)
    ├── SMS Sending (Twilio)
    └── n8n Workflow Triggers
```

## Setup Instructions

### 1. Install Modal CLI

```bash
# Install Modal
pip install modal

# Authenticate with Modal
modal token new
```

This will open a browser window to authenticate with your Modal account (or create one if you don't have one).

### 2. Set Up Credentials

Modal needs access to your API credentials. You have two options:

#### Option A: Using Modal Secrets (Recommended for Production)

Create secrets in the Modal dashboard:

```bash
# Create a secret for each service
modal secret create outreach-secrets \
  OPENAI_API_KEY=<your-key> \
  AIRTABLE_API_KEY=<your-key> \
  AIRTABLE_BASE_ID=<your-base-id> \
  TWILIO_ACCOUNT_SID=<your-sid> \
  TWILIO_AUTH_TOKEN=<your-token> \
  TWILIO_PHONE_NUMBER=<your-number> \
  MAILCHIMP_API_KEY=<your-key> \
  MAILCHIMP_SERVER_PREFIX=<your-prefix> \
  MAILCHIMP_LIST_ID=<your-list-id> \
  N8N_API_URL=<your-url> \
  N8N_API_KEY=<your-key>
```

#### Option B: Using Environment Variables (Development)

Set environment variables in your `.env` file or shell:

```bash
export OPENAI_API_KEY=your_key_here
export AIRTABLE_API_KEY=your_key_here
# ... etc
```

### 3. Deploy Modal App

From the `outreach-automation` directory:

```bash
# Deploy the Modal app
modal deploy modal_app.py
```

You should see output like:

```
✓ Created objects.
├── 🔨 Created function personalize_message.
├── 🔨 Created function personalize_messages_batch.
├── 🔨 Created function send_email_via_mailchimp.
├── 🔨 Created function send_sms_via_twilio.
├── 🔨 Created function execute_campaign.
└── 🔨 Created function trigger_n8n_workflow.

✓ App deployed! 🎉
```

### 4. Configure Backend

Add Modal credentials to your backend `.env` file:

```bash
# Modal Configuration
MODAL_TOKEN_ID=your_modal_token_id
MODAL_TOKEN_SECRET=your_modal_token_secret
```

These can be found in your Modal dashboard under Settings → API Tokens.

### 5. Restart Backend

```bash
cd webapp/backend
uvicorn main:app --reload
```

## Using Modal Functions

### Check Modal Status

```bash
curl http://localhost:8000/api/modal/status
```

Response:
```json
{
  "available": true,
  "message": "Modal integration is active"
}
```

### Personalize a Single Message

```bash
curl -X POST http://localhost:8000/api/modal/personalize \
  -H "Content-Type: application/json" \
  -d '{
    "lead_data": {
      "id": "lead_001",
      "name": "Jane Smith",
      "company": "TechCorp",
      "industry": "Software"
    },
    "template": "Hi {name}, I noticed {company} is in the {industry} space...",
    "model": "gpt-4-turbo-preview"
  }'
```

Response:
```json
{
  "success": true,
  "lead_id": "lead_001",
  "personalized_message": "Hi Jane, I noticed TechCorp is doing amazing work in the Software space. I'd love to discuss how...",
  "tokens_used": 145,
  "model": "gpt-4-turbo-preview"
}
```

### Launch a Campaign on Modal

```bash
curl -X POST http://localhost:8000/api/modal/campaigns/launch \
  -H "Content-Type: application/json" \
  -d '{
    "campaign_id": "campaign_001",
    "campaign_type": "email",
    "template": "Hi {name}, ...",
    "leads": [
      {"id": "1", "name": "John", "email": "john@example.com"},
      {"id": "2", "name": "Jane", "email": "jane@example.com"}
    ],
    "personalize": true,
    "dry_run": true
  }'
```

Response:
```json
{
  "status": "launching",
  "campaign_id": "campaign_001",
  "campaign_type": "email",
  "lead_count": 2,
  "personalize": true,
  "dry_run": true,
  "execution_platform": "modal"
}
```

## Modal Functions Reference

### 1. `personalize_message`

Personalizes a single message using OpenAI GPT-4.

**Parameters:**
- `lead_data` (dict): Lead information (id, name, company, etc.)
- `template` (str): Message template with placeholders
- `model` (str): OpenAI model to use (default: "gpt-4-turbo-preview")

**Returns:**
```json
{
  "success": true,
  "lead_id": "...",
  "personalized_message": "...",
  "tokens_used": 150,
  "model": "gpt-4-turbo-preview"
}
```

### 2. `personalize_messages_batch`

Personalizes messages for multiple leads in parallel.

**Parameters:**
- `leads` (list): List of lead dictionaries
- `template` (str): Message template
- `model` (str): OpenAI model to use

**Returns:** List of personalization results

### 3. `execute_campaign`

Executes a full campaign (personalization + sending).

**Parameters:**
- `campaign_id` (str): Unique campaign identifier
- `campaign_type` (str): "email" or "sms"
- `leads` (list): List of lead dictionaries
- `template` (str): Message template
- `personalize` (bool): Whether to use AI personalization
- `dry_run` (bool): If true, don't actually send messages

**Returns:**
```json
{
  "campaign_id": "...",
  "campaign_type": "email",
  "total_leads": 100,
  "personalized": 100,
  "sent": 100,
  "failed": 0,
  "errors": [],
  "dry_run": false
}
```

### 4. `send_email_via_mailchimp`

Sends a single email via Mailchimp.

**Parameters:**
- `recipient_email` (str): Email address
- `subject` (str): Email subject
- `message` (str): Email body
- `lead_data` (dict, optional): Lead metadata

### 5. `send_sms_via_twilio`

Sends a single SMS via Twilio.

**Parameters:**
- `recipient_phone` (str): Phone number (E.164 format)
- `message` (str): SMS message
- `lead_data` (dict, optional): Lead metadata

### 6. `trigger_n8n_workflow`

Triggers an n8n workflow from Modal.

**Parameters:**
- `workflow_id` (str): n8n workflow ID
- `payload` (dict): Data to send to workflow

## Testing Modal Functions Locally

You can test Modal functions locally before deploying:

```bash
# Run the test entrypoint
modal run modal_app.py

# This will test personalization with sample data
```

## Monitoring and Debugging

### View Modal Logs

```bash
# View logs for a specific function
modal logs personalize_message

# View all logs for the app
modal logs outreach-automation
```

### Monitor Function Usage

Visit the Modal dashboard at https://modal.com/dashboard to:

- View function execution history
- Monitor costs and compute usage
- See error rates and performance metrics
- Debug failed executions

## Cost Optimization

Modal charges based on:
- **CPU time**: Per-second billing for active computation
- **GPU time**: If using GPU-accelerated models
- **Memory**: Based on container memory usage

### Tips to Reduce Costs:

1. **Use batch functions**: Process multiple items in one function call
2. **Set appropriate timeouts**: Avoid runaway executions
3. **Use smaller models**: Consider gpt-3.5-turbo for simple personalization
4. **Enable dry_run**: Test campaigns without sending (and without API costs)

Example cost for 1000 leads:
- Personalization: ~$0.50-2.00 (depending on model)
- Modal compute: ~$0.10-0.50
- **Total**: ~$0.60-2.50 per 1000 personalized messages

## Comparison: Local vs Modal Execution

| Feature | Local Execution | Modal Execution |
|---------|----------------|-----------------|
| **Scale** | Limited by your machine | Unlimited parallel workers |
| **Cost** | Free (uses your resources) | Pay per use (~$0.001/second) |
| **Setup** | No additional setup | Requires Modal account + deploy |
| **Speed** | Sequential processing | Parallel processing |
| **Reliability** | Depends on your machine | Enterprise-grade infrastructure |
| **Monitoring** | Local logs only | Dashboard + metrics |

## When to Use Modal

✅ **Use Modal when:**
- Running campaigns with 100+ leads
- Need to process leads in parallel
- Want to offload compute from your server
- Scaling to thousands of messages
- Running campaigns on a schedule

❌ **Skip Modal when:**
- Testing with < 10 leads
- Running locally for development
- Budget is very tight
- Don't need parallel processing

## Troubleshooting

### "Modal integration not available"

**Solution:**
1. Ensure Modal app is deployed: `modal deploy modal_app.py`
2. Check Modal credentials in `.env`
3. Verify Modal token: `modal token set --token-id <id> --token-secret <secret>`

### "Function not found"

**Solution:**
Redeploy the Modal app:
```bash
modal deploy modal_app.py --force
```

### "Authentication failed"

**Solution:**
Re-authenticate with Modal:
```bash
modal token new
```

### API Keys Not Working

**Solution:**
Ensure secrets are properly set:
```bash
modal secret list
# If missing, create them:
modal secret create outreach-secrets KEY=value ...
```

## Next Steps

1. **Test locally**: Run `modal run modal_app.py` to test
2. **Deploy**: Run `modal deploy modal_app.py`
3. **Try the API**: Use the `/api/modal/*` endpoints
4. **Monitor**: Check the Modal dashboard for execution metrics
5. **Scale**: Launch campaigns with hundreds or thousands of leads

## Additional Resources

- [Modal Documentation](https://modal.com/docs)
- [Modal Pricing](https://modal.com/pricing)
- [Modal Python SDK](https://modal.com/docs/reference)
- [OpenAI API Docs](https://platform.openai.com/docs)

## Support

For issues or questions:
- Modal support: https://modal.com/support
- This project: [Create an issue](https://github.com/your-repo/issues)
