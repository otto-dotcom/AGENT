"""
MCP-based Airtable Connector for Outreach Automation System

This module provides connectivity to Airtable via Model Context Protocol (MCP)
for managing leads, campaigns, and responses in the Kronos database.
"""

import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import requests


class MCPAirtableConnector:
    """Connect to Airtable via MCP for lead management."""

    def __init__(self, config_path: str = "config/mcp_config.json"):
        """Initialize the MCP Airtable connector.

        Args:
            config_path: Path to MCP configuration file
        """
        self.config = self._load_config(config_path)
        self.api_key = os.getenv("AIRTABLE_API_KEY")
        self.base_id = os.getenv("AIRTABLE_BASE_ID")
        self.base_url = f"https://api.airtable.com/v0/{self.base_id}"

        if not self.api_key or not self.base_id:
            raise ValueError("AIRTABLE_API_KEY and AIRTABLE_BASE_ID must be set in environment")

    def _load_config(self, config_path: str) -> Dict:
        """Load MCP configuration."""
        with open(config_path, 'r') as f:
            return json.load(f)

    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make authenticated request to Airtable API.

        Args:
            method: HTTP method (GET, POST, PATCH, DELETE)
            endpoint: API endpoint
            data: Request payload

        Returns:
            API response as dictionary
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        url = f"{self.base_url}/{endpoint}"

        if method == "GET":
            response = requests.get(url, headers=headers, params=data)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PATCH":
            response = requests.patch(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        response.raise_for_status()
        return response.json()

    def get_schema(self) -> Dict[str, Any]:
        """Retrieve and document the Airtable base schema.

        Returns:
            Schema information including tables and fields
        """
        schema = {
            "base_id": self.base_id,
            "base_name": self.config["airtable"]["base_name"],
            "tables": {},
            "retrieved_at": datetime.now().isoformat()
        }

        # Get table information
        for table_key, table_info in self.config["airtable"]["tables"].items():
            table_name = table_info["name"]

            # Fetch sample record to infer schema
            try:
                response = self._make_request("GET", table_name, {"maxRecords": 1})

                if response.get("records"):
                    sample_record = response["records"][0]
                    fields = sample_record.get("fields", {})

                    schema["tables"][table_name] = {
                        "description": table_info["description"],
                        "fields": {
                            field_name: {
                                "type": type(field_value).__name__,
                                "sample_value": str(field_value)[:100] if field_value else None
                            }
                            for field_name, field_value in fields.items()
                        }
                    }
            except Exception as e:
                schema["tables"][table_name] = {
                    "description": table_info["description"],
                    "error": str(e)
                }

        return schema

    def get_leads(self,
                  status: Optional[str] = None,
                  max_records: int = 100,
                  filter_formula: Optional[str] = None) -> List[Dict]:
        """Fetch leads from Airtable.

        Args:
            status: Filter by lead status
            max_records: Maximum number of records to return
            filter_formula: Custom Airtable filter formula

        Returns:
            List of lead records
        """
        table_name = self.config["airtable"]["tables"]["leads"]["name"]

        params = {"maxRecords": max_records}

        if status:
            params["filterByFormula"] = f"{{Status}}='{status}'"
        elif filter_formula:
            params["filterByFormula"] = filter_formula

        response = self._make_request("GET", table_name, params)
        return response.get("records", [])

    def update_lead(self, record_id: str, fields: Dict[str, Any]) -> Dict:
        """Update a lead record.

        Args:
            record_id: Airtable record ID
            fields: Fields to update

        Returns:
            Updated record
        """
        table_name = self.config["airtable"]["tables"]["leads"]["name"]

        data = {
            "records": [{
                "id": record_id,
                "fields": fields
            }]
        }

        response = self._make_request("PATCH", table_name, data)
        return response.get("records", [{}])[0]

    def create_lead(self, fields: Dict[str, Any]) -> Dict:
        """Create a new lead record.

        Args:
            fields: Lead data

        Returns:
            Created record
        """
        table_name = self.config["airtable"]["tables"]["leads"]["name"]

        data = {
            "records": [{
                "fields": fields
            }]
        }

        response = self._make_request("POST", table_name, data)
        return response.get("records", [{}])[0]

    def get_ready_for_outreach(self, limit: int = 50) -> List[Dict]:
        """Get leads ready for outreach.

        Args:
            limit: Maximum number of leads to return

        Returns:
            List of leads ready for outreach
        """
        return self.get_leads(
            status="Ready for Outreach",
            max_records=limit
        )

    def mark_enriched(self, record_id: str, enrichment_data: Dict[str, Any]) -> Dict:
        """Mark a lead as enriched with AI data.

        Args:
            record_id: Airtable record ID
            enrichment_data: Enrichment data to add

        Returns:
            Updated record
        """
        fields = {
            "Status": "Enriched",
            "Enriched Date": datetime.now().isoformat(),
            **enrichment_data
        }

        return self.update_lead(record_id, fields)

    def mark_email_sent(self, record_id: str, campaign_id: str) -> Dict:
        """Mark a lead as having received an email.

        Args:
            record_id: Airtable record ID
            campaign_id: Campaign identifier

        Returns:
            Updated record
        """
        fields = {
            "Status": "Email Sent",
            "Email Sent Date": datetime.now().isoformat(),
            "Campaign ID": campaign_id
        }

        return self.update_lead(record_id, fields)

    def mark_sms_sent(self, record_id: str, campaign_id: str) -> Dict:
        """Mark a lead as having received an SMS.

        Args:
            record_id: Airtable record ID
            campaign_id: Campaign identifier

        Returns:
            Updated record
        """
        fields = {
            "Status": "SMS Sent",
            "SMS Sent Date": datetime.now().isoformat(),
            "Campaign ID": campaign_id
        }

        return self.update_lead(record_id, fields)

    def record_response(self, record_id: str, response_type: str,
                       response_content: str, sentiment: str) -> Dict:
        """Record a lead's response.

        Args:
            record_id: Airtable record ID
            response_type: Type of response (email, sms, phone)
            response_content: The actual response text
            sentiment: Response sentiment (positive, negative, neutral)

        Returns:
            Updated record
        """
        fields = {
            "Status": "Responded",
            "Response Date": datetime.now().isoformat(),
            "Response Type": response_type,
            "Response Content": response_content,
            "Response Sentiment": sentiment
        }

        return self.update_lead(record_id, fields)

    def validate_data_quality(self) -> Dict[str, Any]:
        """Validate data quality in the leads table.

        Returns:
            Data quality report
        """
        leads = self.get_leads(max_records=1000)

        total_leads = len(leads)
        required_fields = ["Company Name", "Email", "Contact Person"]

        quality_report = {
            "total_leads": total_leads,
            "field_completeness": {},
            "quality_score": 0,
            "issues": []
        }

        field_counts = {field: 0 for field in required_fields}

        for lead in leads:
            fields = lead.get("fields", {})
            for field in required_fields:
                if fields.get(field):
                    field_counts[field] += 1

        for field, count in field_counts.items():
            completeness = (count / total_leads * 100) if total_leads > 0 else 0
            quality_report["field_completeness"][field] = {
                "count": count,
                "percentage": round(completeness, 2)
            }

            if completeness < 80:
                quality_report["issues"].append(
                    f"{field} is only {completeness:.1f}% complete"
                )

        # Calculate overall quality score
        avg_completeness = sum(
            data["percentage"]
            for data in quality_report["field_completeness"].values()
        ) / len(required_fields)

        quality_report["quality_score"] = round(avg_completeness, 2)

        return quality_report

    def export_schema_to_file(self, output_path: str = "docs/airtable_schema.json"):
        """Export schema documentation to file.

        Args:
            output_path: Path to save schema documentation
        """
        schema = self.get_schema()

        with open(output_path, 'w') as f:
            json.dump(schema, f, indent=2)

        print(f"✅ Schema exported to {output_path}")

        return schema


def main():
    """Command-line interface for Airtable connector."""
    import argparse

    parser = argparse.ArgumentParser(description="MCP Airtable Connector")
    parser.add_argument(
        "--document-schema",
        action="store_true",
        help="Document and export Airtable schema"
    )
    parser.add_argument(
        "--validate-data",
        action="store_true",
        help="Validate data quality"
    )
    parser.add_argument(
        "--export-leads",
        action="store_true",
        help="Export leads to JSON"
    )
    parser.add_argument(
        "--status",
        type=str,
        help="Filter leads by status"
    )

    args = parser.parse_args()

    connector = MCPAirtableConnector()

    if args.document_schema:
        schema = connector.export_schema_to_file()
        print("\n📊 Airtable Schema:")
        print(json.dumps(schema, indent=2))

    if args.validate_data:
        quality = connector.validate_data_quality()
        print("\n📈 Data Quality Report:")
        print(json.dumps(quality, indent=2))

    if args.export_leads:
        leads = connector.get_leads(status=args.status, max_records=1000)
        output_path = "exports/leads_export.json"
        os.makedirs("exports", exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(leads, f, indent=2)

        print(f"\n✅ Exported {len(leads)} leads to {output_path}")


if __name__ == "__main__":
    main()
