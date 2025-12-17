"""
Campaign Orchestrator for Outreach Automation System

This is the main controller that orchestrates the entire outreach campaign
by coordinating between Airtable (via MCP) and n8n workflows.
"""

import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

from mcp_airtable_connector import MCPAirtableConnector
from n8n_workflow_manager import N8nWorkflowManager


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CampaignOrchestrator:
    """Orchestrate automated outreach campaigns."""

    def __init__(self, config_path: str = "config/mcp_config.json"):
        """Initialize the campaign orchestrator.

        Args:
            config_path: Path to MCP configuration file
        """
        self.config_path = config_path
        self.airtable = MCPAirtableConnector(config_path)
        self.n8n = N8nWorkflowManager(config_path)
        self.dry_run = os.getenv("DRY_RUN_MODE", "true").lower() == "true"

        logger.info(f"🚀 Campaign Orchestrator initialized (Dry Run: {self.dry_run})")

    def run_full_campaign_cycle(self) -> Dict[str, Any]:
        """Execute a complete campaign cycle.

        This runs all stages: enrichment → email → SMS → follow-up

        Returns:
            Campaign execution report
        """
        logger.info("="*60)
        logger.info("🎯 Starting Full Campaign Cycle")
        logger.info("="*60)

        report = {
            "started_at": datetime.now().isoformat(),
            "dry_run": self.dry_run,
            "stages": {}
        }

        try:
            # Stage 1: Lead Enrichment
            logger.info("\n📊 Stage 1: Lead Enrichment")
            enrichment_result = self.enrich_leads()
            report["stages"]["enrichment"] = enrichment_result

            # Stage 2: Email Campaign
            logger.info("\n✉️  Stage 2: Email Campaign")
            email_result = self.launch_email_campaign()
            report["stages"]["email"] = email_result

            # Stage 3: SMS Campaign (for non-responders)
            logger.info("\n📱 Stage 3: SMS Campaign")
            sms_result = self.launch_sms_campaign()
            report["stages"]["sms"] = sms_result

            # Stage 4: Follow-up
            logger.info("\n🔄 Stage 4: Auto Follow-up")
            followup_result = self.run_followup()
            report["stages"]["followup"] = followup_result

            report["completed_at"] = datetime.now().isoformat()
            report["status"] = "success"

        except Exception as e:
            logger.error(f"❌ Campaign cycle failed: {e}")
            report["status"] = "failed"
            report["error"] = str(e)
            report["completed_at"] = datetime.now().isoformat()

        return report

    def enrich_leads(self, limit: int = 50) -> Dict[str, Any]:
        """Enrich leads with AI insights.

        Args:
            limit: Maximum number of leads to enrich

        Returns:
            Enrichment results
        """
        logger.info(f"Fetching up to {limit} leads ready for outreach...")

        # Get leads from Airtable
        leads = self.airtable.get_ready_for_outreach(limit=limit)

        logger.info(f"Found {len(leads)} leads ready for enrichment")

        if not leads:
            return {
                "status": "skipped",
                "reason": "No leads ready for outreach",
                "count": 0
            }

        # Prepare lead data for n8n workflow
        lead_data = [
            {
                "record_id": lead["id"],
                "company_name": lead["fields"].get("Company Name"),
                "contact_person": lead["fields"].get("Contact Person"),
                "email": lead["fields"].get("Email"),
                "industry": lead["fields"].get("Industry"),
                "location": lead["fields"].get("Location"),
                "website": lead["fields"].get("Website")
            }
            for lead in leads
        ]

        if self.dry_run:
            logger.info("🧪 DRY RUN: Would enrich {len(lead_data)} leads")
            return {
                "status": "dry_run",
                "count": len(lead_data),
                "sample": lead_data[:3]
            }

        # Execute enrichment workflow on n8n
        logger.info("Executing lead enrichment workflow on n8n...")
        execution = self.n8n.run_lead_enrichment(lead_data)

        return {
            "status": "executed",
            "execution_id": execution.get("id"),
            "count": len(lead_data),
            "workflow": "lead_enrichment"
        }

    def launch_email_campaign(self, limit: int = 50) -> Dict[str, Any]:
        """Launch email campaign for enriched leads.

        Args:
            limit: Maximum number of emails to send

        Returns:
            Campaign results
        """
        # Get enriched leads
        leads = self.airtable.get_leads(status="Enriched", max_records=limit)

        logger.info(f"Found {len(leads)} enriched leads for email campaign")

        if not leads:
            return {
                "status": "skipped",
                "reason": "No enriched leads available",
                "count": 0
            }

        campaign_data = {
            "campaign_id": f"email_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "leads": [
                {
                    "record_id": lead["id"],
                    "email": lead["fields"].get("Email"),
                    "first_name": lead["fields"].get("Contact Person", "").split()[0],
                    "company_name": lead["fields"].get("Company Name"),
                    "industry": lead["fields"].get("Industry"),
                    "location": lead["fields"].get("Location"),
                    "ai_insight": lead["fields"].get("AI Insight", "")
                }
                for lead in leads
            ]
        }

        if self.dry_run:
            logger.info(f"🧪 DRY RUN: Would send {len(leads)} emails")
            return {
                "status": "dry_run",
                "count": len(leads),
                "campaign_id": campaign_data["campaign_id"]
            }

        logger.info("Executing email campaign workflow on n8n...")
        execution = self.n8n.run_email_campaign(campaign_data)

        return {
            "status": "executed",
            "execution_id": execution.get("id"),
            "count": len(leads),
            "campaign_id": campaign_data["campaign_id"],
            "workflow": "email_campaign"
        }

    def launch_sms_campaign(self, limit: int = 30) -> Dict[str, Any]:
        """Launch SMS campaign for leads who received email.

        Args:
            limit: Maximum number of SMS to send

        Returns:
            Campaign results
        """
        # Get leads who received email but haven't responded
        # Filter for emails sent > 2 days ago
        filter_formula = "AND({Status}='Email Sent', DATETIME_DIFF(NOW(), {Email Sent Date}, 'days') > 2)"

        leads = self.airtable.get_leads(
            filter_formula=filter_formula,
            max_records=limit
        )

        logger.info(f"Found {len(leads)} leads for SMS follow-up")

        if not leads:
            return {
                "status": "skipped",
                "reason": "No leads ready for SMS follow-up",
                "count": 0
            }

        campaign_data = {
            "campaign_id": f"sms_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "leads": [
                {
                    "record_id": lead["id"],
                    "phone": lead["fields"].get("Phone Number"),
                    "first_name": lead["fields"].get("Contact Person", "").split()[0],
                    "company_name": lead["fields"].get("Company Name"),
                    "location": lead["fields"].get("Location")
                }
                for lead in leads
                if lead["fields"].get("Phone Number")  # Only leads with phone numbers
            ]
        }

        if not campaign_data["leads"]:
            return {
                "status": "skipped",
                "reason": "No leads have phone numbers",
                "count": 0
            }

        if self.dry_run:
            logger.info(f"🧪 DRY RUN: Would send {len(campaign_data['leads'])} SMS messages")
            return {
                "status": "dry_run",
                "count": len(campaign_data["leads"]),
                "campaign_id": campaign_data["campaign_id"]
            }

        logger.info("Executing SMS campaign workflow on n8n...")
        execution = self.n8n.run_sms_campaign(campaign_data)

        return {
            "status": "executed",
            "execution_id": execution.get("id"),
            "count": len(campaign_data["leads"]),
            "campaign_id": campaign_data["campaign_id"],
            "workflow": "sms_campaign"
        }

    def run_followup(self) -> Dict[str, Any]:
        """Run automated follow-up for non-responders.

        Returns:
            Follow-up results
        """
        # Get leads who haven't responded after 7 days
        filter_formula = "AND(OR({Status}='Email Sent', {Status}='SMS Sent'), DATETIME_DIFF(NOW(), {Email Sent Date}, 'days') > 7)"

        leads = self.airtable.get_leads(
            filter_formula=filter_formula,
            max_records=100
        )

        logger.info(f"Found {len(leads)} leads for follow-up")

        if not leads:
            return {
                "status": "skipped",
                "reason": "No leads need follow-up",
                "count": 0
            }

        if self.dry_run:
            logger.info(f"🧪 DRY RUN: Would follow up with {len(leads)} leads")
            return {
                "status": "dry_run",
                "count": len(leads)
            }

        logger.info("Executing auto follow-up workflow on n8n...")
        execution = self.n8n.run_auto_followup()

        return {
            "status": "executed",
            "execution_id": execution.get("id"),
            "count": len(leads),
            "workflow": "auto_followup"
        }

    def get_campaign_analytics(self) -> Dict[str, Any]:
        """Generate campaign analytics report.

        Returns:
            Analytics data
        """
        logger.info("Generating campaign analytics...")

        # Get all leads
        all_leads = self.airtable.get_leads(max_records=10000)

        analytics = {
            "generated_at": datetime.now().isoformat(),
            "total_leads": len(all_leads),
            "by_status": {},
            "conversion_metrics": {
                "email_sent": 0,
                "sms_sent": 0,
                "responded": 0,
                "meetings_booked": 0
            },
            "response_rate": 0,
            "meeting_conversion_rate": 0
        }

        # Count by status
        for lead in all_leads:
            status = lead["fields"].get("Status", "Unknown")
            analytics["by_status"][status] = analytics["by_status"].get(status, 0) + 1

            if status in ["Email Sent", "SMS Sent", "Responded", "Meeting Booked"]:
                if status in ["Email Sent", "SMS Sent", "Responded", "Meeting Booked"]:
                    analytics["conversion_metrics"]["email_sent"] += 1
                if status in ["SMS Sent", "Responded", "Meeting Booked"]:
                    analytics["conversion_metrics"]["sms_sent"] += 1
                if status in ["Responded", "Meeting Booked"]:
                    analytics["conversion_metrics"]["responded"] += 1
                if status == "Meeting Booked":
                    analytics["conversion_metrics"]["meetings_booked"] += 1

        # Calculate rates
        contacted = analytics["conversion_metrics"]["email_sent"]
        if contacted > 0:
            analytics["response_rate"] = round(
                (analytics["conversion_metrics"]["responded"] / contacted) * 100, 2
            )
            analytics["meeting_conversion_rate"] = round(
                (analytics["conversion_metrics"]["meetings_booked"] / contacted) * 100, 2
            )

        return analytics

    def health_check(self) -> Dict[str, Any]:
        """Check system health.

        Returns:
            Health status of all components
        """
        logger.info("Running system health check...")

        health = {
            "timestamp": datetime.now().isoformat(),
            "components": {}
        }

        # Check n8n
        try:
            n8n_health = self.n8n.health_check()
            health["components"]["n8n"] = n8n_health
        except Exception as e:
            health["components"]["n8n"] = {
                "status": "unhealthy",
                "error": str(e)
            }

        # Check Airtable
        try:
            quality = self.airtable.validate_data_quality()
            health["components"]["airtable"] = {
                "status": "healthy",
                "quality_score": quality["quality_score"]
            }
        except Exception as e:
            health["components"]["airtable"] = {
                "status": "unhealthy",
                "error": str(e)
            }

        # Overall status
        all_healthy = all(
            comp.get("status") == "healthy"
            for comp in health["components"].values()
        )
        health["overall_status"] = "healthy" if all_healthy else "degraded"

        return health


