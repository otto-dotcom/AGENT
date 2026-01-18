"""
Outreach Campaign Manager - FastAPI Backend

A modern web application for managing automated outreach campaigns.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import asyncio
import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from mcp_airtable_connector import MCPAirtableConnector
from n8n_workflow_manager import N8nWorkflowManager
from campaign_orchestrator import CampaignOrchestrator
from personalization_engine import PersonalizationEngine
from modal_client import get_modal_client

# Initialize FastAPI
app = FastAPI(
    title="Outreach Campaign Manager",
    description="Automated email and SMS outreach campaigns powered by AI",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket manager for real-time updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

# Pydantic models
class LeadFilter(BaseModel):
    status: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    limit: int = 100

class CampaignLaunch(BaseModel):
    campaign_name: str
    campaign_type: str  # email, sms, both
    template_id: str
    lead_ids: List[str]
    schedule_time: Optional[datetime] = None
    dry_run: bool = True

class TemplateCreate(BaseModel):
    name: str
    type: str  # email or sms
    subject: Optional[str] = None
    body: str
    variables: List[str]

class ModalCampaignLaunch(BaseModel):
    campaign_id: str
    campaign_type: str  # email or sms
    template: str
    leads: List[Dict[str, Any]]
    personalize: bool = True
    dry_run: bool = True

class ModalPersonalizationRequest(BaseModel):
    lead_data: Dict[str, Any]
    template: str
    model: str = "gpt-4-turbo-preview"

# Initialize services
airtable = MCPAirtableConnector()
n8n = N8nWorkflowManager()
orchestrator = CampaignOrchestrator()
personalizer = PersonalizationEngine()
modal_client = get_modal_client()

# Routes

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "app": "Outreach Campaign Manager",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/api/health")
async def health_check():
    """System health check."""
    try:
        health = orchestrator.health_check()
        health["modal_available"] = modal_client.is_available()
        return health
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Modal Integration Endpoints

@app.get("/api/modal/status")
async def get_modal_status():
    """Check Modal integration status."""
    return {
        "available": modal_client.is_available(),
        "message": "Modal integration is active" if modal_client.is_available() else "Modal not connected. Deploy with: modal deploy modal_app.py"
    }

@app.post("/api/modal/personalize")
async def personalize_with_modal(request: ModalPersonalizationRequest):
    """Personalize a message using Modal's AI function."""
    try:
        result = await modal_client.personalize_message(
            lead_data=request.lead_data,
            template=request.template,
            model=request.model
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/modal/campaigns/launch")
async def launch_modal_campaign(
    campaign: ModalCampaignLaunch,
    background_tasks: BackgroundTasks
):
    """Launch a campaign using Modal serverless execution."""
    try:
        if not modal_client.is_available():
            raise HTTPException(
                status_code=503,
                detail="Modal integration not available. Please deploy Modal app first."
            )

        # Launch campaign on Modal in background
        background_tasks.add_task(
            run_modal_campaign_async,
            campaign.campaign_id,
            campaign.campaign_type,
            campaign.leads,
            campaign.template,
            campaign.personalize,
            campaign.dry_run
        )

        return {
            "status": "launching",
            "campaign_id": campaign.campaign_id,
            "campaign_type": campaign.campaign_type,
            "lead_count": len(campaign.leads),
            "personalize": campaign.personalize,
            "dry_run": campaign.dry_run,
            "execution_platform": "modal"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/modal/send-email")
async def send_email_modal(data: dict):
    """Send a single email via Modal."""
    try:
        result = await modal_client.send_email(
            recipient_email=data.get("email"),
            subject=data.get("subject"),
            message=data.get("message"),
            lead_data=data.get("lead_data")
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/modal/send-sms")
async def send_sms_modal(data: dict):
    """Send a single SMS via Modal."""
    try:
        result = await modal_client.send_sms(
            recipient_phone=data.get("phone"),
            message=data.get("message"),
            lead_data=data.get("lead_data")
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Lead Management

@app.get("/api/leads")
async def get_leads(
    status: Optional[str] = None,
    industry: Optional[str] = None,
    limit: int = 100
):
    """Get leads from Airtable."""
    try:
        leads = airtable.get_leads(status=status, max_records=limit)

        # Filter by industry if provided
        if industry:
            leads = [l for l in leads if l.get('fields', {}).get('Industry') == industry]

        return {
            "count": len(leads),
            "leads": leads
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/leads/{lead_id}")
async def get_lead(lead_id: str):
    """Get single lead details."""
    try:
        leads = airtable.get_leads(max_records=1000)
        lead = next((l for l in leads if l['id'] == lead_id), None)

        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")

        return lead
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/leads/stats")
async def get_lead_stats():
    """Get lead statistics."""
    try:
        analytics = orchestrator.get_campaign_analytics()
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Campaign Management

@app.post("/api/campaigns/launch")
async def launch_campaign(
    campaign: CampaignLaunch,
    background_tasks: BackgroundTasks
):
    """Launch a new campaign."""
    try:
        # Set dry run mode
        os.environ["DRY_RUN_MODE"] = "true" if campaign.dry_run else "false"

        # Launch campaign in background
        if campaign.schedule_time and campaign.schedule_time > datetime.now():
            # Schedule for later
            return {
                "status": "scheduled",
                "campaign_id": campaign.campaign_name,
                "scheduled_for": campaign.schedule_time.isoformat(),
                "lead_count": len(campaign.lead_ids)
            }
        else:
            # Launch immediately
            background_tasks.add_task(
                run_campaign_async,
                campaign.campaign_type,
                campaign.lead_ids,
                campaign.template_id
            )

            return {
                "status": "launching",
                "campaign_id": campaign.campaign_name,
                "campaign_type": campaign.campaign_type,
                "lead_count": len(campaign.lead_ids),
                "dry_run": campaign.dry_run
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/campaigns")
async def get_campaigns():
    """Get all campaigns."""
    try:
        # Get executions from n8n
        executions = n8n.get_executions(limit=50)

        campaigns = []
        for execution in executions:
            campaigns.append({
                "id": execution.get("id"),
                "name": execution.get("workflowData", {}).get("name"),
                "status": execution.get("status"),
                "started_at": execution.get("startedAt"),
                "finished_at": execution.get("stoppedAt")
            })

        return {"campaigns": campaigns}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/campaigns/{campaign_id}")
async def get_campaign(campaign_id: str):
    """Get campaign details."""
    try:
        execution = n8n.get_execution(campaign_id)
        return execution
    except Exception as e:
        raise HTTPException(status_code=404, detail="Campaign not found")

# Analytics

@app.get("/api/analytics/overview")
async def get_analytics_overview():
    """Get analytics overview."""
    try:
        analytics = orchestrator.get_campaign_analytics()
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/by-status")
async def get_analytics_by_status():
    """Get lead breakdown by status."""
    try:
        leads = airtable.get_leads(max_records=10000)

        status_counts = {}
        for lead in leads:
            status = lead.get('fields', {}).get('Status', 'Unknown')
            status_counts[status] = status_counts.get(status, 0) + 1

        return {"by_status": status_counts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/by-industry")
async def get_analytics_by_industry():
    """Get lead breakdown by industry."""
    try:
        leads = airtable.get_leads(max_records=10000)

        industry_counts = {}
        for lead in leads:
            industry = lead.get('fields', {}).get('Industry', 'Unknown')
            industry_counts[industry] = industry_counts.get(industry, 0) + 1

        return {"by_industry": industry_counts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Templates

@app.get("/api/templates/email")
async def get_email_templates():
    """Get all email templates."""
    try:
        with open('../templates/email_templates.json', 'r') as f:
            templates = json.load(f)
        return templates
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/templates/sms")
async def get_sms_templates():
    """Get all SMS templates."""
    try:
        with open('../templates/sms_templates.json', 'r') as f:
            templates = json.load(f)
        return templates
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/templates/preview")
async def preview_template(data: dict):
    """Preview a template with sample data."""
    try:
        template_id = data.get('template_id')
        template_type = data.get('type', 'email')
        sample_lead = data.get('lead_data', {})

        if template_type == 'email':
            result = personalizer.personalize_email(template_id, sample_lead, generate_ai_content=False)
        else:
            result = personalizer.personalize_sms(template_id, sample_lead)

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Workflows

@app.get("/api/workflows")
async def get_workflows():
    """Get all n8n workflows."""
    try:
        workflows = n8n.list_workflows()
        return {"workflows": workflows}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/workflows/{workflow_id}/stats")
async def get_workflow_stats(workflow_id: str):
    """Get workflow execution statistics."""
    try:
        stats = n8n.get_workflow_statistics(workflow_id, days=30)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket for real-time updates

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and send updates
            data = await websocket.receive_text()

            # Echo back for now, can add real-time campaign updates
            await websocket.send_json({
                "type": "pong",
                "timestamp": datetime.now().isoformat()
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Background task functions

async def run_campaign_async(campaign_type: str, lead_ids: List[str], template_id: str):
    """Run campaign asynchronously."""
    try:
        # Broadcast start
        await manager.broadcast({
            "type": "campaign_started",
            "campaign_type": campaign_type,
            "lead_count": len(lead_ids),
            "timestamp": datetime.now().isoformat()
        })

        # Run campaign based on type
        if campaign_type == "email":
            result = orchestrator.launch_email_campaign(limit=len(lead_ids))
        elif campaign_type == "sms":
            result = orchestrator.launch_sms_campaign(limit=len(lead_ids))
        elif campaign_type == "both":
            result = orchestrator.run_full_campaign_cycle()
        else:
            result = {"error": "Invalid campaign type"}

        # Broadcast completion
        await manager.broadcast({
            "type": "campaign_completed",
            "result": result,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        await manager.broadcast({
            "type": "campaign_error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })

async def run_modal_campaign_async(
    campaign_id: str,
    campaign_type: str,
    leads: List[Dict[str, Any]],
    template: str,
    personalize: bool,
    dry_run: bool
):
    """Run campaign on Modal asynchronously."""
    try:
        # Broadcast start
        await manager.broadcast({
            "type": "modal_campaign_started",
            "campaign_id": campaign_id,
            "campaign_type": campaign_type,
            "lead_count": len(leads),
            "timestamp": datetime.now().isoformat()
        })

        # Execute campaign on Modal
        result = await modal_client.execute_campaign(
            campaign_id=campaign_id,
            campaign_type=campaign_type,
            leads=leads,
            template=template,
            personalize=personalize,
            dry_run=dry_run
        )

        # Broadcast completion
        await manager.broadcast({
            "type": "modal_campaign_completed",
            "campaign_id": campaign_id,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        await manager.broadcast({
            "type": "modal_campaign_error",
            "campaign_id": campaign_id,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
