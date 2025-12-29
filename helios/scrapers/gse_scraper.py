#!/usr/bin/env python3
"""
GSE Solar Installer Scraper for HELIOS
=======================================

Scrapes solar installer leads from:
https://www.gse.it/servizi-per-te/fotovoltaico/reddito-energetico/mappa-realizzatori-impianti-fotovoltaici
"""

import logging
import time
import re
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class GSEScraper:
    """Scraper for GSE solar installer directory"""

    def __init__(self, headless: bool = True):
        """
        Initialize scraper

        Args:
            headless: Run browser in headless mode
        """
        self.url = "https://www.gse.it/servizi-per-te/fotovoltaico/reddito-energetico/mappa-realizzatori-impianti-fotovoltaici"
        self.headless = headless
        self.driver = None

    def setup_driver(self):
        """Set up Selenium WebDriver"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC

            chrome_options = Options()

            if self.headless:
                chrome_options.add_argument('--headless=new')

            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

            # Exclude automation flags
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)

            # Try to use webdriver-manager for automatic driver management
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            except:
                # Fallback to system ChromeDriver
                self.driver = webdriver.Chrome(options=chrome_options)

            self.wait = WebDriverWait(self.driver, 30)

            # Execute CDP commands to mask automation
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            logger.info("✓ Selenium driver initialized")
            return True

        except ImportError:
            logger.error("Selenium not installed. Run: pip install selenium")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize driver: {e}")
            return False

    def scrape(self) -> List[Dict]:
        """
        Main scraping method

        Returns:
            List of lead dictionaries
        """
        if not self.setup_driver():
            return []

        leads = []

        try:
            logger.info(f"Loading page: {self.url}")
            self.driver.get(self.url)

            # Wait for page to load
            time.sleep(5)

            # Save page source for debugging
            page_source = self.driver.page_source

            # Try multiple extraction strategies
            leads = self._extract_with_multiple_strategies()

            if not leads:
                logger.warning("No leads found with automated extraction")
                logger.info("Saving page source for manual inspection...")
                self._save_debug_info()

            logger.info(f"✓ Found {len(leads)} leads")

        except Exception as e:
            logger.error(f"Scraping error: {e}")
            self._save_debug_info()

        finally:
            if self.driver:
                self.driver.quit()

        return leads

    def _extract_with_multiple_strategies(self) -> List[Dict]:
        """Try multiple extraction strategies"""
        from selenium.webdriver.common.by import By

        leads = []

        # Strategy 1: Look for table data
        leads.extend(self._extract_from_tables())

        # Strategy 2: Look for list items
        if not leads:
            leads.extend(self._extract_from_lists())

        # Strategy 3: Look for card/container elements
        if not leads:
            leads.extend(self._extract_from_containers())

        # Strategy 4: Extract from JSON in page
        if not leads:
            leads.extend(self._extract_from_scripts())

        # Strategy 5: Look for specific GSE structure
        if not leads:
            leads.extend(self._extract_gse_specific())

        return leads

    def _extract_from_tables(self) -> List[Dict]:
        """Extract from HTML tables"""
        from selenium.webdriver.common.by import By

        leads = []
        try:
            tables = self.driver.find_elements(By.TAG_NAME, "table")
            logger.info(f"Found {len(tables)} tables")

            for table in tables:
                rows = table.find_elements(By.TAG_NAME, "tr")

                for i, row in enumerate(rows):
                    if i == 0:  # Skip header
                        continue

                    cells = row.find_elements(By.TAG_NAME, "td")
                    if not cells:
                        cells = row.find_elements(By.TAG_NAME, "th")

                    if len(cells) >= 2:
                        lead = self._parse_table_row(cells)
                        if lead:
                            leads.append(lead)

        except Exception as e:
            logger.debug(f"Table extraction failed: {e}")

        return leads

    def _parse_table_row(self, cells) -> Optional[Dict]:
        """Parse a table row into lead data"""
        try:
            # Adapt based on actual table structure
            data = [cell.text.strip() for cell in cells]

            if not data or not data[0]:
                return None

            lead = {
                'company_name': data[0] if len(data) > 0 else '',
                'address': data[1] if len(data) > 1 else '',
                'city': data[2] if len(data) > 2 else '',
                'region': data[3] if len(data) > 3 else '',
                'phone': data[4] if len(data) > 4 else '',
                'email': data[5] if len(data) > 5 else '',
                'source': 'GSE.it',
                'scraped_date': datetime.now().isoformat(),
                'status': 'new_lead',
                'industry': 'Solar/Photovoltaic Installation',
            }

            # Extract email and phone using regex if not in specific columns
            full_text = ' '.join(data)
            if not lead['email']:
                email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', full_text)
                if email_match:
                    lead['email'] = email_match.group()

            if not lead['phone']:
                phone_match = re.search(r'[\+\d][\d\s\-\(\)]{8,}', full_text)
                if phone_match:
                    lead['phone'] = phone_match.group()

            return lead

        except Exception as e:
            logger.debug(f"Failed to parse table row: {e}")
            return None

    def _extract_from_lists(self) -> List[Dict]:
        """Extract from HTML lists"""
        from selenium.webdriver.common.by import By

        leads = []
        try:
            list_items = self.driver.find_elements(By.CSS_SELECTOR, "ul li, ol li")
            logger.info(f"Found {len(list_items)} list items")

            for item in list_items:
                text = item.text.strip()
                if len(text) > 20:  # Minimum content
                    lead = self._parse_text_block(text)
                    if lead:
                        leads.append(lead)

        except Exception as e:
            logger.debug(f"List extraction failed: {e}")

        return leads

    def _extract_from_containers(self) -> List[Dict]:
        """Extract from card/div containers"""
        from selenium.webdriver.common.by import By

        leads = []
        try:
            # Try various container selectors
            selectors = [
                "div.installer",
                "div.company",
                "div.card",
                "article",
                "div[class*='install']",
                "div[class*='company']",
            ]

            for selector in selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    logger.info(f"Found {len(elements)} elements with selector: {selector}")

                    for elem in elements:
                        text = elem.text.strip()
                        if len(text) > 20:
                            lead = self._parse_text_block(text)
                            if lead:
                                leads.append(lead)

                    if leads:
                        break

        except Exception as e:
            logger.debug(f"Container extraction failed: {e}")

        return leads

    def _parse_text_block(self, text: str) -> Optional[Dict]:
        """Parse a text block into lead data"""
        try:
            lines = [line.strip() for line in text.split('\n') if line.strip()]

            if not lines:
                return None

            lead = {
                'company_name': lines[0],
                'source': 'GSE.it',
                'scraped_date': datetime.now().isoformat(),
                'status': 'new_lead',
                'industry': 'Solar/Photovoltaic Installation',
                'notes': '\n'.join(lines[1:]) if len(lines) > 1 else '',
            }

            # Extract structured data using regex
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
            phone_match = re.search(r'[\+\d][\d\s\-\(\)]{8,}', text)
            pec_match = re.search(r'PEC[:\s]*([\w\.-]+@[\w\.-]+\.\w+)', text, re.IGNORECASE)

            if email_match:
                lead['email'] = email_match.group()
            if phone_match:
                lead['phone'] = phone_match.group()
            if pec_match:
                lead['pec'] = pec_match.group(1)

            return lead

        except Exception as e:
            logger.debug(f"Failed to parse text block: {e}")
            return None

    def _extract_from_scripts(self) -> List[Dict]:
        """Extract from JSON data in script tags"""
        from selenium.webdriver.common.by import By
        import json

        leads = []
        try:
            scripts = self.driver.find_elements(By.TAG_NAME, "script")

            for script in scripts:
                content = script.get_attribute('innerHTML')
                if not content:
                    continue

                # Look for JSON arrays or objects
                try:
                    # Try to find JSON data
                    json_match = re.search(r'\[{.*}\]', content, re.DOTALL)
                    if json_match:
                        data = json.loads(json_match.group())
                        if isinstance(data, list):
                            for item in data:
                                lead = self._parse_json_object(item)
                                if lead:
                                    leads.append(lead)
                except:
                    continue

        except Exception as e:
            logger.debug(f"Script extraction failed: {e}")

        return leads

    def _parse_json_object(self, obj: Dict) -> Optional[Dict]:
        """Parse JSON object into lead data"""
        try:
            # Try various field name patterns
            name_fields = ['name', 'ragioneSociale', 'company', 'denominazione']
            address_fields = ['address', 'indirizzo']
            email_fields = ['email', 'mail', 'posta']

            lead = {
                'source': 'GSE.it',
                'scraped_date': datetime.now().isoformat(),
                'status': 'new_lead',
                'industry': 'Solar/Photovoltaic Installation',
            }

            for field in name_fields:
                if field in obj:
                    lead['company_name'] = obj[field]
                    break

            for field in address_fields:
                if field in obj:
                    lead['address'] = obj[field]

            for field in email_fields:
                if field in obj:
                    lead['email'] = obj[field]

            # Add other common fields
            field_mapping = {
                'telefono': 'phone',
                'phone': 'phone',
                'citta': 'city',
                'city': 'city',
                'regione': 'region',
                'region': 'region',
                'pec': 'pec',
                'partitaIva': 'vat_number',
            }

            for json_key, lead_key in field_mapping.items():
                if json_key in obj:
                    lead[lead_key] = obj[json_key]

            if 'company_name' in lead and lead['company_name']:
                return lead

        except Exception as e:
            logger.debug(f"Failed to parse JSON object: {e}")

        return None

    def _extract_gse_specific(self) -> List[Dict]:
        """Extract using GSE-specific selectors"""
        from selenium.webdriver.common.by import By

        leads = []
        try:
            # Look for map markers or specific GSE elements
            # This will need to be customized based on actual page inspection

            # Try to find interactive map elements
            map_elements = self.driver.find_elements(By.CSS_SELECTOR, "[class*='map'], [id*='map']")
            logger.info(f"Found {len(map_elements)} map-related elements")

            # Check for data attributes
            elements_with_data = self.driver.find_elements(By.CSS_SELECTOR, "[data-company], [data-name], [data-installer]")
            logger.info(f"Found {len(elements_with_data)} elements with data attributes")

            for elem in elements_with_data:
                lead = {
                    'company_name': elem.get_attribute('data-company') or elem.get_attribute('data-name') or elem.get_attribute('data-installer'),
                    'source': 'GSE.it',
                    'scraped_date': datetime.now().isoformat(),
                    'status': 'new_lead',
                    'industry': 'Solar/Photovoltaic Installation',
                }

                # Get other data attributes
                for attr in ['data-address', 'data-phone', 'data-email', 'data-region']:
                    value = elem.get_attribute(attr)
                    if value:
                        key = attr.replace('data-', '')
                        lead[key] = value

                if lead.get('company_name'):
                    leads.append(lead)

        except Exception as e:
            logger.debug(f"GSE-specific extraction failed: {e}")

        return leads

    def _save_debug_info(self):
        """Save page source and screenshot for debugging"""
        try:
            from pathlib import Path

            debug_dir = Path(__file__).parent.parent / "logs"
            debug_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            # Save screenshot
            screenshot_path = debug_dir / f"gse_page_{timestamp}.png"
            self.driver.save_screenshot(str(screenshot_path))
            logger.info(f"Screenshot saved: {screenshot_path}")

            # Save page source
            source_path = debug_dir / f"gse_source_{timestamp}.html"
            with open(source_path, 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            logger.info(f"Page source saved: {source_path}")

        except Exception as e:
            logger.error(f"Failed to save debug info: {e}")
