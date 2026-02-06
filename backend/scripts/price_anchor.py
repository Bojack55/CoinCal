#!/usr/bin/env python3
"""
CoinCal Price Anchor - Ground Truth Price Tracker
Scrapes daily grocery prices from major Egyptian retailers for data validation.

This script provides the "Source of Truth" for the Egyptian market prices,
enabling the DataValidator to flag suspicious user-submitted prices.

REFACTORED: Now POSTs data to the CoinCal backend API instead of saving to JSON.
"""

import json
import logging
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, asdict

import requests
from bs4 import BeautifulSoup

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class PriceRecord:
    """Represents a single price observation."""
    item_id: str
    item_name: str
    price_egp: float
    unit: str
    source: str
    scraped_at: str
    confidence: str  # 'high', 'medium', 'low'


@dataclass
class DailyPriceReport:
    """Daily price report for the inflation basket."""
    date: str
    source: str
    items: list
    scrape_duration_seconds: float
    errors: list


# Configuration: The "Inflation Basket" - essential items to track
INFLATION_BASKET = {
    'rice_1kg': {
        'name': 'Rice (1kg)',
        'search_terms': ['rice', 'أرز', 'ارز'],
        'unit': 'kg',
        'expected_range': (25, 80),  # EGP min-max sanity range
    },
    'sugar_1kg': {
        'name': 'Sugar (1kg)',
        'search_terms': ['sugar', 'سكر'],
        'unit': 'kg',
        'expected_range': (25, 60),
    },
    'eggs_30pack': {
        'name': 'Local Eggs (30 pack)',
        'search_terms': ['eggs', 'بيض', 'egg tray'],
        'unit': '30 pack',
        'expected_range': (100, 250),
    },
    'chicken_1kg': {
        'name': 'Poultry Fillet (1kg)',
        'search_terms': ['chicken fillet', 'فراخ', 'صدور فراخ'],
        'unit': 'kg',
        'expected_range': (120, 280),
    },
    'oil_800ml': {
        'name': 'Sunflower Oil (800ml)',
        'search_terms': ['sunflower oil', 'زيت عباد الشمس', 'زيت طعام'],
        'unit': '800ml',
        'expected_range': (50, 120),
    },
}

# API Configuration - loads from .env with fallbacks
API_CONFIG = {
    'base_url': os.getenv('API_BASE_URL', 'http://127.0.0.1:8000'),
    'endpoint': '/api/prices/',
    'api_key': os.getenv('PRICE_ANCHOR_API_KEY', 'COINCAL_PRICE_ANCHOR_2026'),
}


