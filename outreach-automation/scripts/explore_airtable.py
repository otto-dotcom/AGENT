"""
Interactive Airtable Database Explorer

This script helps you explore and document your Airtable database structure
interactively, perfect for understanding your data before launching campaigns.
"""

import json
import os
import sys
from typing import Dict, List, Any
import requests
from datetime import datetime


class AirtableExplorer:
    """Interactive explorer for Airtable databases."""

    def __init__(self, api_key: str = None, base_id: str = None):
        """Initialize the explorer.

        Args:
            api_key: Airtable API key (or set AIRTABLE_API_KEY env var)
            base_id: Airtable Base ID (or set AIRTABLE_BASE_ID env var)
        """
        self.api_key = api_key or os.getenv("AIRTABLE_API_KEY")
        self.base_id = base_id or os.getenv("AIRTABLE_BASE_ID")

        if not self.api_key:
            print("❌ AIRTABLE_API_KEY not found!")
            print("\n📝 How to get your API key:")
            print("1. Go to https://airtable.com/account")
            print("2. Scroll to 'API' section")
            print("3. Click 'Generate API key'")
            print("4. Copy the key")
            print("\nThen set it:")
            print("export AIRTABLE_API_KEY='your_key_here'")
            sys.exit(1)

        if not self.base_id:
            print("❌ AIRTABLE_BASE_ID not found!")
            print("\n📝 How to get your Base ID:")
            print("1. Go to https://airtable.com/api")
            print("2. Select your 'Kronos Switzerland' base")
            print("3. Look for the base ID in the URL (starts with 'app')")
            print("\nThen set it:")
            print("export AIRTABLE_BASE_ID='your_base_id_here'")
            sys.exit(1)

        self.base_url = f"https://api.airtable.com/v0/{self.base_id}"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def list_tables(self) -> List[str]:
        """List all tables in the base.

        Note: Airtable API doesn't provide a direct way to list tables.
        This method tries common table names or asks the user.

        Returns:
            List of table names
        """
        print("\n📋 Note: Airtable API doesn't list tables automatically.")
        print("I'll try to discover tables by checking your base metadata.\n")

        # Try to get base schema from meta API
        schema_url = f"https://api.airtable.com/v0/meta/bases/{self.base_id}/tables"

        try:
            response = requests.get(schema_url, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                tables = [table["name"] for table in data.get("tables", [])]
                return tables
            else:
                print(f"⚠️  Could not auto-discover tables: {response.status_code}")
                return self._ask_for_tables()
        except Exception as e:
            print(f"⚠️  Error discovering tables: {e}")
            return self._ask_for_tables()

    def _ask_for_tables(self) -> List[str]:
        """Ask user to input table names."""
        print("\n📝 Please enter your table names (common ones: Leads, Companies, Contacts)")
        print("Enter table names separated by commas:")
        tables_input = input("> ")

        return [table.strip() for table in tables_input.split(",") if table.strip()]

    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """Get schema information for a table.

        Args:
            table_name: Name of the table

        Returns:
            Schema information
        """
        print(f"\n🔍 Exploring table: {table_name}")

        try:
            # Fetch sample records to infer schema
            url = f"{self.base_url}/{table_name}"
            params = {"maxRecords": 10}

            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()

            data = response.json()
            records = data.get("records", [])

            if not records:
                return {
                    "table_name": table_name,
                    "record_count": 0,
                    "error": "No records found in table"
                }

            # Analyze records to infer schema
            all_fields = {}
            for record in records:
                fields = record.get("fields", {})
                for field_name, field_value in fields.items():
                    if field_name not in all_fields:
                        all_fields[field_name] = {
                            "type": type(field_value).__name__,
                            "sample_values": [],
                            "empty_count": 0,
                            "filled_count": 0
                        }

                    if field_value:
                        all_fields[field_name]["filled_count"] += 1
                        # Store up to 3 sample values
                        if len(all_fields[field_name]["sample_values"]) < 3:
                            sample = str(field_value)[:100]  # Limit sample length
                            all_fields[field_name]["sample_values"].append(sample)
                    else:
                        all_fields[field_name]["empty_count"] += 1

            # Calculate completeness percentage
            for field_name, field_info in all_fields.items():
                total = field_info["filled_count"] + field_info["empty_count"]
                field_info["completeness"] = round(
                    (field_info["filled_count"] / total * 100) if total > 0 else 0,
                    1
                )

            return {
                "table_name": table_name,
                "record_count": len(records),
                "total_records_estimate": data.get("offset") is not None,
                "fields": all_fields
            }

        except requests.exceptions.HTTPError as e:
            return {
                "table_name": table_name,
                "error": f"HTTP {e.response.status_code}: {e.response.text}"
            }
        except Exception as e:
            return {
                "table_name": table_name,
                "error": str(e)
            }

    def get_record_count(self, table_name: str) -> int:
        """Get total number of records in a table.

        Args:
            table_name: Name of the table

        Returns:
            Total record count
        """
        try:
            url = f"{self.base_url}/{table_name}"
            params = {"maxRecords": 1, "fields[]": ""}  # Minimal data

            all_records = 0
            offset = None

            # Paginate to count all records
            while True:
                if offset:
                    params["offset"] = offset

                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()

                data = response.json()
                all_records += len(data.get("records", []))

                offset = data.get("offset")
                if not offset:
                    break

            return all_records

        except Exception as e:
            print(f"⚠️  Could not count records: {e}")
            return 0

    def explore_database(self) -> Dict[str, Any]:
        """Comprehensive database exploration.

        Returns:
            Complete database structure
        """
        print("\n" + "="*60)
        print("🔍 AIRTABLE DATABASE EXPLORER")
        print("="*60)

        print(f"\n📦 Base ID: {self.base_id}")

        # Discover tables
        print("\n📋 Discovering tables...")
        tables = self.list_tables()

        if not tables:
            print("❌ No tables found!")
            return {}

        print(f"\n✅ Found {len(tables)} table(s):")
        for table in tables:
            print(f"   - {table}")

        # Explore each table
        database_schema = {
            "base_id": self.base_id,
            "explored_at": datetime.now().isoformat(),
            "tables": {}
        }

        for table in tables:
            schema = self.get_table_schema(table)
            database_schema["tables"][table] = schema

            # Print table summary
            if "error" in schema:
                print(f"\n❌ {table}: {schema['error']}")
            else:
                print(f"\n✅ {table}:")
                print(f"   Records sampled: {schema['record_count']}")
                print(f"   Fields found: {len(schema.get('fields', {}))}")

        return database_schema

    def print_detailed_report(self, schema: Dict[str, Any]):
        """Print a detailed human-readable report.

        Args:
            schema: Database schema
        """
        print("\n" + "="*60)
        print("📊 DETAILED DATABASE REPORT")
        print("="*60)

        for table_name, table_data in schema.get("tables", {}).items():
            print(f"\n{'='*60}")
            print(f"📋 TABLE: {table_name}")
            print(f"{'='*60}")

            if "error" in table_data:
                print(f"❌ Error: {table_data['error']}")
                continue

            print(f"\n📈 Records: {table_data['record_count']} (sampled)")
            print(f"📊 Fields: {len(table_data.get('fields', {}))}")

            fields = table_data.get("fields", {})
            if fields:
                print(f"\n{'Field Name':<30} {'Type':<15} {'Complete':<10} {'Sample Values'}")
                print("-" * 100)

                for field_name, field_info in fields.items():
                    completeness = field_info.get("completeness", 0)
                    field_type = field_info.get("type", "unknown")
                    sample = ", ".join(field_info.get("sample_values", [])[:2])

                    # Color code completeness
                    if completeness >= 80:
                        status = f"✅ {completeness}%"
                    elif completeness >= 50:
                        status = f"⚠️  {completeness}%"
                    else:
                        status = f"❌ {completeness}%"

                    print(f"{field_name:<30} {field_type:<15} {status:<10} {sample[:40]}")

    def identify_missing_fields(self, schema: Dict[str, Any]) -> List[str]:
        """Identify fields needed for outreach campaigns.

        Args:
            schema: Database schema

        Returns:
            List of missing or incomplete fields
        """
        required_fields = {
            "Company Name": "Business name",
            "Contact Person": "Primary contact",
            "Email": "Email address for outreach",
            "Phone Number": "Phone for SMS",
            "Industry": "Business category",
            "Location": "Geographic location",
            "Status": "Lead status tracking"
        }

        print("\n" + "="*60)
        print("✅ OUTREACH READINESS CHECK")
        print("="*60)

        issues = []

        for table_name, table_data in schema.get("tables", {}).items():
            if "error" in table_data:
                continue

            fields = table_data.get("fields", {})

            print(f"\n📋 Checking table: {table_name}")

            for req_field, description in required_fields.items():
                if req_field in fields:
                    completeness = fields[req_field].get("completeness", 0)
                    if completeness >= 80:
                        print(f"   ✅ {req_field}: {completeness}% complete")
                    elif completeness >= 50:
                        print(f"   ⚠️  {req_field}: {completeness}% complete (needs improvement)")
                        issues.append(f"{table_name}.{req_field} only {completeness}% complete")
                    else:
                        print(f"   ❌ {req_field}: {completeness}% complete (critical)")
                        issues.append(f"{table_name}.{req_field} only {completeness}% complete")
                else:
                    print(f"   ❌ {req_field}: MISSING ({description})")
                    issues.append(f"{table_name}.{req_field} is missing")

        return issues

    def save_schema(self, schema: Dict[str, Any], output_path: str = "../docs/airtable_schema.json"):
        """Save schema to JSON file.

        Args:
            schema: Database schema
            output_path: Path to save file
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(schema, f, indent=2)

        print(f"\n💾 Schema saved to: {output_path}")


def main():
    """Main interactive explorer."""
    print("\n" + "="*60)
    print("🚀 AIRTABLE DATABASE EXPLORER")
    print("   for Automated Outreach System")
    print("="*60)

    # Check for credentials
    api_key = os.getenv("AIRTABLE_API_KEY")
    base_id = os.getenv("AIRTABLE_BASE_ID")

    if not api_key or not base_id:
        print("\n⚠️  Missing credentials!")
        print("\nQuick setup:")
        print("1. Get your Airtable API key: https://airtable.com/account")
        print("2. Get your Base ID: https://airtable.com/api (select your base)")
        print("\n3. Set environment variables:")
        print("   export AIRTABLE_API_KEY='your_key'")
        print("   export AIRTABLE_BASE_ID='your_base_id'")
        print("\nOr create a .env file:")
        print("   echo 'AIRTABLE_API_KEY=your_key' > .env")
        print("   echo 'AIRTABLE_BASE_ID=your_base_id' >> .env")
        return

    # Initialize explorer
    explorer = AirtableExplorer(api_key, base_id)

    # Explore database
    schema = explorer.explore_database()

    if not schema.get("tables"):
        print("\n❌ No tables found or error occurred")
        return

    # Print detailed report
    explorer.print_detailed_report(schema)

    # Check readiness for outreach
    issues = explorer.identify_missing_fields(schema)

    if issues:
        print(f"\n⚠️  Found {len(issues)} issue(s) to address:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print("\n✅ Database is ready for outreach campaigns!")

    # Save schema
    explorer.save_schema(schema)

    print("\n" + "="*60)
    print("✅ EXPLORATION COMPLETE")
    print("="*60)
    print("\nNext steps:")
    print("1. Review the schema in docs/airtable_schema.json")
    print("2. Address any missing or incomplete fields")
    print("3. Run the setup guide to configure campaigns")


if __name__ == "__main__":
    main()
