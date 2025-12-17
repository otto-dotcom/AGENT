# 🤖 JarvisBot Integration Guide
## Merge Outreach System into Your Central Command

Your outreach automation system is ready to integrate into JarvisBot - your central command for AI chat, stores, automations, and agents.

---

## 🎯 Integration Overview

**What This Does:**
- Adds "Campaigns" section to JarvisBot sidebar
- Launch outreach campaigns from your central command
- View all campaign analytics in one dashboard
- Manage leads, templates, and automations from JarvisBot
- Unified experience: AI chat + stores + automations + outreach campaigns

---

## 🚀 Quick Integration (Lovable Method)

### Step 1: Prepare Your Files

The outreach system components are in:
```
outreach-automation/webapp/frontend/src/
├── pages/
│   ├── Dashboard.jsx          # Campaign metrics
│   ├── Leads.jsx              # Lead management
│   ├── LaunchCampaign.jsx     # 4-step campaign wizard
│   ├── Campaigns.jsx          # Active campaign monitoring
│   ├── Templates.jsx          # Email/SMS templates
│   └── Analytics.jsx          # Performance analytics
└── components/
    └── Layout.jsx             # Navigation sidebar
```

### Step 2: Add to JarvisBot on Lovable

**Option A: Use Lovable AI to Import (Easiest)**

1. Open JarvisBot in Lovable: https://preview--jarvisbot.lovable.app/
2. Click the AI prompt in Lovable
3. Use this prompt:

```
Add a new "Campaigns" section to JarvisBot with these features:

1. Add "Campaigns" to the sidebar navigation
2. Create 5 new pages under /campaigns:
   - /campaigns/dashboard - Campaign metrics dashboard
   - /campaigns/leads - Lead management table
   - /campaigns/launch - 4-step campaign wizard
   - /campaigns/active - Active campaign monitoring
   - /campaigns/templates - Email/SMS template library

3. Use this color scheme:
   - Primary: Blue (#3B82F6)
   - Success: Green (#10B981)
   - Warning: Yellow (#F59E0B)
   - Danger: Red (#EF4444)

4. Features needed:
   - Lead filtering by status, industry, location
   - Campaign launch wizard with 4 steps
   - Real-time campaign status monitoring
   - Template preview and selection
   - Analytics charts for open rates, response rates

5. API endpoints (mock data for now):
   GET /api/leads - Get all leads
   GET /api/templates - Get email/SMS templates
   POST /api/campaigns/launch - Launch campaign
   GET /api/campaigns - Get all campaigns
   GET /api/analytics - Get campaign analytics
```

**Option B: Manual Copy-Paste Method**

1. Clone this repo to access the files:
```bash
git clone https://github.com/otto-dotcom/AGENT.git
cd AGENT/outreach-automation/webapp/frontend/src
```

2. In Lovable, create new pages:
   - Copy content from `pages/Dashboard.jsx` → Create `/campaigns/dashboard`
   - Copy content from `pages/Leads.jsx` → Create `/campaigns/leads`
   - Copy content from `pages/LaunchCampaign.jsx` → Create `/campaigns/launch`
   - Copy content from `pages/Campaigns.jsx` → Create `/campaigns/active`
   - Copy content from `pages/Templates.jsx` → Create `/campaigns/templates`
   - Copy content from `pages/Analytics.jsx` → Create `/campaigns/analytics`

3. Update JarvisBot sidebar navigation to include:
```jsx
{
  icon: "📧",
  label: "Campaigns",
  href: "/campaigns/dashboard"
}
```

### Step 3: Connect to Backend API

Add API configuration in JarvisBot:

```javascript
// Add to your API config
const OUTREACH_API_URL = "http://localhost:8000"

// Or use the demo server
const OUTREACH_API_URL = "http://localhost:8000"  // demo_server.py

// API functions
export const outreachAPI = {
  getLeads: () => fetch(`${OUTREACH_API_URL}/api/leads`).then(r => r.json()),
  getTemplates: () => fetch(`${OUTREACH_API_URL}/api/templates`).then(r => r.json()),
  launchCampaign: (data) => fetch(`${OUTREACH_API_URL}/api/campaigns/launch`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }).then(r => r.json()),
  getCampaigns: () => fetch(`${OUTREACH_API_URL}/api/campaigns`).then(r => r.json()),
  getAnalytics: () => fetch(`${OUTREACH_API_URL}/api/analytics`).then(r => r.json())
}
```

---

## 🎨 JarvisBot Navigation Structure (After Integration)

```
JarvisBot Central Command
├── 🏠 Home / Dashboard
├── 💬 AI Chat
├── 🏪 Stores
│   ├── Store 1
│   ├── Store 2
│   └── Store 3
├── 🤖 Automations & Agents
│   ├── Active Automations
│   └── Agent Management
└── 📧 Campaigns (NEW!)
    ├── 📊 Dashboard
    ├── 👥 Leads
    ├── 🚀 Launch Campaign
    ├── 📋 Active Campaigns
    ├── 📝 Templates
    └── 📈 Analytics
```

