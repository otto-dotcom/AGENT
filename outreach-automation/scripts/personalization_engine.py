"""
AI Personalization Engine for Outreach Automation

This module uses OpenAI GPT to generate personalized message content
for email and SMS campaigns at scale.
"""

import json
import os
from typing import Dict, List, Optional, Any
import openai
from datetime import datetime


class PersonalizationEngine:
    """Generate personalized outreach messages using AI."""

    def __init__(self,
                 templates_path: str = "templates",
                 model: str = "gpt-4-turbo-preview"):
        """Initialize the personalization engine.

        Args:
            templates_path: Path to templates directory
            model: OpenAI model to use
        """
        self.templates_path = templates_path
        self.model = model

        # Set OpenAI API key
        openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            raise ValueError("OPENAI_API_KEY must be set in environment")

        # Load templates
        self.email_templates = self._load_json(f"{templates_path}/email_templates.json")
        self.sms_templates = self._load_json(f"{templates_path}/sms_templates.json")

    def _load_json(self, file_path: str) -> Dict:
        """Load JSON file."""
        with open(file_path, 'r') as f:
            return json.load(f)

    def generate_ai_insight(self, lead_data: Dict[str, Any]) -> str:
        """Generate AI-powered personalized insight about a business.

        Args:
            lead_data: Dictionary with lead information

        Returns:
            Personalized insight string
        """
        company_name = lead_data.get("company_name", "the company")
        industry = lead_data.get("industry", "this industry")
        location = lead_data.get("location", "the area")
        website = lead_data.get("website", "")

        prompt = f"""Generate a brief, personalized observation about a business for outreach purposes.

Business Details:
- Company: {company_name}
- Industry: {industry}
- Location: {location}
- Website: {website}

Generate ONE sentence (15-25 words) that shows you've done research about their business.
Focus on something specific and genuine - not generic praise.
Make it conversational and authentic.

Examples:
- "I noticed you're expanding your product line based on your recent Instagram posts"
- "Your website's approach to customer testimonials is really compelling"
- "Saw you recently updated your services section - looks like you're moving into new territory"

Generate the insight (just the sentence, nothing else):"""

        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a business research expert who creates personalized, genuine observations about companies for outreach purposes."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=50
            )

            insight = response.choices[0].message.content.strip()
            return insight

        except Exception as e:
            print(f"⚠️  AI insight generation failed: {e}")
            return f"noticed {company_name}'s presence in {location}'s {industry} sector"

    def generate_pain_point(self, industry: str) -> str:
        """Generate industry-specific pain point.

        Args:
            industry: Business industry/category

        Returns:
            Pain point description
        """
        prompt = f"""What is a common business challenge or pain point for companies in the {industry} industry?

Provide ONE specific, actionable pain point (10-15 words).
Make it concrete and relatable.

Examples:
- "finding qualified staff during peak season"
- "managing inventory costs while maintaining quality"
- "generating consistent leads online"

Generate the pain point (just the phrase, nothing else):"""

        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an industry analyst who identifies specific business pain points."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=30
            )

            pain_point = response.choices[0].message.content.strip()
            return pain_point

        except Exception as e:
            print(f"⚠️  Pain point generation failed: {e}")
            return "scaling operations efficiently"

    def personalize_email(self,
                         template_id: str,
                         lead_data: Dict[str, Any],
                         generate_ai_content: bool = True) -> Dict[str, str]:
        """Generate personalized email from template.

        Args:
            template_id: Template identifier
            lead_data: Lead data for personalization
            generate_ai_content: Whether to generate AI insights

        Returns:
            Dictionary with subject and body
        """
        # Find template
        template = None
        for t in self.email_templates["templates"]:
            if t["id"] == template_id:
                template = t
                break

        if not template:
            raise ValueError(f"Template {template_id} not found")

        # Generate AI content if needed
        if generate_ai_content:
            if "ai_insight" not in lead_data or not lead_data["ai_insight"]:
                lead_data["ai_insight"] = self.generate_ai_insight(lead_data)

            if "pain_point" not in lead_data or not lead_data["pain_point"]:
                lead_data["pain_point"] = self.generate_pain_point(
                    lead_data.get("industry", "business")
                )

        # Prepare personalization variables
        first_name = lead_data.get("contact_person", "").split()[0] if lead_data.get("contact_person") else "there"
        variables = {
            "firstName": first_name,
            "companyName": lead_data.get("company_name", "your company"),
            "industry": lead_data.get("industry", "your industry"),
            "location": lead_data.get("location", "the area"),
            "canton": lead_data.get("canton", lead_data.get("location", "the canton")),
            "city": lead_data.get("city", lead_data.get("location", "the city")),
            "aiInsight": lead_data.get("ai_insight", "your business approach"),
            "painPoint": lead_data.get("pain_point", "growing your business"),
            "website": lead_data.get("website", ""),
            "recentNews": lead_data.get("recent_news", ""),
            "senderName": "Otto"
        }

        # Select subject line (first one for now, could randomize)
        subject_template = template["subject_lines"][0]

        # Replace variables in subject
        subject = subject_template
        for key, value in variables.items():
            subject = subject.replace(f"{{{{{key}}}}}", str(value))

        # Replace variables in body
        body = template["body"]
        for key, value in variables.items():
            body = body.replace(f"{{{{{key}}}}}", str(value))

        return {
            "subject": subject,
            "body": body,
            "template_id": template_id,
            "tone": template.get("tone", "professional")
        }

    def personalize_sms(self,
                       template_id: str,
                       lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personalized SMS from template.

        Args:
            template_id: Template identifier
            lead_data: Lead data for personalization

        Returns:
            Dictionary with message and metadata
        """
        # Find template
        template = None
        for t in self.sms_templates["templates"]:
            if t["id"] == template_id:
                template = t
                break

        if not template:
            raise ValueError(f"Template {template_id} not found")

        # Prepare personalization variables
        first_name = lead_data.get("contact_person", "").split()[0] if lead_data.get("contact_person") else "there"

        # Abbreviate company name if too long
        company_name = lead_data.get("company_name", "your company")
        if len(company_name) > 30:
            company_name = company_name[:27] + "..."

        variables = {
            "firstName": first_name,
            "companyName": company_name,
            "location": lead_data.get("location", "the area"),
            "industry": lead_data.get("industry", "your industry"),
            "senderName": "Otto"
        }

        # Replace variables in message
        message = template["body"]
        for key, value in variables.items():
            message = message.replace(f"{{{{{key}}}}}", str(value))

        # Verify character count
        char_count = len(message)
        if char_count > 160:
            print(f"⚠️  Warning: SMS is {char_count} characters (limit: 160)")

        return {
            "message": message,
            "character_count": char_count,
            "template_id": template_id,
            "tone": template.get("tone", "casual")
        }

    def batch_personalize_emails(self,
                                 leads: List[Dict[str, Any]],
                                 template_id: str) -> List[Dict[str, Any]]:
        """Generate personalized emails for multiple leads.

        Args:
            leads: List of lead data dictionaries
            template_id: Template to use

        Returns:
            List of personalized emails
        """
        results = []

        for i, lead in enumerate(leads):
            try:
                email = self.personalize_email(template_id, lead)
                results.append({
                    "record_id": lead.get("record_id"),
                    "email": lead.get("email"),
                    "subject": email["subject"],
                    "body": email["body"],
                    "template_id": template_id,
                    "generated_at": datetime.now().isoformat()
                })

                # Progress indicator
                if (i + 1) % 10 == 0:
                    print(f"✅ Personalized {i + 1}/{len(leads)} emails")

            except Exception as e:
                print(f"❌ Failed to personalize email for {lead.get('company_name')}: {e}")
                results.append({
                    "record_id": lead.get("record_id"),
                    "error": str(e)
                })

        return results

    def batch_personalize_sms(self,
                             leads: List[Dict[str, Any]],
                             template_id: str) -> List[Dict[str, Any]]:
        """Generate personalized SMS messages for multiple leads.

        Args:
            leads: List of lead data dictionaries
            template_id: Template to use

        Returns:
            List of personalized SMS messages
        """
        results = []

        for i, lead in enumerate(leads):
            try:
                sms = self.personalize_sms(template_id, lead)
                results.append({
                    "record_id": lead.get("record_id"),
                    "phone": lead.get("phone"),
                    "message": sms["message"],
                    "character_count": sms["character_count"],
                    "template_id": template_id,
                    "generated_at": datetime.now().isoformat()
                })

                # Progress indicator
                if (i + 1) % 10 == 0:
                    print(f"✅ Personalized {i + 1}/{len(leads)} SMS messages")

            except Exception as e:
                print(f"❌ Failed to personalize SMS for {lead.get('company_name')}: {e}")
                results.append({
                    "record_id": lead.get("record_id"),
                    "error": str(e)
                })

        return results

    def test_personalization(self, lead_data: Dict[str, Any]):
        """Test personalization with sample data.

        Args:
            lead_data: Sample lead data
        """
        print("\n" + "="*60)
        print("📧 EMAIL PERSONALIZATION TEST")
        print("="*60)

        for template in self.email_templates["templates"][:2]:  # Test first 2 templates
            try:
                email = self.personalize_email(template["id"], lead_data)
                print(f"\n📋 Template: {template['name']}")
                print(f"Subject: {email['subject']}")
                print(f"\nBody:\n{email['body']}")
                print("-" * 60)
            except Exception as e:
                print(f"❌ Error: {e}")

        print("\n" + "="*60)
        print("📱 SMS PERSONALIZATION TEST")
        print("="*60)

        for template in self.sms_templates["templates"][:2]:  # Test first 2 templates
            try:
                sms = self.personalize_sms(template["id"], lead_data)
                print(f"\n📋 Template: {template['name']}")
                print(f"Message ({sms['character_count']} chars):")
                print(sms['message'])
                print("-" * 60)
            except Exception as e:
                print(f"❌ Error: {e}")


def main():
    """Command-line interface for personalization engine."""
    import argparse

    parser = argparse.ArgumentParser(description="Personalization Engine")
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run personalization test"
    )
    parser.add_argument(
        "--generate-insight",
        action="store_true",
        help="Generate AI insight for a company"
    )
    parser.add_argument(
        "--company",
        type=str,
        help="Company name"
    )
    parser.add_argument(
        "--industry",
        type=str,
        help="Industry"
    )
    parser.add_argument(
        "--location",
        type=str,
        help="Location"
    )

    args = parser.parse_args()

    engine = PersonalizationEngine()

    if args.test:
        # Sample test data
        test_lead = {
            "company_name": "Alpine Bakery GmbH",
            "contact_person": "Hans Müller",
            "email": "hans@alpinebakery.ch",
            "phone": "+41791234567",
            "industry": "Food & Beverage",
            "location": "Zurich",
            "canton": "Zurich",
            "website": "https://alpinebakery.ch"
        }

        engine.test_personalization(test_lead)

    if args.generate_insight:
        if not args.company or not args.industry:
            print("❌ Please provide --company and --industry")
            return

        lead_data = {
            "company_name": args.company,
            "industry": args.industry,
            "location": args.location or "Switzerland"
        }

        print("\n🤖 Generating AI insights...")
        insight = engine.generate_ai_insight(lead_data)
        pain_point = engine.generate_pain_point(lead_data["industry"])

        print(f"\n✨ AI Insight: {insight}")
        print(f"💡 Pain Point: {pain_point}")


if __name__ == "__main__":
    main()
