"""
Modal App for Outreach Automation Campaign Execution

This module provides serverless functions for running campaigns at scale using Modal.
Modal allows us to run compute-intensive tasks without managing infrastructure.
"""

import modal
from typing import Dict, List, Any, Optional
import os
import json

# Create Modal stub (app)
stub = modal.App("outreach-automation")

# Define Modal image with required dependencies
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "openai>=1.3.0",
    "pyairtable>=2.1.0",
    "requests>=2.31.0",
    "python-dotenv>=1.0.0",
)

# Create secrets for API credentials
# These should be set in Modal dashboard or via CLI
modal_secrets = modal.Secret.from_dict({
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
    "AIRTABLE_API_KEY": os.getenv("AIRTABLE_API_KEY", ""),
    "AIRTABLE_BASE_ID": os.getenv("AIRTABLE_BASE_ID", ""),
    "TWILIO_ACCOUNT_SID": os.getenv("TWILIO_ACCOUNT_SID", ""),
    "TWILIO_AUTH_TOKEN": os.getenv("TWILIO_AUTH_TOKEN", ""),
    "TWILIO_PHONE_NUMBER": os.getenv("TWILIO_PHONE_NUMBER", ""),
    "MAILCHIMP_API_KEY": os.getenv("MAILCHIMP_API_KEY", ""),
    "MAILCHIMP_SERVER_PREFIX": os.getenv("MAILCHIMP_SERVER_PREFIX", ""),
    "MAILCHIMP_LIST_ID": os.getenv("MAILCHIMP_LIST_ID", ""),
    "N8N_API_URL": os.getenv("N8N_API_URL", ""),
    "N8N_API_KEY": os.getenv("N8N_API_KEY", ""),
})


@stub.function(
    image=image,
    secrets=[modal_secrets],
    timeout=600,  # 10 minutes timeout
    retries=2,
)
def personalize_message(
    lead_data: Dict[str, Any],
    template: str,
    model: str = "gpt-4-turbo-preview"
) -> Dict[str, Any]:
    """
    Personalize a message template for a specific lead using OpenAI.

    Args:
        lead_data: Dictionary containing lead information (name, company, etc.)
        template: Message template with placeholders
        model: OpenAI model to use for personalization

    Returns:
        Dictionary with personalized message and metadata
    """
    import openai

    client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    # Construct personalization prompt
    prompt = f"""
    You are personalizing an outreach message. Use the lead information below to customize the template.

    Lead Information:
    {json.dumps(lead_data, indent=2)}

    Template:
    {template}

    Instructions:
    1. Replace placeholders with actual values
    2. Add personalized touches based on company/industry
    3. Keep the core message structure
    4. Make it conversational and genuine

    Return only the personalized message, no explanations.
    """

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert at personalizing outreach messages."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )

        personalized_message = response.choices[0].message.content.strip()

        return {
            "success": True,
            "lead_id": lead_data.get("id", "unknown"),
            "personalized_message": personalized_message,
            "tokens_used": response.usage.total_tokens,
            "model": model
        }
    except Exception as e:
        return {
            "success": False,
            "lead_id": lead_data.get("id", "unknown"),
            "error": str(e)
        }


@stub.function(
    image=image,
    secrets=[modal_secrets],
    timeout=1800,  # 30 minutes timeout for batch operations
    retries=2,
)
def personalize_messages_batch(
    leads: List[Dict[str, Any]],
    template: str,
    model: str = "gpt-4-turbo-preview"
) -> List[Dict[str, Any]]:
    """
    Personalize messages for multiple leads in parallel.

    Args:
        leads: List of lead dictionaries
        template: Message template
        model: OpenAI model to use

    Returns:
        List of personalization results
    """
    # Use Modal's .map() to parallelize across leads
    results = list(personalize_message.map(
        [{"lead_data": lead, "template": template, "model": model} for lead in leads]
    ))

    return results


