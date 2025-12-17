"""
Updated FastAPI Backend with n8n Integration

This version routes all campaign operations through n8n workflows
instead of running them directly.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from mcp_airtable_connector import MCPAirtableConnector
from n8n_workflow_manager import N8nWorkflowManager
from campaign_orchestrator import CampaignOrchestrator
from personalization_engine import PersonalizationEngine
from n8n_integration import N8nIntegration  # New integration module

# Initialize FastAPI
app = FastAPI(
    title="Outreach Campaign Manager - n8n Powered",
    description="Automated outreach campaigns powered by n8n workflows",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
airtable = MCPAirtableConnector()
n8n_manager = N8nWorkflowManager()
n8n_integration = N8nIntegration()  # New n8n integration
orchestrator = CampaignOrchestrator()
personalizer = PersonalizationEngine()

# Pydantic models
class CampaignLaunch(BaseModel):
    campaign_name: str
    campaign_type: str
    template_id: str
    lead_ids: List[str]
    schedule_time: Optional[datetime] = None
    dry_run: bool = True

# Routes

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "app": "Outreach Campaign Manager",
        "version": "2.0.0",
        "powered_by": "n8n workflows",
        "status": "running"
    }

@app.get("/api/health")
async def health_check():
    """System health check."""
    try:
        health = orchestrator.health_check()
        return health
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Lead Management (unchanged)
@app.get("/api/leads")
async def get_leads(status: Optional[str] = None, industry: Optional[str] = None, limit: int = 100):
    """Get leads from Airtable."""
    try:
        leads = airtable.get_leads(status=status, max_records=limit)
        if industry:
            leads = [l for l in leads if l.get('fields', {}).get('Industry') == industry]
        return {"count": len(leads), "leads": leads}
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

# Campaign Management - NOW USING n8n

@app.post("/api/campaigns/launch")
async def launch_campaign(campaign: CampaignLaunch, background_tasks: BackgroundTasks):
    """Launch campaign via n8n workflow.

    This endpoint creates n8n-compatible JSON and triggers
    the appropriate n8n workflow instead of running locally.
    """
    try:
        # Create n8n payload
        campaign_data = {
            "campaign_name": campaign.campaign_name,
            "campaign_type": campaign.campaign_type,
            "template_id": campaign.template_id,
            "lead_ids": campaign.lead_ids,
            "schedule_time": campaign.schedule_time.isoformat() if campaign.schedule_time else None,
            "dry_run": campaign.dry_run
        }

        # Trigger appropriate n8n workflow
        if campaign.campaign_type == "email":
            result = n8n_integration.trigger_email_campaign(campaign_data)
        elif campaign.campaign_type == "sms":
            result = n8n_integration.trigger_sms_campaign(campaign_data)
        elif campaign.campaign_type == "both":
            result = n8n_integration.trigger_full_campaign(campaign_data)
        else:
            raise HTTPException(status_code=400, detail="Invalid campaign type")

        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Workflow trigger failed"))

        return {
            "status": "launched",
            "campaign_id": campaign.campaign_name,
            "campaign_type": campaign.campaign_type,
            "lead_count": len(campaign.lead_ids),
            "dry_run": campaign.dry_run,
            "n8n_execution_id": result.get("execution_id"),
            "n8n_status": result.get("status"),
            "message": "Campaign launched via n8n workflow"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/campaigns")
async def get_campaigns():
    """Get all campaigns (n8n executions)."""
    try:
        executions = n8n_manager.get_executions(limit=50)
        campaigns = []
        for execution in executions:
            campaigns.append({
                "id": execution.get("id"),
                "name": execution.get("workflowData", {}).get("name"),
                "status": execution.get("status"),
                "started_at": execution.get("startedAt"),
                "finished_at": execution.get("stoppedAt"),
                "mode": execution.get("mode"),
                "source": "n8n_workflow"
            })
        return {"campaigns": campaigns, "total": len(campaigns)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/campaigns/{campaign_id}")
async def get_campaign(campaign_id: str):
    """Get campaign details from n8n execution."""
    try:
        # Try to get from n8n
        execution = n8n_integration.get_execution_status(campaign_id)

        if execution.get("error"):
            # Fallback to n8n_manager
            execution = n8n_manager.get_execution(campaign_id)

        return execution
    except Exception as e:
        raise HTTPException(status_code=404, detail="Campaign not found")

@app.post("/api/campaigns/{campaign_id}/status")
async def update_campaign_status(campaign_id: str, status_data: Dict):
    """Webhook endpoint for n8n to update campaign status.

    n8n workflows call this endpoint to report progress.
    """
    try:
        # Store status update (could save to database)
        return n8n_integration.create_webhook_response(
            success=True,
            data={"campaign_id": campaign_id, "status_updated": True}
        )
    except Exception as e:
        return n8n_integration.create_webhook_response(
            success=False,
            error=str(e)
        )

# Lead Enrichment via n8n

@app.post("/api/leads/enrich")
async def enrich_leads(lead_ids: List[str]):
    """Trigger lead enrichment via n8n workflow."""
    try:
        result = n8n_integration.trigger_lead_enrichment(lead_ids)

        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))

        return {
            "status": "enrichment_started",
            "lead_count": len(lead_ids),
            "n8n_execution_id": result.get("execution_id"),
            "message": "Lead enrichment started via n8n"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# n8n Webhook Endpoints

@app.post("/api/webhooks/campaign-complete")
async def webhook_campaign_complete(data: Dict):
    """Webhook for n8n to report campaign completion."""
    try:
        campaign_id = data.get("campaign_id")
        status = data.get("status")
        results = data.get("results", {})

        # Process completion (update database, send notifications, etc.)

        return n8n_integration.create_webhook_response(
            success=True,
            data={
                "campaign_id": campaign_id,
                "processed": True,
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        return n8n_integration.create_webhook_response(
            success=False,
            error=str(e)
        )

@app.post("/api/webhooks/lead-updated")
async def webhook_lead_updated(data: Dict):
    """Webhook for n8n to report lead updates."""
    try:
        lead_id = data.get("lead_id")
        updates = data.get("updates", {})

        # Process lead update

        return n8n_integration.create_webhook_response(
            success=True,
            data={"lead_id": lead_id, "updated": True}
        )
    except Exception as e:
        return n8n_integration.create_webhook_response(
            success=False,
            error=str(e)
        )

# Export n8n JSON Schemas

@app.get("/api/n8n/schemas")
async def get_n8n_schemas():
    """Get all n8n-compatible JSON schemas."""
    from n8n_integration import (
        LEAD_ENRICHMENT_SCHEMA,
        EMAIL_CAMPAIGN_SCHEMA,
        WEBHOOK_RESPONSE_SCHEMA
    )

    return {
        "lead_enrichment": LEAD_ENRICHMENT_SCHEMA,
        "email_campaign": EMAIL_CAMPAIGN_SCHEMA,
        "webhook_response": WEBHOOK_RESPONSE_SCHEMA
    }

@app.get("/api/n8n/example-payload")
async def get_example_payload(workflow_type: str = "email_campaign"):
    """Get example n8n payload for testing."""
    examples = {
        "email_campaign": {
            "metadata": {
                "source": "web_app",
                "timestamp": "2025-12-17T10:00:00Z",
                "campaign_id": "test-campaign-001",
                "version": "1.0"
            },
            "campaign": {
                "name": "Test Email Campaign",
                "type": "email",
                "template_id": "email_v1_discovery",
                "dry_run": True,
                "schedule_time": None
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
                "retry_on_failure": True,
                "notification_webhook": "https://example.com/webhook/campaign-status"
            }
        },
        "lead_enrichment": {
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
                "generate_ai_insight": True,
                "generate_pain_point": True,
                "update_airtable": True
            }
        }
    }

    return examples.get(workflow_type, {"error": "Unknown workflow type"})

# Analytics (unchanged)
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

# Templates (unchanged)
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

# Workflows
@app.get("/api/workflows")
async def get_workflows():
    """Get all n8n workflows."""
    try:
        workflows = n8n_manager.list_workflows()
        return {"workflows": workflows}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
