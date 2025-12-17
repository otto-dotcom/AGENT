# 🚀 Automated Outreach Machine

**Built by Otto | Powered by n8n, AI, and Smart Automation**

## 📖 Overview

This is an n8n-powered automation system for personalized email and SMS outreach campaigns targeting businesses in the Kronos Airtable database. The system follows Nate Herk's automation methodology principles to create scalable, personalized multi-channel outreach at scale.

## 🎯 Core Principles

1. **Automation Over Manual Labor**: Build systems that scale infinitely
2. **Personalization at Scale**: Use data fields to create unique messages
3. **Multi-Channel Approach**: Email + SMS + Social for maximum reach
4. **Smart Segmentation**: Target based on business data
5. **Iterative Testing**: A/B test everything, optimize continuously

## 🏗️ System Architecture

```
┌─────────────────┐
│  Apify Scraper  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Airtable     │ ◄───┐
│  (Kronos DB)    │     │
└────────┬────────┘     │
         │              │
         ▼              │
┌─────────────────┐     │
│  n8n Workflow   │     │
│  Lead Enrichment│     │
└────────┬────────┘     │
         │              │
         ▼              │
┌─────────────────┐     │
│  GPT-4 AI       │     │
│  Personalization│     │
└────────┬────────┘     │
         │              │
         ├──────────────┼─── Email Campaign (Mailchimp)
         │              │
         └──────────────┼─── SMS Campaign (Twilio)
                        │
                        │
         ┌──────────────┘
         │
         ▼
┌─────────────────┐
│  Response       │
│  Tracker        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Auto Follow-up │
│  System         │
└─────────────────┘
```

## 📁 Project Structure

```
outreach-automation/
├── README.md                          # This file
├── config/
│   ├── airtable_config.json          # Airtable connection settings
│   ├── n8n_config.json               # n8n instance configuration
│   └── credentials.example.env       # Template for API credentials
├── n8n_workflows/
│   ├── 01_lead_enrichment.json       # Workflow: Lead enrichment
│   ├── 02_email_campaign.json        # Workflow: Email campaigns
│   ├── 03_sms_campaign.json          # Workflow: SMS campaigns
│   ├── 04_response_tracker.json      # Workflow: Response tracking
│   └── 05_auto_followup.json         # Workflow: Automated follow-ups
├── templates/
│   ├── email_templates.json          # Email message templates
│   ├── sms_templates.json            # SMS message templates
│   └── personalization_vars.json     # Available personalization variables
├── scripts/
│   ├── airtable_connector.py         # Airtable API helper functions
│   ├── personalization_engine.py     # Message personalization logic
│   ├── data_validator.py             # Data quality validation
│   └── analytics_tracker.py          # Campaign analytics and reporting
├── docs/
│   ├── setup_guide.md                # Complete setup instructions
│   ├── airtable_schema.md            # Airtable database structure
│   ├── workflow_guide.md             # n8n workflow documentation
│   ├── best_practices.md             # Outreach best practices
│   └── troubleshooting.md            # Common issues and solutions
└── tests/
    ├── test_data.json                # Sample test data
    ├── test_personalization.py       # Unit tests for personalization
    └── validate_workflows.py         # Workflow validation scripts
```

## 🚀 Quick Start

### Prerequisites

- n8n instance access: https://fagiolinosssssss.app.n8n.cloud/mcp-server/http
- Airtable account with Kronos database
- Twilio account (SMS)
- Mailchimp account (Email)
- OpenAI API key (for AI personalization)

### Installation

1. **Clone and navigate to the project**
   ```bash
   cd outreach-automation
   ```

2. **Set up credentials**
   ```bash
   cp config/credentials.example.env config/credentials.env
   # Edit credentials.env with your API keys
   ```

3. **Document your Airtable structure**
   ```bash
   python scripts/airtable_connector.py --document-schema
   ```

4. **Import n8n workflows**
   - Log into your n8n instance
   - Import workflows from `n8n_workflows/` directory
   - Configure credentials for each service

5. **Test with sample data**
   ```bash
   python tests/validate_workflows.py
   ```

## 📊 Workflows Overview

### 1. Lead Enrichment Pipeline
**Purpose**: Prepare leads for outreach by enriching data with AI insights

**Trigger**: Schedule (daily) or Manual
**Input**: Airtable records with `Status = "Ready for Outreach"`
**Output**: Enriched records with `Status = "Enriched"`

