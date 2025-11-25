# GitHub Actions Workflows

This directory contains GitHub Actions workflows for automating the Pasardana data scraper.

## Available Workflows

### 1. Main Scraper (`scraper.yml`)

**Purpose**: Scrapes Pasardana fund data on a schedule and stores results.

**Triggers**:
- **Schedule**: Daily at 9:00 AM UTC (adjustable)
- **Manual**: Via workflow_dispatch in GitHub Actions tab
- **Push**: When scraper code changes

**What it does**:
1. Sets up Python environment and dependencies
2. Installs Playwright browser
3. Runs the scraper
4. Uploads data as GitHub Actions artifacts (90-day retention)
5. Commits latest data to `data` branch
6. Generates run summary with statistics

**Artifacts**:
- `pasardana-data-{run_number}` - Scraped CSV and JSON files
- `scraper-logs-{run_number}` - Log files (30-day retention)

**Schedule customization**:
```yaml
schedule:
  - cron: '0 9 * * *'  # Daily at 9:00 AM UTC
```

Common cron schedules:
- `0 */6 * * *` - Every 6 hours
- `0 9,21 * * *` - Twice daily (9 AM and 9 PM UTC)
- `0 9 * * 1-5` - Weekdays only at 9 AM UTC
- `0 0 * * 0` - Weekly on Sundays at midnight UTC

### 2. Weekly Archive (`weekly-archive.yml`)

**Purpose**: Creates weekly archives of scraped data for long-term storage.

**Triggers**:
- **Schedule**: Weekly on Sundays at midnight UTC
- **Manual**: Via workflow_dispatch

**What it does**:
1. Checks out the `data` branch
2. Creates compressed archive of weekly data
3. Stores archives in `archives/` directory
4. Cleans up archives older than 12 weeks
5. Commits archives to `data` branch

**Artifacts**:
- `weekly-archive-{run_number}` - Compressed weekly archive

### 3. Test (`test.yml`)

**Purpose**: Tests scraper code on multiple Python versions.

**Triggers**:
- **Pull Request**: When Python files change
- **Manual**: Via workflow_dispatch

**What it does**:
1. Tests on Python 3.9, 3.10, 3.11, 3.12
2. Runs linting (flake8, pylint)
3. Validates imports
4. Tests scraper initialization

## Setup Instructions

### 1. Enable GitHub Actions

Ensure GitHub Actions is enabled for your repository:
- Go to repository **Settings** → **Actions** → **General**
- Under "Actions permissions", select "Allow all actions and reusable workflows"

### 2. Configure Branch Protection (Optional)

Create a `data` branch to store scraped data:

```bash
git checkout -b data
git push origin data
```

### 3. Set Schedule

Edit `.github/workflows/scraper.yml` to customize the schedule:

```yaml
on:
  schedule:
    - cron: '0 9 * * *'  # Modify this line
```

### 4. Manual Triggering

To run the scraper manually:
1. Go to **Actions** tab in GitHub
2. Select "Pasardana Data Scraper" workflow
3. Click "Run workflow"
4. Select options and click "Run workflow"

## Data Storage

### GitHub Actions Artifacts

- Automatically uploaded after each run
- Accessible from Actions tab → Workflow run → Artifacts
- Retention: 90 days (configurable)

### Data Branch

- Scraped data is committed to `data` branch
- `pasardana_funds_latest.csv` - Always current
- `pasardana_funds_latest.json` - Always current
- Timestamped files for last 30 days
- Weekly archives in `archives/` directory

### Accessing Data

**Via Git**:
```bash
git checkout data
cd data
```

**Via GitHub**:
- Browse files: `https://github.com/USERNAME/REPO/tree/data`
- Direct download: Use "Download" button or raw file links

**Via GitHub API**:
```bash
curl -H "Accept: application/vnd.github.v3.raw" \
     https://api.github.com/repos/USERNAME/REPO/contents/data/pasardana_funds_latest.csv?ref=data
```

## Monitoring

### Workflow Status

