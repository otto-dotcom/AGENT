#!/usr/bin/env python3
"""
GSE Solar Installer Lead Scraper
=================================

Scrapes solar installer leads from GSE.it (Gestore dei Servizi Energetici)
Target URL: https://www.gse.it/servizi-per-te/fotovoltaico/reddito-energetico/mappa-realizzatori-impianti-fotovoltaici

Features:
- Handles JavaScript-rendered content using Selenium
- Exports to CSV and JSON formats
- Compatible with Airtable lead enrichment workflow
- Extracts: Company Name, Address, Contact Info, Region, etc.
"""

import json
import csv
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GSESolarScraper:
    """Scraper for GSE solar installer leads"""

    def __init__(self, headless: bool = True):
        """
        Initialize the scraper

        Args:
            headless: Run browser in headless mode (default: True)
        """
        self.url = "https://www.gse.it/servizi-per-te/fotovoltaico/reddito-energetico/mappa-realizzatori-impianti-fotovoltaici"
        self.headless = headless
        self.leads = []

    def setup_selenium(self):
        """Set up Selenium WebDriver with Chrome"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC

            # Set up Chrome options
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

            # Initialize driver
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 20)

            logger.info("✓ Selenium WebDriver initialized")
            return True

        except ImportError:
            logger.error("Selenium not installed. Install with: pip install selenium")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize Selenium: {e}")
            return False

    def scrape_with_selenium(self) -> List[Dict]:
        """
        Scrape leads using Selenium (handles JavaScript-rendered content)

        Returns:
            List of lead dictionaries
        """
        if not self.setup_selenium():
            return []

        try:
            logger.info(f"Loading page: {self.url}")
            self.driver.get(self.url)

            # Wait for page to load (adjust selector based on actual page structure)
            time.sleep(5)  # Initial wait for JavaScript to execute

            # Take a screenshot for debugging
            screenshot_path = Path(__file__).parent.parent / "debug_screenshot.png"
            self.driver.save_screenshot(str(screenshot_path))
            logger.info(f"Screenshot saved to: {screenshot_path}")

            # Get page source for analysis
            page_source = self.driver.page_source

            # Try to find the data - this will need to be customized based on actual page structure
            # Common patterns for installer data:
            leads = self._extract_leads_from_page(page_source)

            if not leads:
                logger.warning("No leads found. The page structure may have changed.")
                logger.info("Checking for common data containers...")

                # Try to find data in various formats
                leads = self._try_multiple_extraction_methods()

            logger.info(f"✓ Scraped {len(leads)} leads")
            return leads

        except Exception as e:
            logger.error(f"Error during scraping: {e}")
            return []
        finally:
            if hasattr(self, 'driver'):
                self.driver.quit()

    def _try_multiple_extraction_methods(self) -> List[Dict]:
        """Try different methods to extract lead data"""
        from selenium.webdriver.common.by import By

        leads = []

        # Method 1: Look for table rows
        try:
            tables = self.driver.find_elements(By.TAG_NAME, "table")
            logger.info(f"Found {len(tables)} tables")
            for table in tables:
                rows = table.find_elements(By.TAG_NAME, "tr")
                for row in rows[1:]:  # Skip header
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if cells:
                        lead = self._extract_from_table_row(cells)
                        if lead:
                            leads.append(lead)
        except Exception as e:
            logger.debug(f"Table extraction failed: {e}")

        # Method 2: Look for list items
        if not leads:
            try:
                list_items = self.driver.find_elements(By.CSS_SELECTOR, "ul li, ol li")
                logger.info(f"Found {len(list_items)} list items")
                for item in list_items:
                    lead = self._extract_from_list_item(item)
                    if lead:
                        leads.append(lead)
            except Exception as e:
                logger.debug(f"List extraction failed: {e}")

        # Method 3: Look for card/div containers
        if not leads:
            try:
                cards = self.driver.find_elements(By.CSS_SELECTOR, "div.card, div.installer, div.company")
                logger.info(f"Found {len(cards)} card elements")
                for card in cards:
                    lead = self._extract_from_card(card)
                    if lead:
                        leads.append(lead)
            except Exception as e:
                logger.debug(f"Card extraction failed: {e}")

        # Method 4: Check for JSON data in script tags
        if not leads:
            try:
                scripts = self.driver.find_elements(By.TAG_NAME, "script")
                for script in scripts:
                    content = script.get_attribute('innerHTML')
                    if content and ('installer' in content.lower() or 'company' in content.lower()):
                        extracted = self._extract_from_json_script(content)
                        if extracted:
                            leads.extend(extracted)
            except Exception as e:
                logger.debug(f"JSON extraction failed: {e}")

        return leads

    def _extract_from_table_row(self, cells) -> Optional[Dict]:
        """Extract lead data from table cells"""
        try:
            # Adapt this based on actual table structure
            if len(cells) >= 3:
                return {
                    'company_name': cells[0].text.strip(),
                    'address': cells[1].text.strip() if len(cells) > 1 else '',
                    'region': cells[2].text.strip() if len(cells) > 2 else '',
                    'phone': cells[3].text.strip() if len(cells) > 3 else '',
                    'email': cells[4].text.strip() if len(cells) > 4 else '',
                    'source': 'GSE.it',
                    'scraped_date': datetime.now().isoformat(),
                    'status': 'New Lead',
                    'industry': 'Solar/Photovoltaic Installation'
                }
        except Exception as e:
            logger.debug(f"Failed to extract from table row: {e}")
        return None

    def _extract_from_list_item(self, item) -> Optional[Dict]:
        """Extract lead data from list item"""
        try:
            text = item.text.strip()
            if len(text) > 10:  # Minimum content check
                # Try to parse structured text
                lines = text.split('\n')
                return {
                    'company_name': lines[0] if lines else text,
                    'address': lines[1] if len(lines) > 1 else '',
                    'source': 'GSE.it',
                    'scraped_date': datetime.now().isoformat(),
                    'status': 'New Lead',
                    'industry': 'Solar/Photovoltaic Installation'
                }
        except Exception as e:
            logger.debug(f"Failed to extract from list item: {e}")
        return None

    def _extract_from_card(self, card) -> Optional[Dict]:
        """Extract lead data from card/div element"""
        try:
            text = card.text.strip()
            if len(text) > 10:
                # Look for common patterns
                lines = [line.strip() for line in text.split('\n') if line.strip()]

                lead = {
                    'company_name': lines[0] if lines else '',
                    'source': 'GSE.it',
                    'scraped_date': datetime.now().isoformat(),
                    'status': 'New Lead',
                    'industry': 'Solar/Photovoltaic Installation'
                }

                # Try to find email and phone in text
                import re
                email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
                phone_match = re.search(r'[\+\d][\d\s\-\(\)]{8,}', text)

                if email_match:
                    lead['email'] = email_match.group()
                if phone_match:
                    lead['phone'] = phone_match.group()

                # Add remaining lines as notes
                if len(lines) > 1:
                    lead['notes'] = '\n'.join(lines[1:])

                return lead
        except Exception as e:
            logger.debug(f"Failed to extract from card: {e}")
        return None

    def _extract_from_json_script(self, script_content: str) -> List[Dict]:
        """Extract lead data from JSON in script tags"""
        import re

        leads = []
        try:
            # Look for JSON arrays or objects
            json_matches = re.findall(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', script_content)
            for match in json_matches:
                try:
                    data = json.loads(match)
                    if isinstance(data, dict) and any(key in data for key in ['name', 'company', 'installer']):
                        lead = self._normalize_json_lead(data)
                        if lead:
                            leads.append(lead)
                except:
                    continue
        except Exception as e:
            logger.debug(f"Failed to extract from JSON: {e}")

        return leads

    def _normalize_json_lead(self, data: Dict) -> Optional[Dict]:
        """Normalize lead data from various JSON formats"""
        try:
            return {
                'company_name': data.get('name') or data.get('company') or data.get('ragioneSociale', ''),
                'address': data.get('address') or data.get('indirizzo', ''),
                'city': data.get('city') or data.get('comune', ''),
                'region': data.get('region') or data.get('regione', ''),
                'phone': data.get('phone') or data.get('telefono', ''),
                'email': data.get('email') or data.get('pec', ''),
                'source': 'GSE.it',
                'scraped_date': datetime.now().isoformat(),
                'status': 'New Lead',
                'industry': 'Solar/Photovoltaic Installation'
            }
        except:
            return None

    def _extract_leads_from_page(self, page_source: str) -> List[Dict]:
        """
        Extract leads from page source using BeautifulSoup

        Args:
            page_source: HTML source code

        Returns:
            List of lead dictionaries
        """
        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(page_source, 'html.parser')
            leads = []

            # Try to find data - customize these selectors based on actual page structure
            # This is a template - you'll need to inspect the actual page

            # Example: Looking for table data
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows[1:]:  # Skip header
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        lead = {
                            'company_name': cells[0].get_text(strip=True),
                            'address': cells[1].get_text(strip=True) if len(cells) > 1 else '',
                            'region': cells[2].get_text(strip=True) if len(cells) > 2 else '',
                            'source': 'GSE.it',
                            'scraped_date': datetime.now().isoformat(),
                            'status': 'New Lead',
                            'industry': 'Solar/Photovoltaic Installation'
                        }
                        leads.append(lead)

            return leads

        except ImportError:
            logger.error("BeautifulSoup not installed. Install with: pip install beautifulsoup4")
            return []
        except Exception as e:
            logger.error(f"Failed to parse page source: {e}")
            return []

    def export_to_csv(self, leads: List[Dict], filename: str = None) -> str:
        """
        Export leads to CSV format (Airtable compatible)

        Args:
            leads: List of lead dictionaries
            filename: Output filename (optional)

        Returns:
            Path to exported file
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"gse_solar_leads_{timestamp}.csv"

        output_path = Path(__file__).parent.parent / "exports" / filename
        output_path.parent.mkdir(exist_ok=True)

        if not leads:
            logger.warning("No leads to export")
            return str(output_path)

        # Get all unique keys from all leads
        all_keys = set()
        for lead in leads:
            all_keys.update(lead.keys())

        fieldnames = sorted(all_keys)

        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(leads)

        logger.info(f"✓ Exported {len(leads)} leads to CSV: {output_path}")
        return str(output_path)

    def export_to_json(self, leads: List[Dict], filename: str = None) -> str:
        """
        Export leads to JSON format

        Args:
            leads: List of lead dictionaries
            filename: Output filename (optional)

        Returns:
            Path to exported file
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"gse_solar_leads_{timestamp}.json"

        output_path = Path(__file__).parent.parent / "exports" / filename
        output_path.parent.mkdir(exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as jsonfile:
            json.dump({
                'source': 'GSE.it Solar Installers',
                'scraped_at': datetime.now().isoformat(),
                'total_leads': len(leads),
                'leads': leads
            }, jsonfile, indent=2, ensure_ascii=False)

        logger.info(f"✓ Exported {len(leads)} leads to JSON: {output_path}")
        return str(output_path)

    def run(self, export_format: str = 'both') -> Dict:
        """
        Run the complete scraping workflow

        Args:
            export_format: 'csv', 'json', or 'both' (default: 'both')

        Returns:
            Dictionary with results and export paths
        """
        logger.info("🚀 Starting GSE Solar Installer Lead Scraper")
        logger.info(f"Target: {self.url}")

        # Scrape leads
        leads = self.scrape_with_selenium()

        if not leads:
            logger.warning("⚠️  No leads found. Please check the page structure.")
            return {
                'success': False,
                'leads_count': 0,
                'message': 'No leads extracted. Page structure may have changed.'
            }

        # Export results
        result = {
            'success': True,
            'leads_count': len(leads),
            'leads': leads
        }

        if export_format in ['csv', 'both']:
            result['csv_path'] = self.export_to_csv(leads)

        if export_format in ['json', 'both']:
            result['json_path'] = self.export_to_json(leads)

        logger.info(f"✅ Scraping complete! Found {len(leads)} leads")
        return result


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Scrape solar installer leads from GSE.it',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape and export to both CSV and JSON
  python gse_solar_scraper.py

  # Export to CSV only
  python gse_solar_scraper.py --format csv

  # Run in visible browser mode (not headless)
  python gse_solar_scraper.py --no-headless
        """
    )

    parser.add_argument(
        '--format',
        choices=['csv', 'json', 'both'],
        default='both',
        help='Export format (default: both)'
    )

    parser.add_argument(
        '--no-headless',
        action='store_true',
        help='Run browser in visible mode (useful for debugging)'
    )

    args = parser.parse_args()

    # Run scraper
    scraper = GSESolarScraper(headless=not args.no_headless)
    result = scraper.run(export_format=args.format)

    # Print summary
    print("\n" + "="*60)
    print("SCRAPING SUMMARY")
    print("="*60)
    print(f"Status: {'✅ Success' if result['success'] else '❌ Failed'}")
    print(f"Leads Found: {result['leads_count']}")

    if 'csv_path' in result:
        print(f"CSV Export: {result['csv_path']}")

    if 'json_path' in result:
        print(f"JSON Export: {result['json_path']}")

    print("="*60)

    return 0 if result['success'] else 1


if __name__ == '__main__':
    exit(main())