### 2. Email Campaign Launcher
**Purpose**: Send personalized emails via Mailchimp

**Trigger**: Manual/Schedule
**Input**: Enriched leads
**Output**: Sent emails with tracking

### 3. SMS Campaign Launcher
**Purpose**: Send personalized SMS via Twilio

**Trigger**: Manual/Schedule
**Input**: Leads with `Status = "Email Sent"`, `Days_Since_Email > 2`
**Output**: Sent SMS messages

### 4. Response Tracker
**Purpose**: Monitor replies and categorize responses

**Trigger**: Webhook (Mailchimp/Twilio)
**Input**: Email/SMS replies
**Output**: Updated lead status and next actions

### 5. Auto Follow-up System
**Purpose**: Re-engage non-responders with contextual follow-ups

**Trigger**: Schedule (weekly)
**Input**: Leads with no response after 7 days
**Output**: Follow-up messages sent

## 📧 Message Templates

### Email Structure
- **Subject**: Personalized hook based on company data
- **Opening**: Reference to their business/location/industry
- **Pain Point**: Industry-specific challenge
- **Solution Tease**: Your value proposition
- **CTA**: Low-pressure call to action
- **P.S.**: Personalized insight

### SMS Structure
- **Greeting**: Hi [Name]
- **Hook**: Personal observation about business
- **Value Prop**: Quick question/benefit (1 line)
- **CTA**: Soft ask (e.g., "Reply YES for details")

## 📈 Success Metrics

Target metrics:
- ✅ 100+ personalized emails per day
- ✅ 50+ personalized SMS per day
- ✅ Response rate > 5%
- ✅ Meeting booking rate > 1%
- ✅ System maintenance < 10 min/day

## 🔒 Compliance & Best Practices

### Legal Requirements
- ✅ Include unsubscribe link in all emails
- ✅ GDPR compliance for EU contacts
- ✅ SMS opt-out mechanism (Reply STOP)
- ✅ Honest sender identification
- ✅ Clear value proposition

### Quality Guidelines
- Max 50 emails per day (warm up period)
- Max 30 SMS per day
- Never send after 8 PM local time
- Respect "Do Not Contact" list
- Monitor complaint rates

## 📚 Documentation

Detailed guides available in the `docs/` directory:
- [Setup Guide](docs/setup_guide.md) - Complete installation instructions
- [Airtable Schema](docs/airtable_schema.md) - Database structure reference
- [Workflow Guide](docs/workflow_guide.md) - n8n workflow documentation
- [Best Practices](docs/best_practices.md) - Outreach optimization tips
- [Troubleshooting](docs/troubleshooting.md) - Common issues and fixes

## 🛠️ Helper Scripts

### Airtable Connector
```bash
python scripts/airtable_connector.py --document-schema
python scripts/airtable_connector.py --validate-data
python scripts/airtable_connector.py --export-leads
```

### Personalization Engine
```bash
python scripts/personalization_engine.py --test-templates
python scripts/personalization_engine.py --generate-preview
```

### Analytics Tracker
```bash
python scripts/analytics_tracker.py --campaign-report
python scripts/analytics_tracker.py --export-metrics
```

## 📞 Support

For issues or questions:
- Check [Troubleshooting Guide](docs/troubleshooting.md)
- Review n8n workflow logs
- Validate Airtable data quality
- Test with small batches first

## 📅 Development Roadmap

### Week 1: Foundation (Current Phase)
- [x] Set up project structure
- [ ] Document Airtable schema
- [ ] Create message templates
- [ ] Build helper scripts

### Week 2: Build
- [ ] Create all 5 n8n workflows
- [ ] Test with dummy data
- [ ] Fix bugs and optimize

### Week 3: Launch
- [ ] Soft launch with 50 leads
- [ ] Monitor responses
- [ ] Iterate based on feedback

### Week 4: Scale
- [ ] Roll out to full database
- [ ] Automate reporting
- [ ] Optimize for efficiency

## 🎓 Credits

Inspired by Nate Herk's "Book of 8" automation methodology:
- "Automation is the multiplier of human intention"
- "Build once, deploy infinitely"
- "Personalization at scale beats generic mass outreach"

---

**Version**: 1.0.0
**Last Updated**: 2025-12-17
**Maintained by**: Otto
