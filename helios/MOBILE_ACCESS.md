# 📱 HELIOS Mobile Access Guide

## Overview

HELIOS is a Flask web application that runs on your **computer**, but you can access it from your **mobile device** (phone or tablet).

## 🚀 Quick Start

### On Your Computer:

```bash
cd helios
./start_webapp_mobile.sh
```

You'll see something like:

```
========================================
🌞 HELIOS Web App Starting
========================================

📱 Access from this computer:
   http://localhost:5000

📱 Access from mobile device:
   http://192.168.1.100:5000

💡 Make sure your phone is on the same WiFi network!
========================================
```

### On Your Mobile Device:

1. **Connect to the same WiFi network** as your computer
2. Open your mobile browser (Safari, Chrome, etc.)
3. Type the IP address shown: `http://192.168.x.x:5000`
4. Bookmark it for easy access!

## ✅ What Works on Mobile

✅ **Full UI Access**
- All tabs (Inspector, Config, Database, Scraper, Results)
- Responsive design adapts to screen size
- Touch-friendly buttons and forms

✅ **Page Inspector**
- Inspect GSE.it page structure
- View sample data
- See screenshots (saved on computer)

✅ **API Configuration**
- Enter and save credentials
- Test connections
- Secure storage on computer

✅ **Database Setup**
- View field requirements
- Copy SQL schema
- Setup instructions

✅ **Run Scraper**
- Trigger scraping from phone
- View progress updates
- See results

✅ **Results Viewer**
- Browse scraped leads
- View sample data
- Refresh results

## ⚠️ Limitations

❌ **Server Must Run on Computer**
- The actual scraping happens on your computer
- Mobile device is just the remote control
- Computer must stay on and connected

❌ **Same Network Required**
- Phone and computer must be on same WiFi
- Won't work over cellular data (unless you set up port forwarding)

❌ **Browser-Based Scraping**
- Selenium runs on computer, not phone
- Screenshots saved to computer, not phone

## 🔧 Setup Steps

### 1. Find Your Computer's IP Address

**Mac:**
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

**Linux:**
```bash
hostname -I
```

**Windows:**
```bash
ipconfig
```

Look for something like: `192.168.1.100`

### 2. Start HELIOS with Mobile Access

```bash
cd helios
./start_webapp_mobile.sh
```

The script automatically:
- Detects your IP address
- Binds Flask to `0.0.0.0` (accepts connections from any device)
- Shows the mobile access URL

### 3. Open on Your Phone

1. Open browser on phone
2. Type: `http://YOUR_IP:5000`
3. Example: `http://192.168.1.100:5000`

### 4. Bookmark for Quick Access

On iOS (Safari):
1. Tap the Share button
2. Tap "Add to Home Screen"
3. Name it "HELIOS"
4. Now it appears like an app!

On Android (Chrome):
1. Tap the three dots menu
2. Tap "Add to Home screen"
3. Name it "HELIOS"

## 🌐 Advanced: Access From Anywhere

If you want to access HELIOS from outside your home network:

### Option A: SSH Tunnel (Secure)

On your phone, use an SSH client to tunnel:

```bash
ssh -L 5000:localhost:5000 user@your-computer-ip
```

Then access: `http://localhost:5000` on phone

### Option B: Cloud Deployment

Deploy HELIOS to a cloud service:

**Heroku:**
```bash
# Create Procfile
echo "web: gunicorn -b 0.0.0.0:$PORT webapp.app:app" > Procfile

# Deploy
heroku create helios-scraper
git push heroku main
```

**Render/Railway/Fly.io:**
Similar process - deploy as a Python web app

### Option C: ngrok (Quick & Temporary)

```bash
# Install ngrok
brew install ngrok  # or download from ngrok.com

# Start HELIOS
./start_webapp.sh

# In another terminal
ngrok http 5000
```

You'll get a public URL like: `https://abc123.ngrok.io`

⚠️ **Security Warning:** This exposes your app to the internet!

### Option D: Tailscale (Secure VPN)

1. Install Tailscale on computer and phone
2. Start HELIOS normally
3. Access via Tailscale IP from anywhere

## 🔒 Security Considerations

### On Local Network (Safe)

✅ Only devices on your WiFi can access
✅ Credentials stored locally on computer
✅ No internet exposure

### On Public Internet (Be Careful!)

