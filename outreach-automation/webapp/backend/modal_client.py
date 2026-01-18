"""
Modal Client for Outreach Automation Backend

This module provides a client interface for calling Modal functions from the FastAPI backend.
"""

from typing import Dict, List, Any, Optional
import modal
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ModalClient:
    """
    Client for interacting with Modal serverless functions.
    """

    def __init__(self):
        """Initialize Modal client and connect to deployed app."""
        # Set Modal credentials if provided
        if os.getenv("MODAL_TOKEN_ID") and os.getenv("MODAL_TOKEN_SECRET"):
            os.environ["MODAL_TOKEN_ID"] = os.getenv("MODAL_TOKEN_ID")
            os.environ["MODAL_TOKEN_SECRET"] = os.getenv("MODAL_TOKEN_SECRET")

        try:
            # Connect to the deployed Modal app
            self.app = modal.App.lookup("outreach-automation", create_if_missing=False)
            self.connected = True
        except Exception as e:
            print(f"Warning: Could not connect to Modal app: {e}")
            print("Modal functions will not be available. Deploy with: modal deploy modal_app.py")
            self.connected = False
            self.app = None

    def is_available(self) -> bool:
        """Check if Modal integration is available."""
        return self.connected and self.app is not None

    async def personalize_message(
        self,
        lead_data: Dict[str, Any],
        template: str,
        model: str = "gpt-4-turbo-preview"
    ) -> Dict[str, Any]:
        """
        Personalize a message for a single lead using Modal.

        Args:
            lead_data: Lead information dictionary
            template: Message template
            model: OpenAI model to use

        Returns:
            Personalization result
        """
        if not self.is_available():
            return {
                "success": False,
                "error": "Modal integration not available"
            }

        try:
            # Get the function from the deployed app
            personalize_fn = self.app.function_from_name("personalize_message")

            # Call the Modal function
            result = personalize_fn.remote(
                lead_data=lead_data,
                template=template,
                model=model
            )

            return result
        except Exception as e:
            return {
                "success": False,
                "error": f"Modal function call failed: {str(e)}"
            }

    async def personalize_messages_batch(
        self,
        leads: List[Dict[str, Any]],
        template: str,
        model: str = "gpt-4-turbo-preview"
    ) -> List[Dict[str, Any]]:
        """
        Personalize messages for multiple leads in parallel using Modal.

        Args:
            leads: List of lead dictionaries
            template: Message template
            model: OpenAI model to use

        Returns:
            List of personalization results
        """
        if not self.is_available():
            return [{
                "success": False,
                "error": "Modal integration not available"
            } for _ in leads]

        try:
            # Get the function from the deployed app
            personalize_batch_fn = self.app.function_from_name("personalize_messages_batch")

            # Call the Modal function
            results = personalize_batch_fn.remote(
                leads=leads,
                template=template,
                model=model
            )

            return results
        except Exception as e:
            return [{
                "success": False,
                "error": f"Modal batch function call failed: {str(e)}"
            } for _ in leads]

    async def execute_campaign(
        self,
        campaign_id: str,
        campaign_type: str,
        leads: List[Dict[str, Any]],
        template: str,
        personalize: bool = True,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Execute a full campaign on Modal (personalization + sending).

        Args:
            campaign_id: Unique campaign identifier
            campaign_type: "email" or "sms"
            leads: List of lead dictionaries
            template: Message template
            personalize: Whether to use AI personalization
            dry_run: If True, don't actually send messages

        Returns:
            Campaign execution summary
        """
        if not self.is_available():
            return {
                "success": False,
                "error": "Modal integration not available"
            }

        try:
            # Get the function from the deployed app
            execute_campaign_fn = self.app.function_from_name("execute_campaign")

            # Call the Modal function
            result = execute_campaign_fn.remote(
                campaign_id=campaign_id,
                campaign_type=campaign_type,
                leads=leads,
                template=template,
                personalize=personalize,
                dry_run=dry_run
            )

            return result
        except Exception as e:
            return {
                "success": False,
                "error": f"Modal campaign execution failed: {str(e)}"
            }

    async def send_email(
        self,
        recipient_email: str,
        subject: str,
        message: str,
        lead_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send an email via Modal.

        Args:
            recipient_email: Email address
            subject: Email subject
            message: Email message
            lead_data: Optional lead metadata

        Returns:
            Send result
        """
        if not self.is_available():
            return {
                "success": False,
                "error": "Modal integration not available"
            }

        try:
            send_email_fn = self.app.function_from_name("send_email_via_mailchimp")

            result = send_email_fn.remote(
                recipient_email=recipient_email,
                subject=subject,
                message=message,
                lead_data=lead_data
            )

            return result
        except Exception as e:
            return {
                "success": False,
                "error": f"Modal email send failed: {str(e)}"
            }

    async def send_sms(
        self,
        recipient_phone: str,
        message: str,
        lead_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send an SMS via Modal.

        Args:
            recipient_phone: Phone number (E.164 format)
            message: SMS message
            lead_data: Optional lead metadata

        Returns:
            Send result
        """
        if not self.is_available():
            return {
                "success": False,
                "error": "Modal integration not available"
            }

        try:
            send_sms_fn = self.app.function_from_name("send_sms_via_twilio")

            result = send_sms_fn.remote(
                recipient_phone=recipient_phone,
                message=message,
                lead_data=lead_data
            )

            return result
        except Exception as e:
            return {
                "success": False,
                "error": f"Modal SMS send failed: {str(e)}"
            }

    async def trigger_n8n_workflow(
        self,
        workflow_id: str,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Trigger an n8n workflow via Modal.

        Args:
            workflow_id: n8n workflow ID
            payload: Data to send to workflow

        Returns:
            Workflow execution result
        """
        if not self.is_available():
            return {
                "success": False,
                "error": "Modal integration not available"
            }

        try:
            trigger_fn = self.app.function_from_name("trigger_n8n_workflow")

            result = trigger_fn.remote(
                workflow_id=workflow_id,
                payload=payload
            )

            return result
        except Exception as e:
            return {
                "success": False,
                "error": f"Modal n8n trigger failed: {str(e)}"
            }


# Singleton instance
_modal_client = None


def get_modal_client() -> ModalClient:
    """
    Get or create the Modal client singleton.

    Returns:
        ModalClient instance
    """
    global _modal_client

    if _modal_client is None:
        _modal_client = ModalClient()

    return _modal_client
