# 🚀 Outreach Campaign Manager - Web Application

A modern, beautiful web application for managing your automated outreach campaigns.

![Dashboard Preview](https://via.placeholder.com/800x400/3B82F6/FFFFFF?text=Outreach+Campaign+Manager)

## ✨ Features

### 📊 **Campaign Dashboard**
- Real-time campaign statistics
- Lead status breakdown
- Recent activity feed
- Quick launch access

### 👥 **Lead Management**
- View and filter all leads
- Search by company, contact, or email
- Filter by status and industry
- Import/export capabilities
- Detailed lead profiles

### 🚀 **Campaign Launcher**
- Step-by-step campaign creation
- Select leads with filters
- Choose from professional templates
- Preview before sending
- Schedule or launch immediately
- Dry-run mode for testing

### 📧 **Template Library**
- Professional email templates
- Optimized SMS templates
- Preview and edit templates
- Variable substitution
- A/B testing support

### 📈 **Analytics Dashboard**
- Response rate tracking
- Conversion metrics
- Lead distribution charts
- Industry breakdown
- Performance targets

### ⚙️ **Settings & Configuration**
- System health monitoring
- Campaign settings
- API credential status
- Rate limiting controls

## 🎯 Tech Stack

### Backend
- **FastAPI** - Modern, fast Python web framework
- **Python 3.11+** - Latest Python features
- **WebSockets** - Real-time updates
- **REST API** - Clean, documented endpoints

### Frontend
- **React 18** - Modern React with hooks
- **Vite** - Lightning-fast build tool
- **Tailwind CSS** - Beautiful, responsive design
- **Lucide Icons** - Modern icon library
- **Axios** - API communication
- **React Router** - Navigation

## 📦 Installation

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm or yarn
- Docker (optional)

### Quick Start

1. **Clone and navigate to the webapp directory**
   ```bash
   cd outreach-automation/webapp
   ```

2. **Set up environment variables**
   ```bash
   # Make sure credentials are in ../config/credentials.env
   # The start script will load them automatically
   ```

3. **Start the application**
   ```bash
   ./start.sh
   ```

   The script will:
   - Check for credentials
   - Detect if Docker is available
   - Start backend and frontend
   - Open your browser automatically

4. **Access the application**
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:8000
   - **API Docs**: http://localhost:8000/docs

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

### Manual Docker Setup

**Backend:**
```bash
cd backend
docker build -t outreach-backend .
docker run -p 8000:8000 --env-file ../../config/credentials.env outreach-backend
```

**Frontend:**
```bash
cd frontend
docker build -t outreach-frontend .
docker run -p 3000:3000 outreach-frontend
```

## 🔧 Development

### Backend Development

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run development server with hot reload
uvicorn main:app --reload --port 8000

# Run with auto-reload
python -m uvicorn main:app --reload
```

**API Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 📡 API Endpoints

### Lead Management
- `GET /api/leads` - Get all leads
- `GET /api/leads/{id}` - Get single lead
- `GET /api/leads/stats` - Get lead statistics

### Campaign Management
- `POST /api/campaigns/launch` - Launch new campaign
- `GET /api/campaigns` - Get all campaigns
- `GET /api/campaigns/{id}` - Get campaign details

### Analytics
- `GET /api/analytics/overview` - Get overview stats
- `GET /api/analytics/by-status` - Leads by status
- `GET /api/analytics/by-industry` - Leads by industry

### Templates
- `GET /api/templates/email` - Get email templates
- `GET /api/templates/sms` - Get SMS templates
- `POST /api/templates/preview` - Preview template

### System
- `GET /api/health` - System health check
- `GET /api/workflows` - Get n8n workflows
- `WS /ws` - WebSocket for real-time updates

## 🎨 Customization

### Styling

The app uses Tailwind CSS. Customize the theme in `frontend/tailwind.config.js`:

```javascript
theme: {
  extend: {
    colors: {
      primary: {
        // Your brand colors
      },
    },
  },
}
```

### Templates

Add custom templates in:
- `../templates/email_templates.json`
- `../templates/sms_templates.json`

### Branding

Update branding in `frontend/src/components/Layout.jsx`:
- Logo
- App name
- Color scheme

## 🚀 Deployment

### Production Build

**Frontend:**
```bash
cd frontend
npm run build
# Files will be in dist/
```

**Backend:**
```bash
# Set production environment
export ENV=production

# Run with Gunicorn
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Deploy to Cloud

#### Heroku
```bash
# Add Heroku remote
heroku create your-app-name

# Set environment variables
heroku config:set AIRTABLE_API_KEY=your_key

# Deploy
git push heroku main
```

#### AWS/GCP/Azure
Use the provided Docker images for easy deployment to any cloud platform.

## 📊 Usage

### 1. First Time Setup

1. Navigate to **Settings**
2. Verify all API connections are healthy
3. Configure campaign settings (rate limits, timezone)

### 2. Import Leads

1. Go to **Leads**
2. Click "Import"
3. Upload CSV or sync from Airtable

### 3. Launch Campaign

1. Click **Launch Campaign**
2. Select campaign type (Email, SMS, or Both)
3. Choose your leads
4. Pick a template
5. Review and launch!

### 4. Monitor Performance

1. View **Dashboard** for overview
2. Check **Analytics** for detailed metrics
3. Monitor **Campaigns** for execution status

## 🔒 Security

### Best Practices

- Never commit `.env` files
- Use environment variables for all secrets
- Enable dry-run mode for testing
- Regularly rotate API keys
- Monitor API usage and costs

### Rate Limiting

The app includes built-in rate limiting:
- Default: 50 emails/day, 30 SMS/day
- Adjust in Settings
- Gradual warm-up recommended

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.11+

# Reinstall dependencies
pip install --force-reinstall -r backend/requirements.txt

# Check for port conflicts
lsof -i :8000
```

### Frontend won't start
```bash
# Check Node version
node --version  # Should be 18+

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Check for port conflicts
lsof -i :3000
```

### Can't connect to Airtable/n8n
- Verify credentials in `config/credentials.env`
- Check API key permissions
- Test connection: `curl -H "Authorization: Bearer $AIRTABLE_API_KEY" https://api.airtable.com/v0/$AIRTABLE_BASE_ID`

### WebSocket connection fails
- Check CORS settings in backend
- Verify proxy configuration in Vite
- Check firewall/network settings

## 📖 Documentation

- **API Documentation**: http://localhost:8000/docs (when running)
- **Full Setup Guide**: `../docs/setup_guide.md`
- **Airtable Integration**: `../docs/airtable_exploration_guide.md`
- **Main README**: `../README.md`

## 🤝 Contributing

This is a custom internal tool. For questions or issues:
1. Check the documentation
2. Review the troubleshooting section
3. Check API logs for errors

## 📝 License

Proprietary - Internal Use Only

## 🎉 Credits

Built with:
- FastAPI
- React
- Tailwind CSS
- n8n
- OpenAI
- Airtable
- Twilio
- Mailchimp

Inspired by Nate Herk's automation methodology.

---

**Ready to launch your campaigns? Start the app:**

```bash
./start.sh
```

Then visit http://localhost:3000 🚀
