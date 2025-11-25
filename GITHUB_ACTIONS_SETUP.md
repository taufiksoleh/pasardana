# GitHub Actions Setup Guide

Quick reference for setting up automated scraping with GitHub Actions.

## ⚡ Quick Setup (3 Steps)

### 1. Push to GitHub

```bash
git push origin main
# Or your current branch
```

### 2. Enable GitHub Actions

1. Go to your repository on GitHub
2. Click **Settings** → **Actions** → **General**
3. Under "Actions permissions", select:
   - ✅ "Allow all actions and reusable workflows"
4. Under "Workflow permissions", select:
   - ✅ "Read and write permissions"
5. Click **Save**

### 3. That's It!

The scraper will now run automatically:
- **Daily** at 9:00 AM UTC
- **Manual** via Actions tab
- **On push** when scraper code changes

## 📅 Schedule Options

Edit `.github/workflows/scraper.yml` and change the cron expression:

### Common Schedules

```yaml
# Daily at 9:00 AM UTC
- cron: '0 9 * * *'

# Every 6 hours
- cron: '0 */6 * * *'

# Twice daily (9 AM and 9 PM UTC)
- cron: '0 9,21 * * *'

# Weekdays only at 9 AM
- cron: '0 9 * * 1-5'

# Weekly on Mondays at 9 AM
- cron: '0 9 * * 1'

# First day of every month
- cron: '0 9 1 * *'
```