---

## 🔌 API Integration with n8n

The outreach system works with n8n workflows. Connect JarvisBot → n8n → Airtable:

**Workflow:**
```
JarvisBot UI
    ↓ (user launches campaign)
Backend API
    ↓ (sends JSON payload)
n8n Webhook
    ↓ (processes workflow)
Airtable + Email/SMS
    ↓ (sends messages)
Response tracking
    ↓ (updates JarvisBot)
Real-time dashboard updates
```

**n8n Webhook Setup:**
1. Import workflows from `/outreach-automation/n8n_workflows/`
2. Get webhook URL from n8n
3. Update `credentials.env` with n8n URL
4. JarvisBot will trigger campaigns via webhooks

---

## 📦 Required Dependencies

Add these to JarvisBot's package.json if not already present:

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "lucide-react": "^0.294.0",
    "axios": "^1.6.2"
  }
}
```

---

## 🧪 Testing the Integration

**1. Test in Demo Mode (No APIs Needed)**

Start the demo backend:
```bash
cd outreach-automation/webapp/backend
python3 demo_server.py
```

Access from JarvisBot: http://localhost:8000

**2. Test Campaign Launch Flow**

1. Navigate to Campaigns → Launch
2. Fill out campaign details
3. Select demo leads
4. Choose template
5. Launch in dry-run mode
6. Verify success message

**3. Test Real Integration**

When ready for production:
1. Add real credentials to `credentials.env`
2. Switch to `main_n8n.py` backend
3. Import n8n workflows
4. Test with small batch of real leads

---

## 🎯 Integration Benefits

**Before Integration:**
- Multiple apps to manage
- Separate logins and dashboards
- Context switching between systems
- Fragmented workflow

**After Integration:**
- ✅ One central command (JarvisBot)
- ✅ AI chat + stores + automations + campaigns
- ✅ Unified navigation
- ✅ Single dashboard for everything
- ✅ Streamlined workflow

---

## 🔐 Security Notes

**API Keys:**
Store in environment variables, never in code:
```env
AIRTABLE_API_KEY=xxx
N8N_API_KEY=xxx
OPENAI_API_KEY=xxx
```

**CORS Setup:**
Add JarvisBot domain to allowed origins:
```python
allow_origins=[
    "http://localhost:3000",
    "https://preview--jarvisbot.lovable.app",
    "https://jarvisbot.lovable.app"
]
```

---

## 🚀 Deployment Options

### Option 1: Keep Backend Separate
- Frontend: Deployed with JarvisBot on Lovable
- Backend: Deploy to Railway/Render/Vercel
- Connection: API calls between them

### Option 2: Unified Deployment
- Full stack on Lovable
- Include backend routes in JarvisBot
- Single deployment URL

### Option 3: Hybrid (Recommended)
- JarvisBot UI on Lovable (frontend)
- Outreach backend on Railway (API)
- n8n on n8n.cloud (workflows)
- Airtable for data (database)

---

## 📚 Next Steps

1. **Import to Lovable** using the AI prompt above
2. **Test in demo mode** with mock data
3. **Add real credentials** when ready
4. **Import n8n workflows** for automation
5. **Launch your first campaign** from JarvisBot!

---

## 💡 Pro Tips

**Lovable AI Prompts for Customization:**

- "Make the campaign dashboard match JarvisBot's color scheme"
- "Add a quick launch button to JarvisBot's main dashboard"
- "Show recent campaign stats on JarvisBot home page"
- "Add campaign notifications to JarvisBot's notification center"
- "Create a widget showing today's outreach metrics"

**Integration Workflow:**

1. Start with demo mode
2. Test UI/UX in JarvisBot
3. Customize to match your branding
4. Connect real APIs
5. Import n8n workflows
6. Launch campaigns!

---

## 🆘 Troubleshooting

**Issue: API calls failing**
- Check backend is running
- Verify CORS settings
- Check API URL in config

**Issue: Components not matching style**
- Use Lovable AI to match JarvisBot theme
- Update color variables
- Adjust spacing/fonts

**Issue: Navigation not working**
- Check React Router setup
- Verify routes in JarvisBot
- Update sidebar links

---

## 📞 Support

All source code is in:
- `/outreach-automation/webapp/frontend/` - React components
- `/outreach-automation/webapp/backend/` - FastAPI backend
- `/outreach-automation/n8n_workflows/` - Automation workflows

For help: Check other guides in `/outreach-automation/`:
- `COMPLETE_SYSTEM_GUIDE.md` - Full system documentation
- `LOVABLE_INTEGRATION.md` - General Lovable guide
- `N8N_INTEGRATION_GUIDE.md` - n8n setup
- `WEBAPP_GUIDE.md` - Web app features

---

**Ready to unite your command center! 🚀**
