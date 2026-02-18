# Template Customization Guide

Detailed guide for customizing the calendar scraper template for your specific event source.

## Table of Contents

1. [Configuration](#configuration)
2. [Extraction Methods](#extraction-methods)
3. [Event Validation](#event-validation)
4. [iCalendar Generation](#icalendar-generation)
5. [HTML Customization](#html-customization)
6. [Troubleshooting](#troubleshooting)

## Configuration

### Basic Settings (`config.py`)

#### Site URLs
```python
EVENTS_URL = "https://example.com/events"  # Main events page
BASE_URL = "https://example.com"            # Base URL for links
```

#### Calendar Metadata
```python
CALENDAR_NAME = "My Events Calendar"
CALENDAR_DESCRIPTION = "Upcoming events from Example Site"
CALENDAR_PRODID = "-//MyOrg//Events Calendar//EN"
UID_DOMAIN = "example.com"  # Must be unique
```

The `UID_DOMAIN` is used to generate unique event IDs. Use your domain or GitHub Pages URL.

## Extraction Methods

### JSON Extraction

Best for: Next.js sites, React SSR, JSON-LD structured data

**Configuration:**
```python
EXTRACTION_METHOD = "json"
JSON_SCRIPT_ID = "__NEXT_DATA__"  # ID of script tag
JSON_PATH = ["props", "pageProps", "events"]  # Path to events
JSON_UPCOMING_KEY = "upcoming"
JSON_PAST_KEY = "past"
```

**Customization:**
1. Inspect your page's HTML to find the JSON script tag
2. Update `JSON_SCRIPT_ID` if different
3. Navigate the JSON structure and update `JSON_PATH`
4. Adjust field mappings if your JSON uses different names

**Example JSON structure:**
```json
{
  "props": {
    "pageProps": {
      "events": {
        "upcoming": [...],
        "past": [...]
      }
    }
  }
}
```

### HTML Extraction

Best for: Traditional HTML pages, needs CSS selectors

**Requirements:** Uncomment `beautifulsoup4` in `requirements.txt`

**Configuration:**
```python
EXTRACTION_METHOD = "html"
HTML_EVENT_CONTAINER = ".event"        # Container for each event
HTML_TITLE_SELECTOR = "h2"             # Title selector
HTML_DATE_SELECTOR = ".date"          # Date selector
HTML_LOCATION_SELECTOR = ".location"  # Location selector
```

**Customization:**
1. Inspect your HTML structure
2. Update CSS selectors to match your page
3. Customize `extractors/html_extractor.py` for complex structures

### Text Extraction

Best for: Plain text, meeting minutes, simple lists

**Configuration:**
```python
EXTRACTION_METHOD = "text"
TEXT_DATE_PATTERN = r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})"
TEXT_TITLE_PATTERN = r"^(.+?)\s*-\s*"
```

**Customization:**
1. Write regex patterns matching your text format
2. Update `extractors/text_extractor.py` for complex parsing

### API Extraction

Best for: REST APIs, GraphQL endpoints

**Configuration:**
```python
EXTRACTION_METHOD = "api"
API_ENDPOINT = "https://api.example.com/events"
API_HEADERS = {"Authorization": "Bearer TOKEN"}
API_PARAMS = {"limit": 100}
```

**Customization:**
1. Update endpoint URL
2. Add authentication headers if needed
3. Set query parameters
4. Update `api_response_path` if events are nested

## Event Validation

Customize `validate_event_data()` in `scraper.py`:

```python
def validate_event_data(event: Dict[str, Any]) -> bool:
    # Required fields
    if not event.get("title"):
        return False
    if not event.get("start_at"):
        return False
    
    # Optional: Add your own validation
    # if not event.get("location"):
    #     return False
    
    return True
```

## iCalendar Generation

### Basic Event Fields

Events should have at minimum:
- `title` - Event title
- `start_at` - ISO 8601 datetime string
- `end_at` - ISO 8601 datetime string (optional)

### Additional Fields

You can add custom fields in `make_ics_event()`:

```python
# Location
if event.get("location"):
    lines.append(f"LOCATION:{event['location']}")

# GEO coordinates
lat, lon = event.get("map_latitude"), event.get("map_longitude")
if lat and lon:
    lines.append(f"GEO:{lat};{lon}")

# Organizer
if event.get("organizer_email"):
    lines.append(f"ORGANIZER:mailto:{event['organizer_email']}")
```

### Field Mappings

If your source uses different field names, add mappings in `config.py`:

```python
FIELD_MAPPINGS = {
    "source_title": "title",
    "source_start": "start_at",
    "source_end": "end_at",
}
```

Then apply mappings in your extractor.

## HTML Customization

### Colors

Update in `config.py`:
```python
PRIMARY_COLOR = "#00d4ff"    # Main accent
SECONDARY_COLOR = "#a855f7"  # Secondary accent
```

### Layout

Edit `html_templates.py`:
- Modify CSS in `<style>` tags
- Update HTML structure
- Add/remove features (search, filters, etc.)

### Branding

Update in `config.py`:
```python
SITE_NAME = "My Events"
SITE_TAGLINE = "Never miss an event"
AUTHOR_NAME = "Your Name"
AUTHOR_URL = "https://github.com/yourusername"
```

## Troubleshooting

### No Events Found

1. **Check URL**: Verify `EVENTS_URL` is correct
2. **Inspect HTML**: View page source, check for JSON/HTML structure
3. **Check logs**: Look at `scraper_log.txt` for errors
4. **Test extractor**: Run extractor function with sample HTML

### Events Missing Fields

1. **Check extraction**: Verify extractor is getting all fields
2. **Update validation**: Adjust `validate_event_data()` if too strict
3. **Field mappings**: Add mappings in `config.py` if names differ

### iCal File Invalid

1. **Check dates**: Ensure dates are valid ISO 8601 format
2. **Check UIDs**: Each event needs a unique UID
3. **Validate**: Use an iCal validator online

### GitHub Actions Fails

1. **Check logs**: View Actions tab for error messages
2. **Test locally**: Run `python scraper.py` locally first
3. **Dependencies**: Ensure all dependencies are in `requirements.txt`
4. **Permissions**: Verify workflow has `contents: write` permission

### HTML Not Updating

1. **Check GitHub Pages**: Verify Pages is enabled
2. **Check branch**: Ensure deploying from correct branch
3. **Check folder**: Verify deploying from `/docs` folder
4. **Clear cache**: Hard refresh browser (Ctrl+F5)

## Advanced Customization

### Multiple Sources

If scraping multiple locations/sources:

```python
# In config.py
MULTIPLE_SOURCES = {
    "location1": {
        "enabled": True,
        "name": "Location 1",
        "url": "https://example.com/location1/events",
        "ics_filename": "location1.ics",
    },
}
```

Then modify `scraper.py` to iterate over sources.

### Custom Categorization

Add event categorization:

```python
def categorize_event(event: Dict[str, Any]) -> str:
    title = event.get("title", "").lower()
    if "meeting" in title:
        return "meeting"
    elif "workshop" in title:
        return "workshop"
    return "other"
```

### Custom Notifications

Configure reminders:

```python
NOTIFICATIONS = {
    "enabled": True,
    "alarms": [
        {"days_before": 1, "description": "Event tomorrow"},
        {"days_before": 0, "time": "09:00", "description": "Event today"},
    ],
}
```

## Testing

### Local Testing

1. Run scraper: `python scraper.py`
2. Check output: Verify `docs/calendar.ics` and `docs/index.html`
3. Import iCal: Test in Google Calendar, Apple Calendar, etc.
4. View HTML: Open `docs/index.html` in browser

### Sample Data

Create test files in `tests/sample_data/`:
- `sample_page.html` - Example HTML page
- `sample_response.json` - Example API response

Use these to test extractors without hitting the live site.

## Best Practices

1. **Be respectful**: Add delays between requests (`FETCH_DELAY_SEC`)
2. **Cache wisely**: Use caching to avoid re-scraping unchanged data
3. **Handle errors**: Implement retry logic and error handling
4. **Log everything**: Use logging for debugging
5. **Test thoroughly**: Test with real data before deploying
6. **Document changes**: Update README with your customizations

## Getting Help

- Check `scraper_log.txt` for detailed error messages
- Review extractor examples in `extractors/` folder
- See `EXAMPLES.md` for real-world implementations
- Test with sample data before going live