class PriceAnchor:
    """
    Ground Truth Price Scraper for Egyptian grocery retailers.
    Uses BeautifulSoup for robust HTML parsing.
    """
    
    def __init__(self, output_dir: str = './', api_url: str = None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.api_url = api_url or f"{API_CONFIG['base_url']}{API_CONFIG['endpoint']}"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        })
        self.errors: list = []
    
    def check_api_health(self) -> bool:
        """
        Check if the Django API is reachable before attempting data insert.
        Returns True if API is available, False otherwise.
        """
        health_url = f"{API_CONFIG['base_url']}/api/"
        try:
            logger.info(f"Checking API health at {health_url}...")
            response = requests.get(health_url, timeout=5)
            if response.status_code < 500:
                logger.info("✓ API is reachable")
                return True
            else:
                logger.error(f"✗ API returned server error: {response.status_code}")
                return False
        except requests.ConnectionError:
            logger.error(f"✗ Cannot connect to API at {health_url}")
            logger.error("  Make sure Django server is running: python manage.py runserver 0.0.0.0:8000")
            return False
        except requests.Timeout:
            logger.error(f"✗ API request timed out")
            return False
        
    def _extract_price(self, text: str) -> Optional[Decimal]:
        """
        Extract numeric price from text, handling various formats.
        Returns None if no valid price found.
        """
        if not text:
            return None
            
        # Clean the text
        text = text.strip().replace(',', '').replace(' ', '')
        
        # Try to find price patterns
        patterns = [
            r'(\d+\.?\d*)\s*(?:EGP|جنيه|ج\.م|L\.E\.?)?',  # 45.99 EGP
            r'(?:EGP|جنيه|ج\.م|L\.E\.?)\s*(\d+\.?\d*)',   # EGP 45.99
            r'^(\d+\.?\d*)$',  # Just the number
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    price = Decimal(match.group(1))
                    if price > 0:  # Ignore zero prices
                        return price
                except (InvalidOperation, IndexError):
                    continue
        
        return None

    def _validate_price(self, price: float, item_id: str) -> tuple[bool, str]:
        """
        Validate price against expected range.
        Returns (is_valid, confidence_level).
        """
        if price <= 0:
            return False, 'invalid'
            
        expected_range = INFLATION_BASKET.get(item_id, {}).get('expected_range')
        if not expected_range:
            return True, 'medium'
            
        min_price, max_price = expected_range
        
        if min_price <= price <= max_price:
            return True, 'high'
        elif price < min_price * 0.5 or price > max_price * 2:
            return False, 'suspicious'
        else:
            return True, 'medium'

    def scrape_carrefour_egypt(self) -> list[PriceRecord]:
        """
        Scrape prices from Carrefour Egypt website.
        This is the primary source for grocery price anchoring.
        
        Note: In production, implement proper rate limiting and caching.
        """
        prices = []
        base_url = "https://www.carrefouregypt.com"
        
        # Category URLs for the inflation basket items
        category_urls = {
            'rice_1kg': '/mafegy/en/c/FEGY1320200',       # Rice & Grains
            'sugar_1kg': '/mafegy/en/c/FEGY1320800',      # Sugar & Sweeteners
            'eggs_30pack': '/mafegy/en/c/FEGY1420100',    # Eggs
            'chicken_1kg': '/mafegy/en/c/FEGY1430100',    # Poultry
            'oil_800ml': '/mafegy/en/c/FEGY1320400',      # Cooking Oils
        }
        
        for item_id, category_path in category_urls.items():
            try:
                item_config = INFLATION_BASKET[item_id]
                logger.info(f"Scraping {item_config['name']}...")
                
                # Make request to category page
                url = f"{base_url}{category_path}"
                response = self.session.get(url, timeout=15)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find product cards (Carrefour-specific selectors)
                # Note: These selectors may need updating as websites change
                product_cards = soup.select('.product-card, .css-1kp0xn4, [data-testid="product-card"]')
                
                if not product_cards:
                    # Fallback: try generic product listing patterns
                    product_cards = soup.select('[class*="product"], [class*="item-card"]')
                
                for card in product_cards[:10]:  # Check first 10 products
                    # Try to extract product name
                    name_elem = card.select_one('[class*="name"], [class*="title"], h3, h4')
                    if not name_elem:
                        continue
                        
                    product_name = name_elem.get_text().lower()
                    
                    # Check if product matches our search terms
                    search_terms = item_config['search_terms']
                    if not any(term.lower() in product_name for term in search_terms):
                        continue
                    
                    # Extract price
                    price_elem = card.select_one('[class*="price"], [class*="cost"], .css-1i90gmp')
                    if not price_elem:
                        continue
                        
                    price = self._extract_price(price_elem.get_text())
                    
                    if price is None or price <= 0:
                        logger.warning(f"Invalid price for {product_name}: {price_elem.get_text()}")
                        continue
                    
                    # Validate price sanity
                    is_valid, confidence = self._validate_price(price, item_id)
                    
                    if not is_valid:
                        logger.warning(f"Suspicious price rejected: {item_config['name']} = {price} EGP")
                        continue
                    
                    prices.append(PriceRecord(
                        item_id=item_id,
                        item_name=item_config['name'],
                        price_egp=price,
                        unit=item_config['unit'],
                        source='carrefour_egypt',
                        scraped_at=datetime.now().isoformat(),
                        confidence=confidence,
                    ))
                    
                    # Found a valid price, move to next item
                    logger.info(f"  ✓ {item_config['name']}: {price} EGP")
                    break
                else:
                    logger.warning(f"  ✗ No valid price found for {item_config['name']}")
                    self.errors.append(f"No price found: {item_config['name']}")
                    
            except requests.RequestException as e:
                logger.error(f"Network error scraping {item_id}: {e}")
                self.errors.append(f"Network error: {item_id} - {str(e)}")
            except Exception as e:
                logger.error(f"Error scraping {item_id}: {e}")
                self.errors.append(f"Scrape error: {item_id} - {str(e)}")
        
        return prices

    def scrape_mock_prices(self) -> list[PriceRecord]:
        """
        Generate realistic mock prices for testing when actual scraping fails.
        Uses the expected ranges from INFLATION_BASKET with some variance.
        """
        import random
        
        prices = []
        for item_id, config in INFLATION_BASKET.items():
            min_p, max_p = config['expected_range']
            # Generate a price within the expected range with some variance
            price = round(random.uniform(min_p * 0.9, max_p * 1.1), 2)
            
            prices.append(PriceRecord(
                item_id=item_id,
                item_name=config['name'],
                price_egp=price,
                unit=config['unit'],
                source='mock_data',
                scraped_at=datetime.now().isoformat(),
                confidence='mock',
            ))
            logger.info(f"  ✓ {config['name']}: {price} EGP (mock)")
        
        return prices

    def post_to_api(self, report: DailyPriceReport) -> bool:
        """
        POST the price data to the CoinCal backend API.
        Returns True if successful, False otherwise.
        """
        try:
            payload = {
                'date': report.date,
                'source': report.source,
                'items': report.items,
            }
            
            headers = {
                'Content-Type': 'application/json',
                'X-API-Key': API_CONFIG['api_key'],
            }
            
            logger.info(f"POSTing {len(report.items)} prices to {self.api_url}")
            
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 201:
                logger.info(f"✓ Successfully posted prices to API")
                logger.info(f"  Response: {response.json()}")
                return True
            else:
                logger.error(f"✗ API returned status {response.status_code}")
                logger.error(f"  Response: {response.text}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"✗ Failed to POST to API: {e}")
            return False

    def save_to_json(self, report: DailyPriceReport) -> None:
        """
        Fallback: Save prices to local JSON file if API is unavailable.
        """
        output_file = self.output_dir / 'daily_prices.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(report), f, indent=2, ensure_ascii=False)
        logger.info(f"Saved backup to {output_file}")

    def run(self, use_mock: bool = False, save_local: bool = False) -> DailyPriceReport:
        """
        Execute the daily price scraping job.
        
        Args:
            use_mock: If True, use mock data instead of actual scraping.
                      Useful for testing and when websites are unavailable.
            save_local: If True, also save to local JSON file as backup.
        """
        start_time = datetime.now()
        logger.info("=" * 50)
        logger.info(f"CoinCal Price Anchor - {start_time.strftime('%Y-%m-%d %H:%M')}")
        logger.info("=" * 50)
        
        if use_mock:
            logger.info("Using mock data (actual scraping disabled)")
            prices = self.scrape_mock_prices()
        else:
            prices = self.scrape_carrefour_egypt()
            
            # Fallback to mock if scraping returned no results
            if not prices:
                logger.warning("Scraping returned no results, falling back to mock data")
                prices = self.scrape_mock_prices()
        
        duration = (datetime.now() - start_time).total_seconds()
        
        report = DailyPriceReport(
            date=start_time.strftime('%Y-%m-%d'),
            source='carrefour_egypt' if not use_mock else 'mock_data',
            items=[asdict(p) for p in prices],
            scrape_duration_seconds=round(duration, 2),
            errors=self.errors,
        )
        
        # POST to API
        api_success = self.post_to_api(report)
        
        # Save to local JSON as fallback or if requested
        if save_local or not api_success:
            self.save_to_json(report)
        
        logger.info("-" * 50)
        logger.info(f"Collected {len(prices)} prices")
        logger.info(f"Duration: {duration:.2f}s")
        logger.info(f"API POST: {'✓ Success' if api_success else '✗ Failed (saved locally)'}")
        if self.errors:
            logger.warning(f"Errors: {len(self.errors)}")
        
        return report


def main():
    """CLI entry point for the price scraper."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='CoinCal Price Anchor - Daily grocery price scraper'
    )
    parser.add_argument(
        '--mock', 
        action='store_true',
        help='Use mock data instead of actual web scraping'
    )
    parser.add_argument(
        '--save-local',
        action='store_true',
        help='Also save prices to local JSON file'
    )
    parser.add_argument(
        '--api-url',
        type=str,
        default=None,
        help='Custom API URL for posting prices (default: http://127.0.0.1:8000/api/prices/)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='.',
        help='Directory to save the daily_prices.json file (for local backup)'
    )
    
    args = parser.parse_args()
    
    anchor = PriceAnchor(output_dir=args.output_dir, api_url=args.api_url)
    report = anchor.run(use_mock=args.mock, save_local=args.save_local)
    
    print(f"\n{'=' * 50}")
    print("DAILY PRICE SUMMARY")
    print('=' * 50)
    for item in report.items:
        confidence_icon = {'high': '✓', 'medium': '~', 'mock': '⚡'}.get(item['confidence'], '?')
        print(f"  [{confidence_icon}] {item['item_name']}: {item['price_egp']:.2f} EGP")
    print('=' * 50)


if __name__ == '__main__':
    main()
