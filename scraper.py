"""
Pasardana Fund Data Scraper
Scrapes daily mutual fund data from pasardana.id with pagination support
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

import pandas as pd
from playwright.async_api import async_playwright, Page, Browser
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class PasardanaScraper:
    """Scraper for pasardana.id mutual fund data"""

    def __init__(self, headless: bool = True):
        self.base_url = "https://pasardana.id/fund/search"
        self.headless = headless
        self.max_retries = int(os.getenv('MAX_RETRIES', 3))
        self.data_output_dir = Path(os.getenv('DATA_OUTPUT_DIR', './data'))
        self.data_output_dir.mkdir(exist_ok=True)

    async def scrape_page(self, page: Page, page_num: int) -> List[Dict]:
        """
        Scrape data from a single page

        Args:
            page: Playwright page object
            page_num: Current page number

        Returns:
            List of dictionaries containing fund data
        """
        logger.info(f"Scraping page {page_num}")

        try:
            # Wait for table to load
            await page.wait_for_selector('table', timeout=30000)

            # Extract table data
            table_data = await page.evaluate('''() => {
                const rows = Array.from(document.querySelectorAll('table tbody tr'));
                return rows.map(row => {
                    const cells = Array.from(row.querySelectorAll('td'));
                    return cells.map(cell => cell.innerText.trim());
                });
            }''')

            # Get table headers
            headers = await page.evaluate('''() => {
                const headers = Array.from(document.querySelectorAll('table thead th'));
                return headers.map(th => th.innerText.trim());
            }''')

            if not headers or len(headers) == 0:
                # Try alternative selectors
                headers = await page.evaluate('''() => {
                    const headers = Array.from(document.querySelectorAll('table th'));
                    return headers.map(th => th.innerText.trim());
                }''')

            # Clean up headers: remove empty trailing columns
            while headers and headers[-1] == '':
                headers.pop()

            # Remove duplicate empty headers by renaming them
            header_counts = {}
            cleaned_headers = []
            for header in headers:
                if header == '':
                    count = header_counts.get('_empty_', 0)
                    cleaned_headers.append(f'_empty_{count}')
                    header_counts['_empty_'] = count + 1
                else:
                    cleaned_headers.append(header)
            headers = cleaned_headers

            logger.info(f"Found {len(headers)} columns: {headers[:10]}..." if len(headers) > 10 else f"Found {len(headers)} columns: {headers}")
            logger.info(f"Found {len(table_data)} rows on page {page_num}")

            # Convert to list of dictionaries
            records = []
            for row_data in table_data:
                # Skip empty rows (single column with no data)
                if len(row_data) == 1 and not row_data[0]:
                    continue

                # Pad row data with empty strings if it's shorter than headers
                if len(row_data) < len(headers):
                    row_data = row_data + [''] * (len(headers) - len(row_data))
                # Truncate row data if it's longer than headers
                elif len(row_data) > len(headers):
                    logger.warning(f"Row data length ({len(row_data)}) exceeds headers ({len(headers)}), truncating")
                    row_data = row_data[:len(headers)]

                record = dict(zip(headers, row_data))
                record['scraped_at'] = datetime.now().isoformat()
                record['page_number'] = page_num
                records.append(record)

            return records

        except Exception as e:
            logger.error(f"Error scraping page {page_num}: {str(e)}")
            return []

    async def check_next_page(self, page: Page) -> bool:
        """
        Check if there's a next page and navigate to it

        Args:
            page: Playwright page object

        Returns:
            True if successfully navigated to next page, False otherwise
        """
        try:
            # Common pagination selectors
            next_selectors = [
                'a.page-link:has-text("Next")',
                'button:has-text("Next")',
                'a:has-text("›")',
                'button:has-text("›")',
                'a.next',
                'button.next',
                'li.next a',
                'li.pagination-next a',
                '[aria-label="Next"]',
                '.pagination .next:not(.disabled) a',
            ]

            for selector in next_selectors:
                try:
                    next_button = await page.query_selector(selector)
                    if next_button:
                        is_disabled = await next_button.evaluate('''(element) => {
                            return element.disabled ||
                                   element.classList.contains('disabled') ||
                                   element.parentElement.classList.contains('disabled');
                        }''')

                        if not is_disabled:
                            logger.info(f"Found next button with selector: {selector}")
                            await next_button.click()
                            await page.wait_for_load_state('load', timeout=30000)
                            await asyncio.sleep(3)  # Additional wait for dynamic content
                            return True
                except Exception:
                    continue

            # Try pagination by page numbers
            try:
                current_page_elem = await page.query_selector('.pagination .active, .page-item.active')
                if current_page_elem:
                    # Get next page number
                    current_text = await current_page_elem.inner_text()
                    try:
                        current_num = int(current_text.strip())
                        next_num = current_num + 1
                        next_page_selector = f'a.page-link:has-text("{next_num}")'
                        next_page = await page.query_selector(next_page_selector)
                        if next_page:
                            logger.info(f"Navigating to page {next_num}")
                            await next_page.click()
                            await page.wait_for_load_state('load', timeout=30000)
                            await asyncio.sleep(3)
                            return True
                    except ValueError:
                        pass
            except Exception:
                pass

            logger.info("No next page found")
            return False

        except Exception as e:
            logger.error(f"Error checking for next page: {str(e)}")
            return False

    async def scrape_all_pages(self) -> pd.DataFrame:
        """
        Scrape all pages with pagination support

        Returns:
            DataFrame containing all scraped data
        """
        all_data = []
        page_num = 1

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            page = await context.new_page()

            try:
                logger.info(f"Navigating to {self.base_url}")
                # Use domcontentloaded instead of networkidle for better reliability in CI environments
                # Retry up to 3 times if navigation fails
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        await page.goto(self.base_url, wait_until='domcontentloaded', timeout=90000)
                        logger.info(f"Successfully loaded page on attempt {attempt + 1}")
                        break
                    except Exception as e:
                        if attempt < max_retries - 1:
                            logger.warning(f"Navigation attempt {attempt + 1} failed: {e}. Retrying...")
                            await asyncio.sleep(5)
                        else:
                            logger.error(f"All navigation attempts failed")
                            raise

                # Wait for content to load and any JavaScript to execute
                await asyncio.sleep(5)

                # Check if we need to handle any popups or cookie consent
                try:
                    cookie_selectors = ['button:has-text("Accept")', 'button:has-text("Setuju")', '.cookie-consent button']
                    for selector in cookie_selectors:
                        cookie_btn = await page.query_selector(selector)
                        if cookie_btn:
                            await cookie_btn.click()
                            await asyncio.sleep(1)
                            break
                except Exception:
                    pass

                # Scrape first page
                page_data = await self.scrape_page(page, page_num)
                all_data.extend(page_data)

                # Scrape remaining pages
                while True:
                    has_next = await self.check_next_page(page)
                    if not has_next:
                        break

                    page_num += 1
                    page_data = await self.scrape_page(page, page_num)

                    if not page_data:
                        logger.warning(f"No data found on page {page_num}, stopping pagination")
                        break

                    all_data.extend(page_data)

                    # Safety limit to prevent infinite loops
                    if page_num > 1000:
                        logger.warning("Reached maximum page limit (1000), stopping")
                        break

            except Exception as e:
                logger.error(f"Error during scraping: {str(e)}")
                raise
            finally:
                await browser.close()

        logger.info(f"Total records scraped: {len(all_data)} from {page_num} pages")

        if not all_data:
            logger.warning("No data was scraped")
            return pd.DataFrame()

        return pd.DataFrame(all_data)

    def save_data(self, df: pd.DataFrame, format: str = 'csv') -> Path:
        """
        Save scraped data to file

        Args:
            df: DataFrame containing scraped data
            format: Output format ('csv', 'json', 'excel')

        Returns:
            Path to saved file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        if format == 'csv':
            filename = self.data_output_dir / f'pasardana_funds_{timestamp}.csv'
            df.to_csv(filename, index=False, encoding='utf-8-sig')
        elif format == 'json':
            filename = self.data_output_dir / f'pasardana_funds_{timestamp}.json'
            df.to_json(filename, orient='records', indent=2, force_ascii=False)
        elif format == 'excel':
            filename = self.data_output_dir / f'pasardana_funds_{timestamp}.xlsx'
            df.to_excel(filename, index=False, engine='openpyxl')
        else:
            raise ValueError(f"Unsupported format: {format}")

        logger.info(f"Data saved to {filename}")

        # Also save as latest
        latest_filename = self.data_output_dir / f'pasardana_funds_latest.{format}'
        if format == 'csv':
            df.to_csv(latest_filename, index=False, encoding='utf-8-sig')
        elif format == 'json':
            df.to_json(latest_filename, orient='records', indent=2, force_ascii=False)
        elif format == 'excel':
            df.to_excel(latest_filename, index=False, engine='openpyxl')

        logger.info(f"Latest data saved to {latest_filename}")

        return filename

    async def run(self, output_formats: List[str] = ['csv', 'json']) -> Dict[str, Path]:
        """
        Run the complete scraping process

        Args:
            output_formats: List of output formats to save

        Returns:
            Dictionary mapping format to file path
        """
        logger.info("Starting Pasardana scraping process")

        # Scrape data
        df = await self.scrape_all_pages()

        if df.empty:
            logger.error("No data scraped, exiting")
            return {}

        # Display summary
        logger.info(f"\nData Summary:")
        logger.info(f"Total records: {len(df)}")
        logger.info(f"Columns: {list(df.columns)}")

        # Save in multiple formats
        saved_files = {}
        for fmt in output_formats:
            try:
                filepath = self.save_data(df, fmt)
                saved_files[fmt] = filepath
            except Exception as e:
                logger.error(f"Error saving {fmt} format: {str(e)}")

        logger.info("Scraping process completed successfully")
        return saved_files


async def main():
    """Main entry point"""
    headless = os.getenv('HEADLESS_MODE', 'true').lower() == 'true'
    scraper = PasardanaScraper(headless=headless)

    try:
        await scraper.run(output_formats=['csv', 'json'])
    except Exception as e:
        logger.error(f"Scraping failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