**Use [crontab.guru](https://crontab.guru/) to create custom schedules**

## 🚀 Manual Trigger

Run the scraper anytime:

1. Go to **Actions** tab
2. Click "Pasardana Data Scraper"
3. Click **Run workflow** button
4. Select branch and log level
5. Click **Run workflow**

## 📊 Accessing Data

### Method 1: Download from Artifacts

1. Go to **Actions** tab
2. Click on a completed workflow run
3. Scroll to **Artifacts** section
4. Download `pasardana-data-{number}`

**Retention**: 90 days

### Method 2: Data Branch

The latest data is automatically committed to a `data` branch:

```bash
# Clone the data branch
git clone -b data https://github.com/USERNAME/REPO.git pasardana-data

# Or switch to data branch
git checkout data
cd data/
ls -lh
```

**Files**:
- `pasardana_funds_latest.csv` - Latest data (always updated)
- `pasardana_funds_latest.json` - Latest data (always updated)
- `pasardana_funds_YYYYMMDD_HHMMSS.*` - Timestamped files (last 30 days)

### Method 3: Direct Download

Download latest CSV directly:
```bash
curl -L -o pasardana.csv \
  "https://raw.githubusercontent.com/USERNAME/REPO/data/data/pasardana_funds_latest.csv"
```

Replace `USERNAME` and `REPO` with your GitHub username and repository name.

### Method 4: GitHub Web Interface

1. Browse to: `https://github.com/USERNAME/REPO/tree/data`
2. Navigate to `data/` directory
3. Click on file → **Download** button

## 🔔 Notifications

Get notified when scraper fails:

1. Go to GitHub **Settings** (your profile, not repo)
2. Click **Notifications**
3. Scroll to **Actions**
4. Enable:
   - ✅ "Send notifications for failed workflows"
   - ✅ Choose email or web notification

## 📈 Monitoring

### View Run History

1. Go to **Actions** tab
2. Click "Pasardana Data Scraper"
3. See list of all runs with status:
   - ✅ Green = Success
   - ❌ Red = Failed
   - 🟡 Yellow = In progress
   - ⚪ Gray = Cancelled/Skipped

### View Run Details

Click on any run to see:
- Run summary with statistics
- Step-by-step logs
- Artifacts (data files)
- Run duration and resource usage

### Add Status Badge

Add to top of README.md:

```markdown
![Scraper Status](https://github.com/USERNAME/REPO/actions/workflows/scraper.yml/badge.svg)
```

Shows real-time status: ![passing](https://img.shields.io/badge/build-passing-brightgreen) or ![failing](https://img.shields.io/badge/build-failing-red)

## 🐛 Troubleshooting

### Workflow Not Running

**Problem**: Scheduled workflow doesn't trigger

**Solutions**:
1. Check if Actions are enabled (Settings → Actions)
2. Verify cron syntax is correct
3. Push a commit (GitHub disables after 60 days of inactivity)
4. Check workflow file is on default branch

### Authentication Errors

**Problem**: "Permission denied" when pushing to data branch

**Solutions**:
1. Settings → Actions → General
2. Under "Workflow permissions":
   - Select "Read and write permissions"
   - Click Save
3. Re-run the workflow

### Browser Installation Fails

**Problem**: Playwright can't install browser

**Solutions**:
- Workflow already includes `playwright install-deps`
- Usually resolves automatically
- Check workflow logs for specific error

### Data Not Appearing

**Problem**: Workflow succeeds but no data saved

**Solutions**:
1. Check workflow logs for errors
2. Verify website is accessible
3. Run manually with DEBUG log level
4. Check if website structure changed

## 💰 Cost & Limits

### Free Tier (GitHub)

| Type | Limit |
|------|-------|
| **Public repos** | ♾️ Unlimited minutes |
| **Private repos** | 2,000 minutes/month |
| **Typical run** | ~5-8 minutes |
| **Daily runs** | ~150-240 min/month |

**Verdict**: Easily fits in free tier! ✅

### Reduce Usage

If needed, reduce frequency:

```yaml
# Weekly instead of daily
- cron: '0 9 * * 1'

# Weekdays only
- cron: '0 9 * * 1-5'
```

## ⚙️ Advanced Configuration

### Multiple Schedules

Run at different times:

```yaml
on:
  schedule:
    - cron: '0 9 * * *'   # Morning
    - cron: '0 21 * * *'  # Evening
```

### Environment Secrets

Add sensitive config:

1. Settings → Secrets and variables → Actions
2. Click **New repository secret**
3. Add name and value
4. Use in workflow:

```yaml
- name: Run scraper
  env:
    API_KEY: ${{ secrets.API_KEY }}
  run: python pipeline.py --mode once
```

### Conditional Execution

Run only on specific conditions:

```yaml
- name: Run scraper
  if: github.event_name == 'schedule'
  run: python pipeline.py --mode once
```

### Custom Outputs

Modify data storage location:

```yaml
- name: Run scraper
  env:
    DATA_OUTPUT_DIR: ./custom-data
  run: python pipeline.py --mode once
```

## 📝 Workflow Files

| File | Purpose | Trigger |
|------|---------|---------|
| `scraper.yml` | Daily scraping | Schedule, Manual, Push |
| `weekly-archive.yml` | Weekly backup | Weekly, Manual |
| `test.yml` | Code testing | Pull Request, Manual |

## 🎯 Best Practices

1. ✅ **Start with default schedule** - Adjust after monitoring
2. ✅ **Enable notifications** - Know when scraper fails
3. ✅ **Check logs regularly** - Catch issues early
4. ✅ **Test locally first** - Verify changes before pushing
5. ✅ **Use status badge** - Show scraper health in README
6. ✅ **Archive old data** - Use weekly-archive workflow
7. ✅ **Monitor usage** - Check Actions tab for minutes used

## 📚 Resources

- **Workflow Documentation**: [.github/workflows/README.md](.github/workflows/README.md)
- **Main README**: [README.md](README.md)
- **Quick Start**: [QUICKSTART.md](QUICKSTART.md)
- **GitHub Actions Docs**: https://docs.github.com/actions
- **Cron Helper**: https://crontab.guru/

## 🆘 Getting Help

1. Check workflow logs in Actions tab
2. Review [Troubleshooting](#-troubleshooting) section
3. Test locally with same Python version
4. Check if website structure changed
5. Open GitHub issue with workflow run ID

---

**Ready to go!** Once you push to GitHub and enable Actions, everything runs automatically. No servers, no maintenance! 🎉