View workflow runs in the **Actions** tab:
- Green checkmark: Success
- Red X: Failure
- Yellow dot: In progress

### Notifications

Configure notifications in GitHub settings:
- **Settings** → **Notifications** → **Actions**
- Enable email/web notifications for workflow failures

### Status Badge

Add to README.md:

```markdown
![Scraper Status](https://github.com/USERNAME/REPO/actions/workflows/scraper.yml/badge.svg)
```

## Troubleshooting

### Workflow Not Running

1. **Check schedule**: Verify cron syntax is correct
2. **Check repository activity**: GitHub disables scheduled workflows after 60 days of no repository activity
3. **Check Actions settings**: Ensure workflows are enabled

### Authentication Issues

If workflow fails to push to `data` branch:
- GitHub Actions uses `GITHUB_TOKEN` automatically
- Check repository permissions in Settings → Actions → General → Workflow permissions
- Ensure "Read and write permissions" is selected

### Resource Limits

GitHub Actions free tier limits:
- 2,000 minutes/month for private repos
- Unlimited for public repos
- Each workflow run uses ~5-10 minutes

### Browser Issues

If Playwright fails:
- Ensure `playwright install-deps chromium` is included
- Check Ubuntu version compatibility
- Consider using `ubuntu-latest` runner

## Cost Optimization

### Reduce Frequency

```yaml
schedule:
  - cron: '0 9 * * 1'  # Weekly instead of daily
```

### Conditional Execution

Run only on weekdays:
```yaml
- name: Check if weekday
  id: check_day
  run: |
    if [ $(date +%u) -lt 6 ]; then
      echo "run=true" >> $GITHUB_OUTPUT
    fi

- name: Run scraper
  if: steps.check_day.outputs.run == 'true'
  run: python pipeline.py --mode once
```

### Self-Hosted Runner

For unlimited execution:
1. Set up self-hosted runner
2. Change workflow to use: `runs-on: self-hosted`

## Advanced Configuration

### Multiple Schedules

```yaml
on:
  schedule:
    - cron: '0 9 * * 1-5'   # Weekdays at 9 AM
    - cron: '0 0 * * 0'     # Sundays at midnight
```

### Environment Variables

Add secrets in **Settings** → **Secrets and variables** → **Actions**:

```yaml
- name: Run scraper
  env:
    CUSTOM_CONFIG: ${{ secrets.CUSTOM_CONFIG }}
  run: python pipeline.py --mode once
```

### Matrix Strategy

Test multiple configurations:
```yaml
strategy:
  matrix:
    schedule: ['morning', 'evening']
    format: ['csv', 'json']
```

## Workflow Files Reference

| File | Purpose | Schedule | Branch |
|------|---------|----------|--------|
| `scraper.yml` | Main data collection | Daily 9 AM UTC | Commits to `data` |
| `weekly-archive.yml` | Weekly archiving | Sunday midnight | Commits to `data` |
| `test.yml` | Code testing | On PR | N/A |

## Best Practices

1. **Test locally first**: Always test scraper changes locally before pushing
2. **Monitor runs**: Check Actions tab regularly for failures
3. **Review logs**: Download artifacts to debug issues
4. **Keep dependencies updated**: Regularly update `requirements.txt`
5. **Respect rate limits**: Don't schedule too frequently
6. **Archive data**: Use weekly archive workflow for backup

## Example Workflow Run

```
1. Scheduled trigger at 9:00 AM UTC
2. Setup Python 3.11
3. Install dependencies (cached)
4. Install Playwright
5. Run scraper (~2-5 minutes)
6. Upload artifacts
7. Commit to data branch
8. Generate summary
✓ Complete in ~5-8 minutes
```

## Support

For issues with workflows:
1. Check workflow logs in Actions tab
2. Review this documentation
3. Test locally with same Python version
4. Open issue with workflow run ID

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
- [Cron Syntax](https://crontab.guru/)
- [Playwright GitHub Actions](https://playwright.dev/docs/ci-intro)
