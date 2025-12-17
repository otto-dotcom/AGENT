"""
n8n Integration Module - Web App to n8n Bridge

This module transforms web app data into n8n-compatible JSON
and triggers n8n workflows via webhooks.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import requests
import os


class N8nIntegration:
    """Bridge between web app and n8n workflows."""

    def __init__(self, n8n_url: str = None, api_key: str = None):
        """Initialize n8n integration.

        Args:
            n8n_url: n8n instance URL
            api_key: n8n API key
        """
        self.n8n_url = n8n_url or os.getenv("N8N_API_URL", "https://fagiolinosssssss.app.n8n.cloud")
        self.api_key = api_key or os.getenv("N8N_API_KEY")
        self.webhook_base = f"{self.n8n_url}/webhook"

    def create_campaign_payload(self, campaign_data: Dict) -> Dict:
        """Transform campaign data to n8n JSON format.

        Args:
            campaign_data: Campaign data from web app

        Returns:
            n8n-compatible JSON payload
        """
        return {
            "metadata": {
                "source": "web_app",
                "timestamp": datetime.now().isoformat(),
                "campaign_id": campaign_data.get("campaign_name"),
                "version": "1.0"
            },
            "campaign": {
                "name": campaign_data.get("campaign_name"),
                "type": campaign_data.get("campaign_type"),
                "template_id": campaign_data.get("template_id"),
                "dry_run": campaign_data.get("dry_run", True),
                "schedule_time": campaign_data.get("schedule_time")
            },
            "leads": self._format_leads(campaign_data.get("lead_ids", [])),
            "settings": {
                "rate_limit": self._get_rate_limit(campaign_data.get("campaign_type")),
                "retry_on_failure": True,
                "notification_webhook": f"{self.webhook_base}/campaign-status"
            }
        }

    def _format_leads(self, lead_ids: List[str]) -> List[Dict]:
        """Format leads for n8n processing.

        Args:
            lead_ids: List of Airtable record IDs

        Returns:
            List of formatted lead objects
        """
        # In production, fetch full lead data from Airtable
        return [
            {
                "record_id": lead_id,
                "source": "airtable",
                "status": "pending"
            }
            for lead_id in lead_ids
        ]

    def _get_rate_limit(self, campaign_type: str) -> Dict:
        """Get rate limits based on campaign type.

        Args:
            campaign_type: Type of campaign (email, sms, both)

        Returns:
            Rate limit configuration
        """
        limits = {
            "email": {
                "max_per_minute": 1,
                "max_per_hour": 20,
                "max_per_day": 50,
                "delay_between_sends": 2
            },
            "sms": {
                "max_per_minute": 1,
                "max_per_hour": 15,
                "max_per_day": 30,
                "delay_between_sends": 3
            },
            "both": {
                "max_per_minute": 1,
                "max_per_hour": 15,
                "max_per_day": 30,
                "delay_between_sends": 3
            }
        }
        return limits.get(campaign_type, limits["email"])

    def trigger_workflow(self, workflow_name: str, payload: Dict) -> Dict:
        """Trigger an n8n workflow via webhook.

        Args:
            workflow_name: Name of the workflow
            payload: Data to send to workflow

        Returns:
            Workflow execution response
        """
        webhook_url = f"{self.webhook_base}/{workflow_name}"

        headers = {
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(webhook_url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()

            return {
                "success": True,
                "execution_id": response.json().get("executionId"),
                "status": response.json().get("status"),
                "data": response.json()
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "status": "failed"
            }

    def trigger_lead_enrichment(self, lead_ids: List[str]) -> Dict:
        """Trigger lead enrichment workflow.

        Args:
            lead_ids: List of lead IDs to enrich

        Returns:
            Execution result
        """
        payload = {
            "action": "enrich_leads",
            "leads": [
                {
                    "record_id": lead_id,
                    "source": "airtable"
                }
                for lead_id in lead_ids
            ],
            "enrichment_config": {
                "generate_ai_insight": True,
                "generate_pain_point": True,
                "update_airtable": True
            }
        }

        return self.trigger_workflow("lead-enrichment", payload)

    def trigger_email_campaign(self, campaign_data: Dict) -> Dict:
        """Trigger email campaign workflow.

        Args:
            campaign_data: Campaign configuration

        Returns:
            Execution result
        """
        payload = self.create_campaign_payload(campaign_data)
        payload["campaign_type"] = "email"

        return self.trigger_workflow("email-campaign", payload)

    def trigger_sms_campaign(self, campaign_data: Dict) -> Dict:
        """Trigger SMS campaign workflow.

        Args:
            campaign_data: Campaign configuration

        Returns:
            Execution result
        """
        payload = self.create_campaign_payload(campaign_data)
        payload["campaign_type"] = "sms"

        return self.trigger_workflow("sms-campaign", payload)

    def trigger_full_campaign(self, campaign_data: Dict) -> Dict:
        """Trigger full multi-channel campaign.

        Args:
            campaign_data: Campaign configuration

        Returns:
            Execution result
        """
        payload = self.create_campaign_payload(campaign_data)

        # Trigger email first
        email_result = self.trigger_workflow("email-campaign", payload)

        if not email_result.get("success"):
            return email_result

        # Then trigger SMS follow-up
        sms_result = self.trigger_workflow("sms-campaign", payload)

        return {
            "success": True,
            "email_execution": email_result,
            "sms_execution": sms_result
        }

    def get_execution_status(self, execution_id: str) -> Dict:
        """Get status of an n8n workflow execution.

        Args:
            execution_id: n8n execution ID

        Returns:
            Execution status and data
        """
        url = f"{self.n8n_url}/api/v1/executions/{execution_id}"

        headers = {
            "X-N8N-API-KEY": self.api_key,
            "Accept": "application/json"
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "error": str(e),
                "status": "unknown"
            }

    def create_webhook_response(self, success: bool, data: Any = None, error: str = None) -> Dict:
        """Create standardized webhook response for n8n.

        Args:
            success: Whether operation succeeded
            data: Response data
            error: Error message if failed

        Returns:
            Standardized response object
        """
        response = {
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "source": "web_app"
        }

        if success:
            response["data"] = data
        else:
            response["error"] = error

        return response


# Example n8n-compatible JSON schemas

LEAD_ENRICHMENT_SCHEMA = {
    "type": "object",
    "properties": {
        "action": {"type": "string", "enum": ["enrich_leads"]},
        "leads": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "record_id": {"type": "string"},
                    "company_name": {"type": "string"},
                    "industry": {"type": "string"},
                    "location": {"type": "string"},
                    "website": {"type": "string"}
                },
                "required": ["record_id"]
            }
        },
        "enrichment_config": {
            "type": "object",
            "properties": {
                "generate_ai_insight": {"type": "boolean"},
                "generate_pain_point": {"type": "boolean"},
                "update_airtable": {"type": "boolean"}
            }
        }
    },
    "required": ["action", "leads"]
}

EMAIL_CAMPAIGN_SCHEMA = {
    "type": "object",
    "properties": {
        "metadata": {
            "type": "object",
            "properties": {
                "source": {"type": "string"},
                "timestamp": {"type": "string"},
                "campaign_id": {"type": "string"},
                "version": {"type": "string"}
            }
        },
        "campaign": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "type": {"type": "string", "enum": ["email", "sms", "both"]},
                "template_id": {"type": "string"},
                "dry_run": {"type": "boolean"},
                "schedule_time": {"type": "string"}
            },
            "required": ["name", "type", "template_id"]
        },
        "leads": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "record_id": {"type": "string"},
                    "source": {"type": "string"},
                    "status": {"type": "string"}
                },
                "required": ["record_id"]
            }
        },
        "settings": {
            "type": "object",
            "properties": {
                "rate_limit": {"type": "object"},
                "retry_on_failure": {"type": "boolean"},
                "notification_webhook": {"type": "string"}
            }
        }
    },
    "required": ["metadata", "campaign", "leads"]
}

WEBHOOK_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "success": {"type": "boolean"},
        "timestamp": {"type": "string"},
        "source": {"type": "string"},
        "data": {"type": "object"},
        "error": {"type": "string"}
    },
    "required": ["success", "timestamp", "source"]
}


def format_for_n8n(data: Any, schema_type: str = "generic") -> Dict:
    """Format any data for n8n consumption.

    Args:
        data: Data to format
        schema_type: Type of schema to use

    Returns:
        n8n-compatible formatted data
    """
    return {
        "json": data,
        "binary": {},
        "pairedItem": {"item": 0}
    }


def create_n8n_output(items: List[Dict]) -> List[Dict]:
    """Create n8n output format with multiple items.

    Args:
        items: List of data items

    Returns:
        n8n-compatible output format
    """
    return [
        {
            "json": item,
            "binary": {},
            "pairedItem": {"item": i}
        }
        for i, item in enumerate(items)
    ]
