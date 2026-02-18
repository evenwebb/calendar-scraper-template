# Quick Start Guide

Get your calendar scraper running in 5 minutes.

## Step 1: Copy the Template

```bash
cp -r calendar-scraper-template my-calendar-scraper
cd my-calendar-scraper
```

## Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 3: Configure Your Scraper

Edit `config.py` and update these essential settings:

```python
# Site Configuration
EVENTS_URL = "https://example.com/events"  # Your events page URL
BASE_URL = "https://example.com"            # Base URL for building links

# Calendar Metadata
CALENDAR_NAME = "My Events Calendar"
CALENDAR_DESCRIPTION = "Upcoming events from Example Site"
UID_DOMAIN = "example.com"  # Unique domain for event UIDs

# Site Branding
SITE_NAME = "Example Events"
SITE_TAGLINE = "Never miss an event"
```

## Step 4: Choose Your Extraction Method

### Option A: JSON in HTML (e.g., Next.js __NEXT_DATA__)

```python
# In config.py
EXTRACTION_METHOD = "json"
JSON_SCRIPT_ID = "__NEXT_DATA__"
JSON_PATH = ["props", "pageProps", "events"]
```

### Option B: HTML Parsing (BeautifulSoup)

```python
# In config.py
EXTRACTION_METHOD = "html"
HTML_EVENT_CONTAINER = ".event"  # CSS selector for event container
HTML_TITLE_SELECTOR = "h2"       # Selector for title
```

**Note**: Uncomment `beautifulsoup4` in `requirements.txt` if using HTML extraction.

### Option C: Text/Regex Parsing

```python
# In config.py
EXTRACTION_METHOD = "text"
TEXT_DATE_PATTERN = r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})"
```

### Option D: REST API

```python
# In config.py
EXTRACTION_METHOD = "api"
API_ENDPOINT = "https://api.example.com/events"
API_HEADERS = {"Authorization": "Bearer YOUR_TOKEN"}
```

## Step 5: Customize Extraction (If Needed)

Edit the appropriate extractor file in `extractors/` to match your data structure.

For JSON extraction, edit `extractors/json_extractor.py`:
- Update `json_path` if events are nested differently
- Adjust field mappings if your JSON uses different field names

## Step 6: Test Your Scraper

```bash
python scraper.py
```

Check the `docs/` folder for generated files:
- `calendar.ics` - Your iCalendar file
- `index.html` - Calendar page

## Step 7: Deploy to GitHub Pages

1. Create a new GitHub repository
2. Push your code
3. Go to Settings → Pages
4. Deploy from `main` branch, `/docs` folder
5. Your calendar will be at `https://username.github.io/repo-name/`

## Step 8: Set Up GitHub Actions

The workflow in `.github/workflows/scrape.yml` will automatically update your calendar weekly.

Edit the schedule if needed:
```yaml
schedule:
  - cron: '0 9 * * 1'  # Every Monday at 9 AM UTC
```

## Troubleshooting

**No events found?**
- Check that `EVENTS_URL` is correct
- Verify your extraction method matches the page structure
- Look at `scraper_log.txt` for errors

**Events missing fields?**
- Customize `validate_event_data()` in `scraper.py`
- Update field mappings in `config.py`

**HTML looks wrong?**
- Customize `html_templates.py` with your branding
- Update colors in `config.py`

## Next Steps

- Read [TEMPLATE_GUIDE.md](TEMPLATE_GUIDE.md) for advanced customization
- Check [EXAMPLES.md](EXAMPLES.md) for inspiration
- Use `.template_checklist.md` to track your progress
