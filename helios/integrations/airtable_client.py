#!/usr/bin/env python3
"""
Airtable Integration for HELIOS
================================

Handles all interactions with Airtable for storing scraped solar leads.
"""

import os
import logging
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class AirtableClient:
    """Client for interacting with Airtable"""

    def __init__(self, api_key: str = None, base_id: str = None, table_name: str = None):
        """
        Initialize Airtable client

        Args:
            api_key: Airtable API key (from env if not provided)
            base_id: Airtable base ID (from env if not provided)
            table_name: Table name (from env if not provided)
        """
        try:
            from pyairtable import Api
        except ImportError:
            raise ImportError("pyairtable not installed. Run: pip install pyairtable")

        self.api_key = api_key or os.getenv('AIRTABLE_API_KEY')
        self.base_id = base_id or os.getenv('AIRTABLE_BASE_ID')
        self.table_name = table_name or os.getenv('AIRTABLE_TABLE_NAME', 'Solar_Leads')

        if not self.api_key or not self.base_id:
            raise ValueError("AIRTABLE_API_KEY and AIRTABLE_BASE_ID must be set")

        self.api = Api(self.api_key)
        self.table = self.api.table(self.base_id, self.table_name)

        logger.info(f"✓ Airtable client initialized: {self.table_name}")

    def create_lead(self, lead_data: Dict) -> Dict:
        """
        Create a single lead in Airtable

        Args:
            lead_data: Lead information dictionary

        Returns:
            Created record from Airtable
        """
        try:
            # Transform lead data to Airtable format
            airtable_fields = self._transform_to_airtable(lead_data)

            # Create record
            record = self.table.create(airtable_fields)

            logger.info(f"✓ Created lead: {lead_data.get('company_name', 'Unknown')}")
            return record

        except Exception as e:
            logger.error(f"Failed to create lead in Airtable: {e}")
            raise

    def create_leads_batch(self, leads: List[Dict]) -> List[Dict]:
        """
        Create multiple leads in Airtable (batch operation)

        Args:
            leads: List of lead dictionaries

        Returns:
            List of created records
        """
        if not leads:
            logger.warning("No leads to create")
            return []

        try:
            # Transform all leads
            airtable_records = [self._transform_to_airtable(lead) for lead in leads]

            # Batch create (Airtable supports up to 10 records per batch)
            created_records = []
            batch_size = 10

            for i in range(0, len(airtable_records), batch_size):
                batch = airtable_records[i:i + batch_size]
                batch_result = self.table.batch_create(batch)
                created_records.extend(batch_result)

                logger.info(f"✓ Created batch {i//batch_size + 1}: {len(batch)} leads")

            logger.info(f"✅ Total leads created in Airtable: {len(created_records)}")
            return created_records

        except Exception as e:
            logger.error(f"Failed to batch create leads: {e}")
            raise

    def _transform_to_airtable(self, lead: Dict) -> Dict:
        """
        Transform lead data to Airtable field format

        Args:
            lead: Raw lead dictionary

        Returns:
            Airtable-formatted fields
        """
        # Map common fields to Airtable column names
        # Customize these field names based on your Airtable schema
        return {
            'Company Name': lead.get('company_name', ''),
            'Address': lead.get('address', ''),
            'City': lead.get('city', ''),
            'Region': lead.get('region', ''),
            'Phone': lead.get('phone', ''),
            'Email': lead.get('email', ''),
            'Website': lead.get('website', ''),
            'Source': lead.get('source', 'GSE.it'),
            'Industry': lead.get('industry', 'Solar/Photovoltaic Installation'),
            'Status': lead.get('status', 'New Lead'),
            'Scraped Date': lead.get('scraped_date', datetime.now().isoformat()),
            'Notes': lead.get('notes', ''),
            'Contact Person': lead.get('contact_person', ''),
            'VAT Number': lead.get('vat_number', ''),
            'PEC': lead.get('pec', ''),  # Italian certified email
        }

    def check_duplicate(self, company_name: str) -> Optional[Dict]:
        """
        Check if a company already exists in Airtable

        Args:
            company_name: Company name to check

        Returns:
            Existing record if found, None otherwise
        """
        try:
            formula = f"{{Company Name}} = '{company_name}'"
            records = self.table.all(formula=formula)

            if records:
                logger.debug(f"Duplicate found: {company_name}")
                return records[0]

            return None

        except Exception as e:
            logger.error(f"Failed to check duplicate: {e}")
            return None

    def update_lead(self, record_id: str, updates: Dict) -> Dict:
        """
        Update an existing lead in Airtable

        Args:
            record_id: Airtable record ID
            updates: Fields to update

        Returns:
            Updated record
        """
        try:
            airtable_updates = self._transform_to_airtable(updates)
            record = self.table.update(record_id, airtable_updates)

            logger.info(f"✓ Updated lead: {record_id}")
            return record

        except Exception as e:
            logger.error(f"Failed to update lead: {e}")
            raise

    def get_all_leads(self, formula: str = None) -> List[Dict]:
        """
        Retrieve all leads from Airtable

        Args:
            formula: Optional Airtable formula to filter records

        Returns:
            List of records
        """
        try:
            records = self.table.all(formula=formula) if formula else self.table.all()
            logger.info(f"✓ Retrieved {len(records)} leads from Airtable")
            return records

        except Exception as e:
            logger.error(f"Failed to retrieve leads: {e}")
            raise

    def create_or_update(self, lead: Dict) -> Dict:
        """
        Create a lead if it doesn't exist, update if it does

        Args:
            lead: Lead data

        Returns:
            Created or updated record
        """
        company_name = lead.get('company_name')
        if not company_name:
            raise ValueError("company_name is required")

        # Check for duplicate
        existing = self.check_duplicate(company_name)

        if existing:
            # Update existing record
            logger.info(f"Updating existing lead: {company_name}")
            return self.update_lead(existing['id'], lead)
        else:
            # Create new record
            return self.create_lead(lead)
