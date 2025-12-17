"""
Demo Server - No credentials required!
This lets you explore the UI without setting up APIs
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import random

app = FastAPI(
    title="Outreach Campaign Manager - DEMO MODE",
    description="Demo mode - no credentials required",
    version="1.0.0-demo"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data
MOCK_LEADS = [
    {"id": f"lead_{i}", "name": f"Business {i}", "email": f"contact{i}@business.com",
     "phone": f"+1555000{i:04d}", "industry": random.choice(["Tech", "Retail", "Services"]),
     "location": random.choice(["New York", "San Francisco", "Chicago"]),
     "status": random.choice(["new", "contacted", "responded"])}
    for i in range(1, 51)
]

MOCK_TEMPLATES = [
    {"id": "email_v1", "name": "Discovery Email", "type": "email",
     "subject": "Quick question about {{companyName}}", "body": "Hi {{firstName}}..."},
    {"id": "email_v2", "name": "Value Proposition", "type": "email",
     "subject": "Help {{companyName}} grow", "body": "Hi {{firstName}}..."},
    {"id": "sms_v1", "name": "SMS Direct", "type": "sms", "body": "Hi {{firstName}}, quick question..."}
]

MOCK_CAMPAIGNS = []

class CampaignLaunch(BaseModel):
    campaign_name: str
    campaign_type: str
    template_id: str
    lead_ids: List[str]
    dry_run: bool = True

@app.get("/")
async def root():
    return {"app": "Outreach Manager", "mode": "DEMO", "status": "running"}

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "mode": "demo",
        "airtable": "demo",
        "n8n": "demo",
        "openai": "demo"
    }

@app.get("/api/leads")
async def get_leads(status: Optional[str] = None):
    leads = MOCK_LEADS
    if status:
        leads = [l for l in leads if l["status"] == status]
    return {"leads": leads, "total": len(leads)}

@app.get("/api/leads/{lead_id}")
async def get_lead(lead_id: str):
    lead = next((l for l in MOCK_LEADS if l["id"] == lead_id), None)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead

@app.get("/api/templates")
async def get_templates():
    return {"templates": MOCK_TEMPLATES}

@app.get("/api/campaigns")
async def get_campaigns():
    return {"campaigns": MOCK_CAMPAIGNS}

@app.post("/api/campaigns/launch")
async def launch_campaign(campaign: CampaignLaunch):
    campaign_data = {
        "id": f"camp_{len(MOCK_CAMPAIGNS)+1}",
        "name": campaign.campaign_name,
        "type": campaign.campaign_type,
        "template_id": campaign.template_id,
        "lead_count": len(campaign.lead_ids),
        "status": "running" if not campaign.dry_run else "dry_run",
        "created_at": datetime.now().isoformat(),
        "sent": 0,
        "delivered": 0,
        "opened": 0,
        "responded": 0
    }
    MOCK_CAMPAIGNS.append(campaign_data)
    return {
        "success": True,
        "campaign_id": campaign_data["id"],
        "message": "Demo campaign launched! (No emails sent in demo mode)",
        "campaign": campaign_data
    }

@app.get("/api/analytics")
async def get_analytics():
    return {
        "total_leads": len(MOCK_LEADS),
        "emails_sent": random.randint(100, 500),
        "sms_sent": random.randint(50, 200),
        "response_rate": round(random.uniform(0.15, 0.35), 2),
        "campaigns_active": len([c for c in MOCK_CAMPAIGNS if c["status"] == "running"]),
        "status_breakdown": {
            "new": len([l for l in MOCK_LEADS if l["status"] == "new"]),
            "contacted": len([l for l in MOCK_LEADS if l["status"] == "contacted"]),
            "responded": len([l for l in MOCK_LEADS if l["status"] == "responded"])
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