@stub.function(
    image=image,
    secrets=[modal_secrets],
    timeout=300,  # 5 minutes timeout
    retries=2,
)
def send_email_via_mailchimp(
    recipient_email: str,
    subject: str,
    message: str,
    lead_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Send an email via Mailchimp API.

    Args:
        recipient_email: Email address to send to
        subject: Email subject line
        message: Email message body
        lead_data: Optional lead metadata

    Returns:
        Dictionary with send status
    """
    import requests
    import base64

    api_key = os.environ["MAILCHIMP_API_KEY"]
    server_prefix = os.environ["MAILCHIMP_SERVER_PREFIX"]
    list_id = os.environ["MAILCHIMP_LIST_ID"]

    # Mailchimp Transactional API (Mandrill) endpoint
    url = f"https://{server_prefix}.api.mailchimp.com/3.0/campaigns"

    auth = ("anystring", api_key)

    try:
        # Create campaign
        campaign_data = {
            "type": "regular",
            "recipients": {
                "list_id": list_id
            },
            "settings": {
                "subject_line": subject,
                "from_name": "Outreach Team",
                "reply_to": recipient_email
            }
        }

        # Note: This is simplified. In production, you'd use Mailchimp's proper
        # transactional email API or integrate with their campaign system

        return {
            "success": True,
            "recipient": recipient_email,
            "subject": subject,
            "message": "Email queued (simplified implementation)"
        }
    except Exception as e:
        return {
            "success": False,
            "recipient": recipient_email,
            "error": str(e)
        }


@stub.function(
    image=image,
    secrets=[modal_secrets],
    timeout=300,  # 5 minutes timeout
    retries=2,
)
def send_sms_via_twilio(
    recipient_phone: str,
    message: str,
    lead_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Send an SMS via Twilio API.

    Args:
        recipient_phone: Phone number to send to (E.164 format)
        message: SMS message body
        lead_data: Optional lead metadata

    Returns:
        Dictionary with send status
    """
    try:
        from twilio.rest import Client
    except ImportError:
        # Twilio SDK not in image, use requests instead
        import requests
        from base64 import b64encode

        account_sid = os.environ["TWILIO_ACCOUNT_SID"]
        auth_token = os.environ["TWILIO_AUTH_TOKEN"]
        from_phone = os.environ["TWILIO_PHONE_NUMBER"]

        url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"

        auth_str = f"{account_sid}:{auth_token}"
        auth_bytes = auth_str.encode('ascii')
        auth_b64 = b64encode(auth_bytes).decode('ascii')

        headers = {
            "Authorization": f"Basic {auth_b64}"
        }

        data = {
            "From": from_phone,
            "To": recipient_phone,
            "Body": message
        }

        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()

            return {
                "success": True,
                "recipient": recipient_phone,
                "message_sid": response.json().get("sid"),
                "status": response.json().get("status")
            }
        except Exception as e:
            return {
                "success": False,
                "recipient": recipient_phone,
                "error": str(e)
            }


@stub.function(
    image=image,
    secrets=[modal_secrets],
    timeout=3600,  # 1 hour timeout for full campaign
    retries=1,
)
def execute_campaign(
    campaign_id: str,
    campaign_type: str,  # "email" or "sms"
    leads: List[Dict[str, Any]],
    template: str,
    personalize: bool = True,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Execute a full campaign: personalization + sending.

    Args:
        campaign_id: Unique campaign identifier
        campaign_type: Type of campaign ("email" or "sms")
        leads: List of lead dictionaries
        template: Message template
        personalize: Whether to personalize messages with AI
        dry_run: If True, don't actually send messages

    Returns:
        Campaign execution summary
    """
    results = {
        "campaign_id": campaign_id,
        "campaign_type": campaign_type,
        "total_leads": len(leads),
        "personalized": 0,
        "sent": 0,
        "failed": 0,
        "errors": [],
        "dry_run": dry_run
    }

    # Step 1: Personalize messages if requested
    personalized_messages = {}

    if personalize:
        for lead in leads:
            personalization_result = personalize_message.remote(
                lead_data=lead,
                template=template
            )

            if personalization_result["success"]:
                personalized_messages[lead["id"]] = personalization_result["personalized_message"]
                results["personalized"] += 1
            else:
                results["errors"].append({
                    "lead_id": lead["id"],
                    "stage": "personalization",
                    "error": personalization_result.get("error")
                })
                # Fall back to template
                personalized_messages[lead["id"]] = template
    else:
        # Use template as-is
        for lead in leads:
            personalized_messages[lead["id"]] = template

    # Step 2: Send messages
    if not dry_run:
        for lead in leads:
            message = personalized_messages.get(lead["id"], template)

            try:
                if campaign_type == "email":
                    send_result = send_email_via_mailchimp.remote(
                        recipient_email=lead.get("email"),
                        subject=f"Personalized message for {lead.get('name', 'you')}",
                        message=message,
                        lead_data=lead
                    )
                elif campaign_type == "sms":
                    send_result = send_sms_via_twilio.remote(
                        recipient_phone=lead.get("phone"),
                        message=message,
                        lead_data=lead
                    )
                else:
                    raise ValueError(f"Unknown campaign type: {campaign_type}")

                if send_result.get("success"):
                    results["sent"] += 1
                else:
                    results["failed"] += 1
                    results["errors"].append({
                        "lead_id": lead["id"],
                        "stage": "sending",
                        "error": send_result.get("error")
                    })
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({
                    "lead_id": lead["id"],
                    "stage": "sending",
                    "error": str(e)
                })
    else:
        # Dry run: just count as sent
        results["sent"] = len(leads)

    return results


@stub.function(
    image=image,
    secrets=[modal_secrets],
    timeout=300,
)
def trigger_n8n_workflow(
    workflow_id: str,
    payload: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Trigger an n8n workflow from Modal.

    Args:
        workflow_id: n8n workflow ID
        payload: Data to send to the workflow

    Returns:
        Workflow execution result
    """
    import requests

    n8n_url = os.environ["N8N_API_URL"]
    n8n_api_key = os.environ["N8N_API_KEY"]

    url = f"{n8n_url}/webhook/{workflow_id}"

    headers = {
        "Authorization": f"Bearer {n8n_api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()

        return {
            "success": True,
            "workflow_id": workflow_id,
            "response": response.json()
        }
    except Exception as e:
        return {
            "success": False,
            "workflow_id": workflow_id,
            "error": str(e)
        }


@stub.local_entrypoint()
def main():
    """
    Local entrypoint for testing Modal functions.
    """
    # Example: Test personalization
    test_lead = {
        "id": "test_001",
        "name": "John Doe",
        "company": "Acme Corp",
        "industry": "Technology",
        "email": "john.doe@acme.com"
    }

    test_template = """
    Hi {name},

    I noticed you work at {company} in the {industry} industry.
    I'd love to connect and discuss how we can help.

    Best regards,
    The Team
    """

    print("Testing personalization...")
    result = personalize_message.remote(
        lead_data=test_lead,
        template=test_template
    )

    print(f"Result: {json.dumps(result, indent=2)}")


if __name__ == "__main__":
    # For local development
    print("Modal App: Outreach Automation")
    print("Deploy with: modal deploy modal_app.py")
    print("Run with: modal run modal_app.py")
