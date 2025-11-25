"""
Automated Pipeline for Pasardana Data Scraper
Schedules and runs the scraper at specified intervals
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

import schedule
import time
from dotenv import load_dotenv

from scraper import PasardanaScraper

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class PasardanaPipeline:
    """Automated pipeline for running Pasardana scraper on schedule"""

    def __init__(self):
        self.schedule_time = os.getenv('SCRAPE_SCHEDULE_TIME', '09:00')
        self.headless = os.getenv('HEADLESS_MODE', 'true').lower() == 'true'
        self.scraper = PasardanaScraper(headless=self.headless)

    async def run_scraper_job(self):
        """
        Execute the scraper job

        Returns:
            bool: True if successful, False otherwise
        """
        logger.info("=" * 60)
        logger.info(f"Starting scheduled scrape job at {datetime.now()}")
        logger.info("=" * 60)

        try:
            saved_files = await self.scraper.run(output_formats=['csv', 'json'])

            if saved_files:
                logger.info("Scrape job completed successfully")
                logger.info("Saved files:")
                for fmt, filepath in saved_files.items():
                    logger.info(f"  - {fmt.upper()}: {filepath}")
                logger.info("=" * 60)
                return True
            else:
                logger.error("Scrape job completed but no files were saved")
                logger.info("=" * 60)
                return False

        except Exception as e:
            logger.error(f"Scrape job failed: {str(e)}", exc_info=True)
            logger.info("=" * 60)
            return False

    def run_scraper_sync(self):
        """
        Synchronous wrapper for async scraper job

        Returns:
            bool: True if successful, False otherwise
        """
        return asyncio.run(self.run_scraper_job())

    def run_once(self):
        """
        Run the scraper once immediately

        Returns:
            bool: True if successful, False otherwise
        """
        logger.info("Running scraper once (immediate execution)")
        return self.run_scraper_sync()

    def run_scheduled(self):
        """Run the scraper on a schedule"""
        logger.info(f"Setting up scheduled scraping at {self.schedule_time} daily")
        schedule.every().day.at(self.schedule_time).do(self.run_scraper_sync)

        logger.info("Pipeline is running. Press Ctrl+C to stop.")
        logger.info(f"Next run scheduled at: {self.schedule_time}")

        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Pipeline stopped by user")

    def run_interval(self, hours: int = 24):
        """
        Run the scraper at fixed intervals

        Args:
            hours: Number of hours between runs
        """
        logger.info(f"Setting up scraping every {hours} hours")
        schedule.every(hours).hours.do(self.run_scraper_sync)

        # Run once immediately
        logger.info("Running initial scrape...")
        self.run_scraper_sync()

        logger.info("Pipeline is running. Press Ctrl+C to stop.")

        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Pipeline stopped by user")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Pasardana Data Scraper Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run once immediately
  python pipeline.py --mode once

  # Run on daily schedule at 09:00
  python pipeline.py --mode schedule --time "09:00"

  # Run every 6 hours
  python pipeline.py --mode interval --hours 6

Environment Variables:
  SCRAPE_SCHEDULE_TIME: Default schedule time (default: 09:00)
  HEADLESS_MODE: Run browser in headless mode (default: true)
  DATA_OUTPUT_DIR: Directory for output files (default: ./data)
  LOG_LEVEL: Logging level (default: INFO)
        """
    )

    parser.add_argument(
        '--mode',
        choices=['once', 'schedule', 'interval'],
        default='once',
        help='Execution mode (default: once)'
    )

    parser.add_argument(
        '--time',
        type=str,
        default=None,
        help='Time for scheduled runs in HH:MM format (default: from SCRAPE_SCHEDULE_TIME env)'
    )

    parser.add_argument(
        '--hours',
        type=int,
        default=24,
        help='Hours between runs for interval mode (default: 24)'
    )

    args = parser.parse_args()

    # Create pipeline
    pipeline = PasardanaPipeline()

    # Override schedule time if provided
    if args.time:
        pipeline.schedule_time = args.time

    # Run based on mode
    try:
        if args.mode == 'once':
            success = pipeline.run_once()
            if not success:
                logger.error("Scraper failed - exiting with error code")
                sys.exit(1)
        elif args.mode == 'schedule':
            pipeline.run_scheduled()
        elif args.mode == 'interval':
            pipeline.run_interval(hours=args.hours)
    except Exception as e:
        logger.error(f"Pipeline execution failed: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
