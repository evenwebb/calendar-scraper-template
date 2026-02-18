# Real-World Examples

Examples of calendar scrapers built using this template.

## Example 1: JSON Extraction (Next.js)

**Source**: Event website using Next.js with __NEXT_DATA__

**Key Features**:
- Extracts events from `__NEXT_DATA__` JSON
- Fetches detail pages for enriched data
- Handles timezone conversion
- Includes map coordinates

**Configuration**:
```python
EXTRACTION_METHOD = "json"
JSON_SCRIPT_ID = "__NEXT_DATA__"
JSON_PATH = ["props", "pageProps", "events"]
```

**Customizations**:
- Custom event categorization
- Region detection
- Ticket availability status
- Banner images in iCal

## Example 2: HTML Extraction (BeautifulSoup)

**Source**: Cinema listings website

**Key Features**:
- Parses HTML with BeautifulSoup
- Multiple cinema locations
- Film release date parsing
- Synopsis extraction

**Configuration**:
```python
EXTRACTION_METHOD = "html"
HTML_EVENT_CONTAINER = "div.content"
HTML_TITLE_SELECTOR = "h2"
```

**Customizations**:
- Multiple source support (4 cinema locations)
- Date parsing from text ("Expected: DD Month YYYY")
- Film detail page scraping
- Separate iCal files per location

## Example 3: Text Extraction (Regex)

**Source**: Meeting minutes or text-based calendar

**Key Features**:
- Line-by-line text parsing
- Regex pattern matching
- Date range handling

**Configuration**:
```python
EXTRACTION_METHOD = "text"
TEXT_DATE_PATTERN = r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})"
```

**Customizations**:
- Custom date format parsing
- Event type detection
- Multi-line event handling

## Example 4: API Extraction

**Source**: (Hypothetical REST API)

**Key Features**:
- REST API endpoint
- Authentication headers
- Pagination handling

**Configuration**:
```python
EXTRACTION_METHOD = "api"
API_ENDPOINT = "https://api.example.com/events"
API_HEADERS = {"Authorization": "Bearer TOKEN"}
```

**Customizations**:
- API response parsing
- Pagination support
- Rate limiting

## Common Patterns

### Handling Multiple Sources

```python
# In scraper.py main()
for source_id, source_config in config.MULTIPLE_SOURCES.items():
    if not source_config.get("enabled"):
        continue
    events = extract_from_source(source_config)
    generate_ics(events, source_config["ics_filename"])
```

### Custom Event Categorization

```python
def categorize_event(event):
    title = event.get("title", "").lower()
    if "meeting" in title:
        return "meeting"
    elif "workshop" in title:
        return "workshop"
    return "other"
```

### Date Parsing from Text

```python
from utils import parse_date_from_text

date_text = "Expected: 10 October 2025"
date_obj = parse_date_from_text(date_text)
if date_obj:
    event["start_at"] = date_obj.isoformat()
```

### Handling Timezones

```python
from datetime import timezone
import pytz

# Convert to UTC
local_tz = pytz.timezone("Europe/London")
dt = local_tz.localize(datetime(2025, 10, 10, 10, 0))
utc_dt = dt.astimezone(timezone.utc)
```

## Tips from Real Implementations

1. **Cache aggressively**: Cache detail pages for 7+ days to reduce requests
2. **Skip when no changes**: Compare event IDs/slugs to skip full scrape
3. **Handle errors gracefully**: Retry transient failures, log permanent ones
4. **Validate early**: Validate events as soon as extracted
5. **Test with real data**: Always test with actual website data before deploying
