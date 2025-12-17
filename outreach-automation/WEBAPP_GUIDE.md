# 🌐 Web Application Quick Start Guide

## 🎯 What You Get

A complete, production-ready web application to launch and manage your outreach campaigns with a beautiful, modern interface!

**No command line needed** - Everything in a visual dashboard!

---

## ⚡ Super Quick Start (5 Minutes)

### 1. **Navigate to the web app**
```bash
cd outreach-automation/webapp
```

### 2. **Start the application**
```bash
./start.sh
```

That's it! The app will:
- ✅ Check your credentials
- ✅ Install dependencies
- ✅ Start backend server (port 8000)
- ✅ Start frontend app (port 3000)
- ✅ Open in your browser

### 3. **Access your dashboard**
Open: **http://localhost:3000**

---

## 📸 What You'll See

### **Dashboard**
Real-time overview of your campaigns
- Total leads, emails sent, SMS sent
- Response rates and conversion metrics
- Recent activity feed
- Quick launch button

### **Leads**
Manage all your contacts
- Search and filter leads
- View by status (New, Ready, Contacted, Responded)
- Import/export capabilities
- Lead details and history

### **Launch Campaign**
Step-by-step campaign creation
- **Step 1**: Choose campaign type (Email, SMS, or Both)
- **Step 2**: Select leads with checkboxes
- **Step 3**: Pick a template
- **Step 4**: Review and launch!

### **Campaigns**
Track all your campaigns
- View running campaigns
- See completed campaigns
- Check success/error status
- Monitor execution details

### **Templates**
Browse and preview templates
- 3+ professional email templates
- 4+ optimized SMS templates
- Preview with sample data
- Edit and customize

### **Analytics**
Visual performance metrics
- Response rate tracking
- Lead distribution charts
- Industry breakdown
- Target achievement

### **Settings**
Configure your system
- System health monitoring
- Campaign settings (rate limits)
- API credential status
- Timezone configuration

---

## 🎨 Features

### ✅ Visual Campaign Builder
No code required - point, click, launch!

### ✅ Real-Time Updates
See campaign progress live with WebSockets

### ✅ Dry Run Mode
Test campaigns without actually sending

### ✅ Beautiful Analytics
Charts and metrics to track performance

### ✅ Lead Management
Filter, search, and organize your contacts

### ✅ Template Library
Professional, tested templates ready to use

### ✅ System Health
Monitor all integrations at a glance

---

## 🚀 Your First Campaign

### Step 1: Check Your Setup
1. Go to **Settings**
2. Verify "System Health" shows all green ✅
3. If not, check your credentials in `../config/credentials.env`

### Step 2: View Your Leads
1. Click **Leads** in sidebar
2. See all leads from your Airtable database
3. Use filters to find enriched leads

### Step 3: Launch Your First Campaign
1. Click **Launch Campaign** in sidebar
2. **Name your campaign** (e.g., "Test Campaign 1")
3. **Choose type**: Select "Email Only" for first test
4. **Enable Dry Run** ✅ (very important for testing!)
5. Click "Continue"

6. **Select Leads**:
   - Check 3-5 test leads
   - Click "Continue"

7. **Choose Template**:
   - Select "Discovery - Local Business Growth"
   - Click "Review Campaign"

8. **Review & Launch**:
   - Verify everything looks good
   - Note "Dry Run Mode" warning (no emails actually sent)
   - Click "Launch Campaign" 🚀

### Step 4: Monitor Results
1. You'll see "Campaign Launched!" success message
2. Go to **Campaigns** to see execution
3. Check **Dashboard** for updated stats

---

## 🎯 Campaign Workflow

```
Dashboard → Launch Campaign → Select Leads → Choose Template → Launch! → Monitor
```

### Full Production Launch (After Testing)

Once you've tested with dry run:

1. Go to **Settings**
2. Uncheck "Enable dry run mode by default"
3. Save settings
4. Launch your real campaign!
5. Monitor in **Analytics**

---

## 🔧 Technical Details

### Backend API
- **URL**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Tech**: FastAPI + Python 3.11

### Frontend App
- **URL**: http://localhost:3000
- **Tech**: React 18 + Vite + Tailwind CSS

### WebSocket
- **URL**: ws://localhost:8000/ws
- **Real-time updates** for campaign progress

---

## 🐳 Docker Deployment (Optional)

If you prefer Docker:

```bash
# Start with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## 🎨 Customization

### Change Branding
Edit `frontend/src/components/Layout.jsx`:
- Change "Outreach Pro" to your company name
- Update logo and colors

### Customize Colors
Edit `frontend/tailwind.config.js`:
```javascript
colors: {
  primary: {
    600: '#YOUR_COLOR',  // Main brand color
  },
}
```

### Add Custom Templates
Edit templates in `../templates/`:
- `email_templates.json` - Email templates
- `sms_templates.json` - SMS templates

---

## 📊 Understanding the Dashboard

### Key Metrics

**Total Leads**
- All leads in your database
- Green = ready for outreach

**Emails Sent**
- Successfully delivered emails
- Track open rates (coming soon)

**SMS Sent**
- SMS messages delivered
- Higher engagement than email

**Response Rate**
- % of leads that responded
- Target: >5%

### Status Breakdown
- **New Lead**: Just imported
- **Ready for Outreach**: Validated, ready to contact
- **Enriched**: AI insights added
- **Email Sent**: Email delivered
- **SMS Sent**: SMS delivered
- **Responded - Interested**: Positive response
- **Responded - Not Interested**: Opted out
- **Meeting Booked**: Success!

---

## 🔒 Safety Features

### Dry Run Mode
**Always test first!**
- Enable in campaign launcher
- No actual emails/SMS sent
- Verifies everything works
- Check logs and execution

### Rate Limiting
**Protect your sender reputation**
- Default: 50 emails/day
- Default: 30 SMS/day
- Gradual warm-up recommended
- Adjust in Settings

### Compliance
**Built-in best practices**
- Unsubscribe links in emails
- SMS opt-out (reply STOP)
- Business hours only
- Respect do-not-contact

---

## 💡 Pro Tips

### 1. Start Small
Test with 5-10 leads first, then scale

### 2. Use Dry Run
Always test new templates in dry run mode

### 3. Monitor Health
Check Settings → System Health regularly

### 4. Track Analytics
Review Analytics weekly to optimize

### 5. A/B Test
Try different templates, see what works

### 6. Segment Leads
Filter by industry for targeted messaging

---

## 🐛 Troubleshooting

### App Won't Start
```bash
# Check if ports are free
lsof -i :3000  # Frontend
lsof -i :8000  # Backend

# If occupied, kill the process
kill -9 PID
```

### Can't See Leads
1. Go to Settings
2. Check Airtable connection status
3. Verify credentials in `../config/credentials.env`

### Campaign Won't Launch
1. Check dry run mode is enabled for testing
2. Verify at least one lead is selected
3. Check backend logs: `docker-compose logs backend`

### Real-Time Updates Not Working
1. Check WebSocket connection in browser console
2. Verify backend is running
3. Refresh the page

---

## 📚 More Resources

- **API Documentation**: http://localhost:8000/docs (when running)
- **Main README**: `README.md`
- **Setup Guide**: `../docs/setup_guide.md`
- **Full README**: `../README.md`

---

## 🎉 You're Ready!

**Start your outreach machine:**

```bash
cd outreach-automation/webapp
./start.sh
```

Then visit **http://localhost:3000** and start launching campaigns! 🚀

---

**Questions?**
- Check the troubleshooting section
- Review the full documentation
- Check API logs for errors

**Happy campaigning! 📧📱🎯**
