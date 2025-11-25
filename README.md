# Pasardana Data Scraper

A robust web scraper for collecting daily mutual fund data from [pasardana.id](https://pasardana.id/fund/search) with full pagination support and automated pipeline capabilities.

## Features

- ✅ **Complete Data Extraction**: Scrapes all data from fund tables
- ✅ **Pagination Support**: Automatically handles all pages
- ✅ **Multiple Export Formats**: CSV, JSON, and Excel
- ✅ **GitHub Actions Integration**: Automated scraping with no server required
- ✅ **Automated Pipeline**: Schedule daily updates or run at intervals
- ✅ **Robust Error Handling**: Retry logic and comprehensive logging
- ✅ **Docker Support**: Containerized deployment ready
- ✅ **Configurable**: Environment-based configuration
- ✅ **Headless Mode**: Run without GUI for server deployments

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Internet connection

## Quick Start

### 1. Setup

Run the setup script to install all dependencies:

```bash
chmod +x setup.sh
./setup.sh
```

Or manually:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Create data directory
mkdir -p data

# Copy environment configuration
cp .env.example .env
```

### 2. Configuration

Edit `.env` file to customize settings:

```env
DATA_OUTPUT_DIR=./data          # Output directory for scraped data
SCRAPE_SCHEDULE_TIME=09:00      # Time for scheduled runs (24-hour format)
LOG_LEVEL=INFO                   # Logging level (DEBUG, INFO, WARNING, ERROR)
MAX_RETRIES=3                    # Maximum retry attempts
HEADLESS_MODE=true               # Run browser in headless mode
```

### 3. Run the Scraper

#### Run Once (Immediate)

```bash
python pipeline.py --mode once
```

#### Run on Schedule (Daily at specific time)

```bash
python pipeline.py --mode schedule --time "09:00"
```

#### Run at Intervals

```bash
# Run every 6 hours
python pipeline.py --mode interval --hours 6

# Run every 24 hours
python pipeline.py --mode interval --hours 24
```

## Usage Examples

### Basic Scraping

```python
from scraper import PasardanaScraper
import asyncio

async def main():
    scraper = PasardanaScraper(headless=True)
    await scraper.run(output_formats=['csv', 'json'])

asyncio.run(main())
```

### Custom Pipeline

```python
from pipeline import PasardanaPipeline

pipeline = PasardanaPipeline()
pipeline.run_once()  # Run immediately
```

## Output

The scraper generates timestamped files in the configured output directory:

- `pasardana_funds_YYYYMMDD_HHMMSS.csv` - CSV format
- `pasardana_funds_YYYYMMDD_HHMMSS.json` - JSON format
- `pasardana_funds_latest.csv` - Latest data (overwritten each run)
- `pasardana_funds_latest.json` - Latest data (overwritten each run)

### Output Format

Each record includes:
- All columns from the fund table (dynamically extracted)
- `scraped_at`: Timestamp when data was scraped
- `page_number`: Source page number

## Project Structure

```
pasardana/
├── .github/
│   └── workflows/
│       ├── scraper.yml          # Daily scraper workflow
│       ├── weekly-archive.yml   # Weekly archive workflow
│       ├── test.yml            # Test workflow
│       └── README.md           # Workflows documentation
├── scraper.py           # Main scraper implementation
├── pipeline.py          # Automated pipeline and scheduler
├── setup.sh            # Setup script
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker container configuration
├── docker-compose.yml  # Docker Compose setup
├── .env.example        # Example configuration
├── .env               # Your configuration (not in git)
├── .gitignore         # Git ignore rules
├── README.md          # This file
├── QUICKSTART.md      # Quick start guide
├── data/              # Output directory (created automatically)
│   ├── *.csv
│   └── *.json
└── logs/              # Log files
    ├── scraper.log
    └── pipeline.log
```

## GitHub Actions (Recommended)

The easiest way to automate the scraper is using GitHub Actions. No server required!

### Quick Setup

1. **Push to GitHub**: Workflows are already configured in `.github/workflows/`
2. **Enable Actions**: Go to repository Settings → Actions → Enable workflows
3. **Done!** Scraper runs automatically daily at 9:00 AM UTC

### Available Workflows

#### Daily Scraper (scraper.yml)
- **Schedule**: Daily at 9:00 AM UTC (customizable)
- **Manual trigger**: Actions tab → Run workflow
- **Outputs**:
  - Data uploaded as artifacts (90-day retention)
  - Latest data committed to `data` branch
  - Run summary with statistics

#### Weekly Archive (weekly-archive.yml)
- **Schedule**: Weekly on Sundays
- **Purpose**: Creates compressed archives of data
- **Retention**: Last 12 weeks

#### Test Suite (test.yml)
- **Trigger**: On pull requests
- **Tests**: Python 3.9-3.12, linting, imports

### Manual Run

1. Go to **Actions** tab on GitHub
2. Select "Pasardana Data Scraper"
3. Click "Run workflow"
4. Choose log level and run

### Accessing Scraped Data

**From Data Branch**:
```bash
git checkout data
ls data/
```

**Download from GitHub**:
- Navigate to: `https://github.com/USERNAME/REPO/tree/data`
- Download `pasardana_funds_latest.csv` or `.json`

**Via GitHub Actions Artifacts**:
- Actions tab → Workflow run → Artifacts section

### Customize Schedule

Edit `.github/workflows/scraper.yml`:
```yaml
schedule:
  - cron: '0 */6 * * *'  # Every 6 hours
  - cron: '0 9,21 * * *'  # Twice daily (9 AM, 9 PM UTC)
  - cron: '0 9 * * 1-5'  # Weekdays only
```

**Cron Helper**: [crontab.guru](https://crontab.guru/)

### Add Status Badge

Add to README:
```markdown
![Scraper Status](https://github.com/USERNAME/REPO/actions/workflows/scraper.yml/badge.svg)
```

### Free Tier Limits

- **Public repos**: Unlimited
- **Private repos**: 2,000 minutes/month
- **Typical run**: ~5-8 minutes

For detailed GitHub Actions documentation, see [.github/workflows/README.md](.github/workflows/README.md)

## Local Automation

If you prefer to run locally instead of GitHub Actions:

### Using Cron (Linux/Mac)

Add to crontab (`crontab -e`):

```bash
# Run daily at 9:00 AM
0 9 * * * cd /path/to/pasardana && /path/to/venv/bin/python pipeline.py --mode once >> logs/cron.log 2>&1
```

### Using Task Scheduler (Windows)

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (daily at 9:00 AM)
4. Action: Start a program
   - Program: `C:\path\to\venv\Scripts\python.exe`
   - Arguments: `pipeline.py --mode once`
   - Start in: `C:\path\to\pasardana`

### Using systemd (Linux)

Create service file `/etc/systemd/system/pasardana-scraper.service`:

```ini
[Unit]
Description=Pasardana Fund Data Scraper
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/pasardana
Environment="PATH=/path/to/pasardana/venv/bin"
ExecStart=/path/to/pasardana/venv/bin/python pipeline.py --mode schedule --time "09:00"
Restart=on-failure
RestartSec=60

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable pasardana-scraper
sudo systemctl start pasardana-scraper
sudo systemctl status pasardana-scraper
```

## Logging

Logs are written to:
- `scraper.log` - Scraper activity
- `pipeline.log` - Pipeline/scheduler activity

Log levels can be configured via `LOG_LEVEL` in `.env`:
- `DEBUG` - Detailed information
- `INFO` - General information (default)
- `WARNING` - Warning messages
- `ERROR` - Error messages only

## Troubleshooting

### Browser Launch Errors

If Playwright fails to launch the browser:

```bash
# Reinstall browsers
playwright install chromium

# On Linux, install system dependencies
playwright install-deps chromium
```

### Permission Errors

Make sure the scripts are executable:

```bash
chmod +x setup.sh
```

### Network Errors

- Check internet connection
- Verify the website is accessible
- Try increasing timeout values in scraper.py

### No Data Scraped

- The website structure may have changed
- Run in non-headless mode to debug: set `HEADLESS_MODE=false` in `.env`
- Check logs for detailed error messages

## Advanced Configuration

### Custom Selectors

If the website structure changes, update selectors in `scraper.py`:

```python
# In scrape_page() method
await page.wait_for_selector('your-custom-selector')

# In check_next_page() method
next_selectors = ['your-custom-next-button-selector']
```

### Retry Logic

Adjust retry settings in `.env`:

```env
MAX_RETRIES=5  # Increase for unreliable connections
```

### Custom Export Formats

Modify the `save_data()` method in `scraper.py` to add custom formats.

## Development

### Running Tests

```bash
# Run scraper in debug mode
LOG_LEVEL=DEBUG python pipeline.py --mode once

# Run with visible browser
HEADLESS_MODE=false python pipeline.py --mode once
```

### Code Structure

- `PasardanaScraper` class: Core scraping logic
  - `scrape_page()`: Extract data from single page
  - `check_next_page()`: Handle pagination
  - `scrape_all_pages()`: Orchestrate full scrape
  - `save_data()`: Export to various formats

- `PasardanaPipeline` class: Automation and scheduling
  - `run_once()`: Single execution
  - `run_scheduled()`: Daily schedule
  - `run_interval()`: Periodic execution

## Performance

- Scraping speed: ~1-2 seconds per page
- Memory usage: ~100-200 MB
- Network: Depends on page count and data size

## License

This project is for educational and personal use. Ensure compliance with pasardana.id's terms of service and robots.txt before scraping.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues and questions:
- Check logs for error messages
- Review troubleshooting section
- Open an issue on GitHub

## Disclaimer

This scraper is provided as-is for educational purposes. Users are responsible for:
- Complying with website terms of service
- Respecting rate limits
- Using data ethically and legally

Always verify you have permission to scrape a website before doing so.