def main():
    """Command-line interface for campaign orchestrator."""
    import argparse

    parser = argparse.ArgumentParser(description="Campaign Orchestrator")
    parser.add_argument(
        "--full-cycle",
        action="store_true",
        help="Run full campaign cycle"
    )
    parser.add_argument(
        "--enrich",
        action="store_true",
        help="Run lead enrichment only"
    )
    parser.add_argument(
        "--email",
        action="store_true",
        help="Run email campaign only"
    )
    parser.add_argument(
        "--sms",
        action="store_true",
        help="Run SMS campaign only"
    )
    parser.add_argument(
        "--followup",
        action="store_true",
        help="Run follow-up only"
    )
    parser.add_argument(
        "--analytics",
        action="store_true",
        help="Generate analytics report"
    )
    parser.add_argument(
        "--health",
        action="store_true",
        help="Run health check"
    )

    args = parser.parse_args()

    orchestrator = CampaignOrchestrator()

    if args.full_cycle:
        report = orchestrator.run_full_campaign_cycle()
        print("\n" + "="*60)
        print("📊 CAMPAIGN CYCLE REPORT")
        print("="*60)
        print(json.dumps(report, indent=2))

    if args.enrich:
        result = orchestrator.enrich_leads()
        print("\n✅ Enrichment Result:")
        print(json.dumps(result, indent=2))

    if args.email:
        result = orchestrator.launch_email_campaign()
        print("\n✅ Email Campaign Result:")
        print(json.dumps(result, indent=2))

    if args.sms:
        result = orchestrator.launch_sms_campaign()
        print("\n✅ SMS Campaign Result:")
        print(json.dumps(result, indent=2))

    if args.followup:
        result = orchestrator.run_followup()
        print("\n✅ Follow-up Result:")
        print(json.dumps(result, indent=2))

    if args.analytics:
        analytics = orchestrator.get_campaign_analytics()
        print("\n📈 Campaign Analytics:")
        print(json.dumps(analytics, indent=2))

    if args.health:
        health = orchestrator.health_check()
        print("\n🏥 System Health:")
        print(json.dumps(health, indent=2))


if __name__ == "__main__":
    main()