⚠️ **Add authentication** if exposing to internet
⚠️ **Use HTTPS** for production
⚠️ **Use environment variables** for secrets
⚠️ **Set strong Flask secret key**

### Quick Security Additions:

**1. Add Basic Auth:**

```python
# In webapp/app.py
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()

users = {
    "admin": "your-password-here"
}

@auth.verify_password
def verify_password(username, password):
    if username in users and users[username] == password:
        return username

@app.route('/')
@auth.login_required
def index():
    return render_template('index.html')
```

**2. Set Strong Secret Key:**

```bash
export FLASK_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
./start_webapp_mobile.sh
```

## 📊 Mobile UI Features

The mobile interface includes:

✅ **Responsive Design**
- Cards and forms adapt to screen size
- Scrollable tabs
- Full-width buttons on mobile

✅ **Touch Optimized**
- 44px minimum touch targets
- Swipeable tabs
- Large, easy-to-tap buttons

✅ **Mobile-Friendly Forms**
- Font size 16px (prevents iOS zoom)
- Proper input types for mobile keyboards
- Clear, readable text

✅ **Performance**
- Minimal animations on mobile
- Optimized for slower connections
- Progressive loading

## 🐛 Troubleshooting

### Can't Access from Phone

1. **Check same WiFi:**
   ```
   Phone Settings → WiFi → Network name
   Should match computer's network
   ```

2. **Check firewall:**
   ```bash
   # Mac
   System Preferences → Security → Firewall
   Allow incoming connections for Python

   # Linux
   sudo ufw allow 5000
   ```

3. **Try computer's IP:**
   - Don't use "localhost" on phone
   - Use the actual IP: `192.168.x.x`

4. **Check Flask is binding to 0.0.0.0:**
   ```bash
   # Should show 0.0.0.0:5000, not 127.0.0.1:5000
   netstat -an | grep 5000
   ```

### Page Loads But Doesn't Work

1. **Check browser console** (if possible)
2. **Try different browser** on phone
3. **Clear browser cache**
4. **Check computer's logs** for errors

### Slow on Mobile

1. **Use WiFi, not cellular data**
2. **Reduce number of concurrent operations**
3. **Enable dry-run mode** for testing
4. **Check computer's resources** (CPU/RAM)

### Screenshots/Files Not Showing

- Files are saved on **computer**, not phone
- Access them at: `helios/exports/`
- Download via file sharing if needed

## 💡 Pro Tips

1. **Bookmark the IP** - Save time typing
2. **Add to home screen** - Quick app-like access
3. **Use WiFi** - Much faster than cellular
4. **Keep computer awake** - Prevent sleep during scraping
5. **Use notifications** - Set up alerts when scraping completes

## 📱 Mobile Browser Recommendations

**iOS:**
- ✅ Safari (best compatibility)
- ✅ Chrome
- ⚠️ Firefox (may have issues with forms)

**Android:**
- ✅ Chrome (best compatibility)
- ✅ Samsung Internet
- ✅ Firefox

## 🔄 Workflow Example

**Scenario:** Scrape leads while away from computer

1. **Before leaving:**
   - Start HELIOS on computer: `./start_webapp_mobile.sh`
   - Note the IP address
   - Ensure computer won't sleep

2. **From phone:**
   - Open browser
   - Go to `http://YOUR_IP:5000`
   - Configure API keys (one-time)
   - Click "Run Scraper"
   - Choose target and start

3. **Monitor progress:**
   - View real-time stats
   - Check for errors
   - See results when complete

4. **When back at computer:**
   - Review detailed results
   - Check saved screenshots
   - Export data if needed

## 🎯 Best Use Cases

✅ **Remote Triggering**
- Start scraping from anywhere in the house
- Check results from bed/couch
- Monitor progress on the go

✅ **Configuration**
- Update API keys from phone
- Test connections remotely
- Manage database settings

✅ **Quick Checks**
- View recent results
- Check scraping status
- Browse sample leads

❌ **Not Ideal For:**
- Heavy data entry (use computer)
- Reviewing large datasets
- Debugging scraper code
- Viewing full-size screenshots

## 📚 Additional Resources

- **Main README:** `/helios/README.md`
- **Web App Guide:** `/helios/webapp/README.md`
- **Quick Start:** `/helios/QUICKSTART_WEB.md`

---

**Remember:** HELIOS runs on your computer, your phone is just the remote control! 📱➡️💻
