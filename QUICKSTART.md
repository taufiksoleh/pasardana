# Quick Start Guide

Get up and running with Pasardana scraper in 5 minutes!

## Option 1: Using Setup Script (Recommended)

```bash
# 1. Make setup script executable
chmod +x setup.sh

# 2. Run setup
./setup.sh

# 3. Activate virtual environment
source venv/bin/activate

# 4. Run the scraper
python pipeline.py --mode once
```

## Option 2: Using Docker (Easiest)

```bash
# 1. Run once
docker-compose run scraper-once

# 2. Or run on schedule (daily at 9 AM)
docker-compose up pasardana-scraper

# 3. Or run every 6 hours
docker-compose --profile interval up scraper-interval
```

## Option 3: Manual Setup

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt
playwright install chromium

# 3. Create config
cp .env.example .env

# 4. Run
python pipeline.py --mode once
```

## Common Commands

```bash
# Run once immediately
python pipeline.py --mode once

# Run daily at 9:00 AM
python pipeline.py --mode schedule --time "09:00"

# Run every 6 hours
python pipeline.py --mode interval --hours 6

# Run with debug logging
LOG_LEVEL=DEBUG python pipeline.py --mode once

# Run with visible browser (for debugging)
HEADLESS_MODE=false python pipeline.py --mode once
```

## Output

Data files are saved in `./data/`:
- `pasardana_funds_YYYYMMDD_HHMMSS.csv` - Timestamped CSV
- `pasardana_funds_YYYYMMDD_HHMMSS.json` - Timestamped JSON
- `pasardana_funds_latest.csv` - Latest data
- `pasardana_funds_latest.json` - Latest data

## Troubleshooting

### Playwright Browser Issues
```bash
playwright install chromium
playwright install-deps chromium
```

### Permission Denied
```bash
chmod +x setup.sh
```

### Module Not Found
```bash
source venv/bin/activate
pip install -r requirements.txt
```

## Next Steps

1. Check the output in `./data/` directory
2. Review logs in `scraper.log` and `pipeline.log`
3. Customize settings in `.env` file
4. Set up automation (see README.md)

For detailed documentation, see [README.md](README.md)
