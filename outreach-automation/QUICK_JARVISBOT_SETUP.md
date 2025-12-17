# 🚀 Quick JarvisBot Integration - 3 Steps

## Get Campaigns Running in JarvisBot in Under 5 Minutes

---

## Step 1️⃣: Copy the Lovable Prompt (30 seconds)

1. Open file: `outreach-automation/LOVABLE_PROMPT.txt`
2. Copy the entire prompt
3. Done!

---

## Step 2️⃣: Add to JarvisBot (2 minutes)

1. Go to your JarvisBot in Lovable: https://preview--jarvisbot.lovable.app/
2. Click the AI chat/prompt input in Lovable
3. Paste the prompt from Step 1
4. Press Enter
5. Watch Lovable build the Campaigns section automatically!

---

## Step 3️⃣: Start the Backend (1 minute)

**Option A: Demo Mode (No API Keys Needed)**
```bash
cd outreach-automation/webapp/backend
python3 demo_server.py
```

**Option B: Production Mode (With Your APIs)**
```bash
# Add your API keys to credentials.env first
cd outreach-automation/webapp/backend
python3 -m uvicorn main_n8n:app --reload
```

---

## ✅ Done! You Now Have:

```
JarvisBot Central Command
├── 💬 AI Chat
├── 🏪 Your Stores
├── 🤖 Automations & Agents
└── 📧 Campaigns (NEW!)
    ├── 📊 Dashboard - See all metrics
    ├── 👥 Leads - Manage contacts
    ├── 🚀 Launch - Start campaigns
    ├── 📋 Active - Monitor progress
    ├── 📝 Templates - Email/SMS library
    └── 📈 Analytics - Performance data
```

---

## 🎯 Your First Campaign (30 seconds)

1. In JarvisBot, click **"Campaigns"** in sidebar
2. Click **"Launch Campaign"**
3. Follow the 4-step wizard:
   - Name your campaign
   - Select demo leads
   - Choose a template
   - Launch in dry-run mode
4. See results in **"Active Campaigns"**!

---

## 🔗 How It All Connects

```
You
 ↓
JarvisBot (Lovable)
 ↓
Backend API (FastAPI)
 ↓
n8n Workflows (n8n.cloud)
 ↓
Airtable (Your Kronos Database)
 ↓
Email/SMS Services (Mailchimp/Twilio)
```

---

## 📝 What You Can Do Now

**In Demo Mode:**
- ✅ Launch test campaigns
- ✅ See how the UI works
- ✅ Explore all features
- ✅ No API keys needed!

**In Production Mode (After Adding API Keys):**
- ✅ Launch real campaigns
- ✅ Send actual emails/SMS
- ✅ Track real responses
- ✅ Automate with n8n

---

## 🆘 Quick Troubleshooting

**Problem:** Lovable can't find the API
**Solution:** Make sure backend is running on port 8000

**Problem:** No leads showing
**Solution:** Using demo_server.py? It has 50 mock leads built-in

**Problem:** Campaign won't launch
**Solution:** Check "Dry Run" is ON for testing

**Problem:** Want to match JarvisBot colors
**Solution:** Tell Lovable AI: "Update campaign colors to match JarvisBot theme"

---

## 🚀 Next Steps

1. **Test in Demo Mode** - Launch a test campaign
2. **Customize Design** - Ask Lovable to match your style
3. **Add Real Credentials** - When ready for production
4. **Import n8n Workflows** - For full automation
5. **Launch Real Campaigns** - Start reaching out!

---

## 📚 Full Documentation

- `JARVISBOT_INTEGRATION.md` - Complete integration guide
- `COMPLETE_SYSTEM_GUIDE.md` - Full system documentation
- `N8N_INTEGRATION_GUIDE.md` - n8n workflow setup
- `WEBAPP_GUIDE.md` - Web app features

---

**That's it! Your central command is ready to launch campaigns! 🎉**
