#!/usr/bin/env python3
"""
Supabase Integration for HELIOS
================================

Handles all interactions with Supabase for storing scraped solar leads.
"""

import os
import logging
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class SupabaseClient:
    """Client for interacting with Supabase"""

    def __init__(self, url: str = None, key: str = None, table_name: str = None):
        """
        Initialize Supabase client

        Args:
            url: Supabase project URL (from env if not provided)
            key: Supabase API key (from env if not provided)
            table_name: Table name (from env if not provided)
        """
        try:
            from supabase import create_client, Client
        except ImportError:
            raise ImportError("supabase not installed. Run: pip install supabase")

        self.url = url or os.getenv('SUPABASE_URL')
        self.key = key or os.getenv('SUPABASE_KEY')
        self.table_name = table_name or os.getenv('SUPABASE_TABLE_NAME', 'solar_leads')

        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")

        self.client: Client = create_client(self.url, self.key)

        logger.info(f"✓ Supabase client initialized: {self.table_name}")

    def create_lead(self, lead_data: Dict) -> Dict:
        """
        Create a single lead in Supabase

        Args:
            lead_data: Lead information dictionary

        Returns:
            Created record from Supabase
        """
        try:
            # Transform lead data to Supabase format
            supabase_data = self._transform_to_supabase(lead_data)

            # Insert record
            response = self.client.table(self.table_name).insert(supabase_data).execute()

            logger.info(f"✓ Created lead: {lead_data.get('company_name', 'Unknown')}")
            return response.data[0] if response.data else {}

        except Exception as e:
            logger.error(f"Failed to create lead in Supabase: {e}")
            raise

    def create_leads_batch(self, leads: List[Dict]) -> List[Dict]:
        """
        Create multiple leads in Supabase (batch operation)

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
            supabase_records = [self._transform_to_supabase(lead) for lead in leads]

            # Batch insert
            response = self.client.table(self.table_name).insert(supabase_records).execute()

            created_count = len(response.data) if response.data else 0
            logger.info(f"✅ Total leads created in Supabase: {created_count}")

            return response.data

        except Exception as e:
            logger.error(f"Failed to batch create leads: {e}")
            raise

    def _transform_to_supabase(self, lead: Dict) -> Dict:
        """
        Transform lead data to Supabase format

        Args:
            lead: Raw lead dictionary

        Returns:
            Supabase-formatted data
        """
        # Use snake_case for Supabase columns (PostgreSQL convention)
        return {
            'company_name': lead.get('company_name', ''),
            'address': lead.get('address', ''),
            'city': lead.get('city', ''),
            'region': lead.get('region', ''),
            'phone': lead.get('phone', ''),
            'email': lead.get('email', ''),
            'website': lead.get('website', ''),
            'source': lead.get('source', 'GSE.it'),
            'industry': lead.get('industry', 'Solar/Photovoltaic Installation'),
            'status': lead.get('status', 'new_lead'),
            'scraped_date': lead.get('scraped_date', datetime.now().isoformat()),
            'notes': lead.get('notes', ''),
            'contact_person': lead.get('contact_person', ''),
            'vat_number': lead.get('vat_number', ''),
            'pec': lead.get('pec', ''),
            'metadata': lead.get('metadata', {}),
        }

    def check_duplicate(self, company_name: str) -> Optional[Dict]:
        """
        Check if a company already exists in Supabase

        Args:
            company_name: Company name to check

        Returns:
            Existing record if found, None otherwise
        """
        try:
            response = self.client.table(self.table_name)\
                .select("*")\
                .eq('company_name', company_name)\
                .execute()

            if response.data:
                logger.debug(f"Duplicate found: {company_name}")
                return response.data[0]

            return None

        except Exception as e:
            logger.error(f"Failed to check duplicate: {e}")
            return None

    def update_lead(self, lead_id: int, updates: Dict) -> Dict:
        """
        Update an existing lead in Supabase

        Args:
            lead_id: Supabase record ID
            updates: Fields to update

        Returns:
            Updated record
        """
        try:
            supabase_updates = self._transform_to_supabase(updates)

            response = self.client.table(self.table_name)\
                .update(supabase_updates)\
                .eq('id', lead_id)\
                .execute()

            logger.info(f"✓ Updated lead: {lead_id}")
            return response.data[0] if response.data else {}

        except Exception as e:
            logger.error(f"Failed to update lead: {e}")
            raise

    def get_all_leads(self, filters: Dict = None) -> List[Dict]:
        """
        Retrieve all leads from Supabase

        Args:
            filters: Optional dictionary of column:value filters

        Returns:
            List of records
        """
        try:
            query = self.client.table(self.table_name).select("*")

            # Apply filters if provided
            if filters:
                for column, value in filters.items():
                    query = query.eq(column, value)

            response = query.execute()

            logger.info(f"✓ Retrieved {len(response.data)} leads from Supabase")
            return response.data

        except Exception as e:
            logger.error(f"Failed to retrieve leads: {e}")
            raise

    def create_or_update(self, lead: Dict) -> Dict:
        """
        Create a lead if it doesn't exist, update if it does (upsert)

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

    def delete_lead(self, lead_id: int) -> bool:
        """
        Delete a lead from Supabase

        Args:
            lead_id: Record ID to delete

        Returns:
            True if successful
        """
        try:
            self.client.table(self.table_name).delete().eq('id', lead_id).execute()
            logger.info(f"✓ Deleted lead: {lead_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete lead: {e}")
            return False
