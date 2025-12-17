"""
Test Suite for Automated Outreach System

Run these tests to validate your setup before launching campaigns.
"""

import os
import sys
import json
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))


class OutreachSystemTester:
    """Test suite for outreach automation system."""

    def __init__(self):
        """Initialize tester."""
        self.results = {
            "passed": [],
            "failed": [],
            "warnings": []
        }

    def test_credentials(self) -> bool:
        """Test that all required credentials are set.

        Returns:
            True if all credentials present
        """
        print("\n🔐 Testing Credentials...")

        required_vars = [
            "AIRTABLE_API_KEY",
            "AIRTABLE_BASE_ID",
            "N8N_API_KEY",
            "OPENAI_API_KEY"
        ]

        optional_vars = [
            "TWILIO_ACCOUNT_SID",
            "TWILIO_AUTH_TOKEN",
            "MAILCHIMP_API_KEY"
        ]

        all_present = True

        for var in required_vars:
            if os.getenv(var):
                print(f"  ✅ {var} is set")
                self.results["passed"].append(f"Credential: {var}")
            else:
                print(f"  ❌ {var} is NOT set (REQUIRED)")
                self.results["failed"].append(f"Credential: {var} missing")
                all_present = False

        for var in optional_vars:
            if os.getenv(var):
                print(f"  ✅ {var} is set")
                self.results["passed"].append(f"Optional credential: {var}")
            else:
                print(f"  ⚠️  {var} is NOT set (optional)")
                self.results["warnings"].append(f"Optional credential: {var} not set")

        return all_present

    def test_airtable_connection(self) -> bool:
        """Test Airtable connectivity.

        Returns:
            True if connection successful
        """
        print("\n📊 Testing Airtable Connection...")

        try:
            from mcp_airtable_connector import MCPAirtableConnector

            connector = MCPAirtableConnector()

            # Try to validate data (light operation)
            quality = connector.validate_data_quality()

            if quality.get("total_leads", 0) > 0:
                print(f"  ✅ Connected! Found {quality['total_leads']} leads")
                print(f"  ✅ Data quality score: {quality['quality_score']}%")
                self.results["passed"].append("Airtable connection")
                return True
            else:
                print("  ⚠️  Connected but no leads found")
                self.results["warnings"].append("Airtable has no leads")
                return True

        except Exception as e:
            print(f"  ❌ Connection failed: {e}")
            self.results["failed"].append(f"Airtable connection: {e}")
            return False

    def test_n8n_connection(self) -> bool:
        """Test n8n connectivity.

        Returns:
            True if connection successful
        """
        print("\n🔄 Testing n8n Connection...")

        try:
            from n8n_workflow_manager import N8nWorkflowManager

            manager = N8nWorkflowManager()

            # Get health status
            health = manager.health_check()

            if health.get("status") == "healthy":
                print(f"  ✅ Connected! Found {health['total_workflows']} workflows")
                self.results["passed"].append("n8n connection")
                return True
            else:
                print(f"  ❌ Health check failed: {health.get('error')}")
                self.results["failed"].append("n8n health check failed")
                return False

        except Exception as e:
            print(f"  ❌ Connection failed: {e}")
            self.results["failed"].append(f"n8n connection: {e}")
            return False

    def test_personalization_engine(self) -> bool:
        """Test AI personalization.

        Returns:
            True if personalization works
        """
        print("\n🤖 Testing Personalization Engine...")

        try:
            from personalization_engine import PersonalizationEngine

            engine = PersonalizationEngine()

            # Test data
            test_lead = {
                "company_name": "Test Company GmbH",
                "contact_person": "Max Mustermann",
                "email": "max@testcompany.ch",
                "industry": "Technology",
                "location": "Zurich"
            }

            # Test email personalization
            email = engine.personalize_email("email_v1_discovery", test_lead)

            if email.get("subject") and email.get("body"):
                print("  ✅ Email personalization works")
                print(f"     Subject: {email['subject'][:50]}...")
                self.results["passed"].append("Email personalization")
            else:
                print("  ❌ Email personalization failed")
                self.results["failed"].append("Email personalization")
                return False

            # Test SMS personalization
            sms = engine.personalize_sms("sms_v1_direct", test_lead)

            if sms.get("message"):
                print("  ✅ SMS personalization works")
                print(f"     Message ({sms['character_count']} chars): {sms['message'][:50]}...")
                self.results["passed"].append("SMS personalization")
            else:
                print("  ❌ SMS personalization failed")
                self.results["failed"].append("SMS personalization")
                return False

            return True

        except Exception as e:
            print(f"  ❌ Personalization test failed: {e}")
            self.results["failed"].append(f"Personalization: {e}")
            return False

    def test_campaign_orchestrator(self) -> bool:
        """Test campaign orchestrator.

        Returns:
            True if orchestrator works
        """
        print("\n🎯 Testing Campaign Orchestrator...")

        try:
            from campaign_orchestrator import CampaignOrchestrator

            orchestrator = CampaignOrchestrator()

            # Run health check
            health = orchestrator.health_check()

            if health.get("overall_status") == "healthy":
                print("  ✅ Campaign orchestrator is healthy")
                print(f"     n8n: {health['components']['n8n']['status']}")
                print(f"     Airtable: {health['components']['airtable']['status']}")
                self.results["passed"].append("Campaign orchestrator")
                return True
            else:
                print("  ⚠️  Campaign orchestrator has issues")
                self.results["warnings"].append("Campaign orchestrator degraded")
                return True

        except Exception as e:
            print(f"  ❌ Orchestrator test failed: {e}")
            self.results["failed"].append(f"Campaign orchestrator: {e}")
            return False

    def test_templates(self) -> bool:
        """Test that templates are valid.

        Returns:
            True if templates are valid
        """
        print("\n📧 Testing Templates...")

        try:
            # Load email templates
            with open('../templates/email_templates.json', 'r') as f:
                email_templates = json.load(f)

            print(f"  ✅ Email templates loaded: {len(email_templates['templates'])} templates")
            self.results["passed"].append("Email templates")

            # Load SMS templates
            with open('../templates/sms_templates.json', 'r') as f:
                sms_templates = json.load(f)

            print(f"  ✅ SMS templates loaded: {len(sms_templates['templates'])} templates")
            self.results["passed"].append("SMS templates")

            # Validate SMS character limits
            for template in sms_templates['templates']:
                char_count = template.get('character_count', 0)
                if char_count > 160:
                    print(f"  ⚠️  Template {template['id']} exceeds 160 chars ({char_count})")
                    self.results["warnings"].append(
                        f"SMS template {template['id']} too long"
                    )

            return True

        except Exception as e:
            print(f"  ❌ Template test failed: {e}")
            self.results["failed"].append(f"Templates: {e}")
            return False

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and generate report.

        Returns:
            Test results summary
        """
        print("\n" + "="*60)
        print("🧪 AUTOMATED OUTREACH SYSTEM - TEST SUITE")
        print("="*60)

        # Run all tests
        self.test_credentials()
        self.test_airtable_connection()
        self.test_n8n_connection()
        self.test_personalization_engine()
        self.test_campaign_orchestrator()
        self.test_templates()

        # Generate summary
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)

        print(f"\n✅ Passed: {len(self.results['passed'])}")
        for test in self.results['passed']:
            print(f"   - {test}")

        if self.results['warnings']:
            print(f"\n⚠️  Warnings: {len(self.results['warnings'])}")
            for warning in self.results['warnings']:
                print(f"   - {warning}")

        if self.results['failed']:
            print(f"\n❌ Failed: {len(self.results['failed'])}")
            for failure in self.results['failed']:
                print(f"   - {failure}")

        # Overall status
        print("\n" + "="*60)
        if not self.results['failed']:
            print("✅ ALL TESTS PASSED!")
            print("\nYou're ready to launch campaigns!")
        elif len(self.results['failed']) < 3:
            print("⚠️  MOSTLY PASSING")
            print("\nFix the failed tests before launching.")
        else:
            print("❌ SYSTEM NOT READY")
            print("\nPlease fix the issues and run tests again.")

        return self.results


def main():
    """Run test suite."""
    tester = OutreachSystemTester()
    results = tester.run_all_tests()

    # Exit with error code if tests failed
    if results['failed']:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
