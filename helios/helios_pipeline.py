#!/usr/bin/env python3
"""
HELIOS - Solar Lead Scraping & Pipeline
========================================

Complete pipeline for scraping solar installer leads from GSE.it
and syncing them to Airtable and Supabase.

Usage:
    python helios_pipeline.py --target airtable
    python helios_pipeline.py --target supabase
    python helios_pipeline.py --target both
    python helios_pipeline.py --dry-run
"""

import os
import sys
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
from colorlog import ColoredFormatter

formatter = ColoredFormatter(
    "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
    datefmt=None,
    reset=True,
    log_colors={
        'DEBUG':    'cyan',
        'INFO':     'green',
        'WARNING':  'yellow',
        'ERROR':    'red',
        'CRITICAL': 'red,bg_white',
    }
)

handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class HeliosPipeline:
    """Main pipeline orchestrator"""

    def __init__(self, target: str = 'both', dry_run: bool = False):
        """
        Initialize pipeline

        Args:
            target: Where to sync leads ('airtable', 'supabase', or 'both')
            dry_run: If True, scrape but don't sync to databases
        """
        self.target = target
        self.dry_run = dry_run
        self.stats = {
            'scraped': 0,
            'synced_airtable': 0,
            'synced_supabase': 0,
            'errors': 0,
            'duplicates': 0,
        }

        # Load environment variables
        self._load_env()

        # Initialize clients
        self.airtable_client = None
        self.supabase_client = None

        if target in ['airtable', 'both'] and not dry_run:
            self._init_airtable()

        if target in ['supabase', 'both'] and not dry_run:
            self._init_supabase()

    def _load_env(self):
        """Load environment variables from .env file"""
        try:
            from dotenv import load_dotenv

            env_path = Path(__file__).parent / '.env'
            if env_path.exists():
                load_dotenv(env_path)
                logger.info("✓ Environment variables loaded")
            else:
                logger.warning(f".env file not found at {env_path}")
                logger.info("Using environment variables from system")

        except ImportError:
            logger.warning("python-dotenv not installed. Using system environment variables")

    def _init_airtable(self):
        """Initialize Airtable client"""
        try:
            from integrations.airtable_client import AirtableClient

            self.airtable_client = AirtableClient()
            logger.info("✓ Airtable client ready")

        except Exception as e:
            logger.error(f"Failed to initialize Airtable: {e}")
            if not self.dry_run:
                logger.error("Set AIRTABLE_API_KEY and AIRTABLE_BASE_ID in .env file")

    def _init_supabase(self):
        """Initialize Supabase client"""
        try:
            from integrations.supabase_client import SupabaseClient

            self.supabase_client = SupabaseClient()
            logger.info("✓ Supabase client ready")

        except Exception as e:
            logger.error(f"Failed to initialize Supabase: {e}")
            if not self.dry_run:
                logger.error("Set SUPABASE_URL and SUPABASE_KEY in .env file")

    def scrape_leads(self) -> List[Dict]:
        """
        Scrape leads from GSE.it

        Returns:
            List of lead dictionaries
        """
        logger.info("🔍 Starting web scraping...")

        try:
            from scrapers.gse_scraper import GSEScraper

            scraper = GSEScraper(headless=True)
            leads = scraper.scrape()

            self.stats['scraped'] = len(leads)
            logger.info(f"✅ Scraped {len(leads)} leads from GSE.it")

            return leads

        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            self.stats['errors'] += 1
            return []

    def sync_to_airtable(self, leads: List[Dict]) -> int:
        """
        Sync leads to Airtable

        Args:
            leads: List of lead dictionaries

        Returns:
            Number of leads synced
        """
        if not self.airtable_client:
            logger.warning("Airtable client not initialized")
            return 0

        logger.info("📤 Syncing to Airtable...")

        synced = 0
        duplicates = 0

        try:
            for lead in leads:
                try:
                    # Check for duplicates
                    existing = self.airtable_client.check_duplicate(
                        lead.get('company_name', '')
                    )

                    if existing:
                        logger.debug(f"Skipping duplicate: {lead.get('company_name')}")
                        duplicates += 1
                        continue

                    # Create new lead
                    self.airtable_client.create_lead(lead)
                    synced += 1

                except Exception as e:
                    logger.error(f"Failed to sync lead to Airtable: {e}")
                    self.stats['errors'] += 1

            self.stats['synced_airtable'] = synced
            self.stats['duplicates'] += duplicates

            logger.info(f"✅ Synced {synced} leads to Airtable ({duplicates} duplicates skipped)")

        except Exception as e:
            logger.error(f"Airtable sync failed: {e}")
            self.stats['errors'] += 1

        return synced

    def sync_to_supabase(self, leads: List[Dict]) -> int:
        """
        Sync leads to Supabase

        Args:
            leads: List of lead dictionaries

        Returns:
            Number of leads synced
        """
        if not self.supabase_client:
            logger.warning("Supabase client not initialized")
            return 0

        logger.info("📤 Syncing to Supabase...")

        synced = 0
        duplicates = 0

        try:
            for lead in leads:
                try:
                    # Check for duplicates
                    existing = self.supabase_client.check_duplicate(
                        lead.get('company_name', '')
                    )

                    if existing:
                        logger.debug(f"Skipping duplicate: {lead.get('company_name')}")
                        duplicates += 1
                        continue

                    # Create new lead
                    self.supabase_client.create_lead(lead)
                    synced += 1

                except Exception as e:
                    logger.error(f"Failed to sync lead to Supabase: {e}")
                    self.stats['errors'] += 1

            self.stats['synced_supabase'] = synced
            self.stats['duplicates'] += duplicates

            logger.info(f"✅ Synced {synced} leads to Supabase ({duplicates} duplicates skipped)")

        except Exception as e:
            logger.error(f"Supabase sync failed: {e}")
            self.stats['errors'] += 1

        return synced

    def save_export(self, leads: List[Dict], format: str = 'json'):
        """
        Save leads to local export file

        Args:
            leads: List of lead dictionaries
            format: Export format ('json' or 'csv')
        """
        import json
        import csv

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        export_dir = Path(__file__).parent / 'exports'
        export_dir.mkdir(exist_ok=True)

        if format == 'json':
            filepath = export_dir / f'gse_leads_{timestamp}.json'
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({
                    'source': 'GSE.it',
                    'scraped_at': datetime.now().isoformat(),
                    'total_leads': len(leads),
                    'leads': leads
                }, f, indent=2, ensure_ascii=False)

        elif format == 'csv':
            filepath = export_dir / f'gse_leads_{timestamp}.csv'

            if leads:
                keys = set()
                for lead in leads:
                    keys.update(lead.keys())

                with open(filepath, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=sorted(keys))
                    writer.writeheader()
                    writer.writerows(leads)

        logger.info(f"💾 Saved export: {filepath}")
        return filepath

    def run(self) -> Dict:
        """
        Run the complete pipeline

        Returns:
            Statistics dictionary
        """
        logger.info("="*60)
        logger.info("🌞 HELIOS - Solar Lead Pipeline")
        logger.info("="*60)

        if self.dry_run:
            logger.info("🧪 DRY RUN MODE - No database sync will occur")

        # Step 1: Scrape leads
        leads = self.scrape_leads()

        if not leads:
            logger.warning("⚠️  No leads found. Pipeline stopped.")
            return self.stats

        # Step 2: Save local export
        self.save_export(leads, 'json')
        self.save_export(leads, 'csv')

        if self.dry_run:
            logger.info("🧪 Dry run complete. Leads saved locally.")
            return self.stats

        # Step 3: Sync to targets
        if self.target in ['airtable', 'both']:
            self.sync_to_airtable(leads)

        if self.target in ['supabase', 'both']:
            self.sync_to_supabase(leads)

        # Print summary
        self._print_summary()

        return self.stats

    def _print_summary(self):
        """Print pipeline execution summary"""
        logger.info("")
        logger.info("="*60)
        logger.info("📊 PIPELINE SUMMARY")
        logger.info("="*60)
        logger.info(f"Leads Scraped:        {self.stats['scraped']}")
        logger.info(f"Synced to Airtable:   {self.stats['synced_airtable']}")
        logger.info(f"Synced to Supabase:   {self.stats['synced_supabase']}")
        logger.info(f"Duplicates Skipped:   {self.stats['duplicates']}")
        logger.info(f"Errors:               {self.stats['errors']}")
        logger.info("="*60)

        if self.stats['errors'] > 0:
            logger.warning("⚠️  Pipeline completed with errors")
        else:
            logger.info("✅ Pipeline completed successfully")


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description='HELIOS - Solar Lead Scraping & Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape and sync to both Airtable and Supabase
  python helios_pipeline.py --target both

  # Sync to Airtable only
  python helios_pipeline.py --target airtable

  # Dry run (scrape only, no database sync)
  python helios_pipeline.py --dry-run

  # Increase verbosity
  python helios_pipeline.py --target both --verbose
        """
    )

    parser.add_argument(
        '--target',
        choices=['airtable', 'supabase', 'both'],
        default='both',
        help='Target database for syncing leads (default: both)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Scrape leads but do not sync to databases'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Run pipeline
    pipeline = HeliosPipeline(target=args.target, dry_run=args.dry_run)
    stats = pipeline.run()

    # Exit with error code if there were errors
    sys.exit(1 if stats['errors'] > 0 else 0)


if __name__ == '__main__':
    main()
