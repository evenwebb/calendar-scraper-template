"""Configuration file for calendar scraper.

Customize these settings for your specific event source.
Environment variables override these defaults (see .env.example).
"""
import os
from typing import Dict, List, Any

# ============================================================================
# SITE CONFIGURATION
# ============================================================================
# URL to scrape events from
EVENTS_URL = os.getenv("EVENTS_URL", "https://example.com/events")

# Base URL for building absolute URLs (e.g., for event detail pages)
BASE_URL = os.getenv("BASE_URL", "https://example.com")

# ============================================================================
# OUTPUT CONFIGURATION
# ============================================================================
# Directory where generated files will be written
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "docs")

# Filename for the generated iCalendar file (without .ics extension)
ICS_FILENAME = os.getenv("ICS_FILENAME", "calendar")

# Log file name
LOG_FILE = os.getenv("LOG_FILE", "scraper_log.txt")

# ============================================================================
# HTTP REQUEST SETTINGS
# ============================================================================
HTTP_TIMEOUT = int(os.getenv("HTTP_TIMEOUT", "60"))
HTTP_RETRIES = int(os.getenv("HTTP_RETRIES", "3"))
HTTP_RETRY_DELAY = 1
HTTP_RETRY_MULTIPLIER = 2
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/119.0.0.0 Safari/537.36"
)

# Delay between requests (seconds) - be respectful to the server
FETCH_DELAY_SEC = float(os.getenv("FETCH_DELAY_SEC", "0.5"))

# ============================================================================
# CACHE CONFIGURATION
# ============================================================================
# Cache file for event details (to avoid re-scraping unchanged data)
CACHE_FILE = os.getenv("CACHE_FILE", ".event_cache.json")

# How many days to keep cached entries
CACHE_EXPIRY_DAYS = int(os.getenv("CACHE_EXPIRY_DAYS", "7"))

# State file to detect new events (skip full scrape when no new events)
STATE_FILE = os.path.join(OUTPUT_DIR, ".last_upcoming.json")

# Health status file for monitoring
HEALTH_FILE = os.path.join(OUTPUT_DIR, ".health_status.json")

# ============================================================================
# ICALENDAR SETTINGS
# ============================================================================
ICAL_LINE_LENGTH = 75

# Calendar metadata
CALENDAR_NAME = "{{CALENDAR_NAME}}"  # e.g., "My Events Calendar"
CALENDAR_DESCRIPTION = "{{CALENDAR_DESCRIPTION}}"  # e.g., "Upcoming events from Example Site"
CALENDAR_PRODID = "-//{{ORGANIZATION}}//Events Calendar//EN"  # e.g., "-//MyOrg//Events Calendar//EN"

# UID domain for event UIDs (should be unique to your calendar)
UID_DOMAIN = "{{UID_DOMAIN}}"  # e.g., "example.com" or "mycalendar.github.io"

# ============================================================================
# NOTIFICATION SETTINGS
# ============================================================================
# Default time of day for notifications (24-hour format)
NOTIFICATION_TIME = "09:00"

# Calendar notification/alarm configuration
# Set 'enabled' to True and specify when you want reminders
NOTIFICATIONS: Dict[str, Any] = {
    "enabled": False,
    "alarms": [
        # Example: Remind 1 day before
        # {"days_before": 1, "description": "Event tomorrow"},
        # Example: Remind on event day at 9 AM
        # {"days_before": 0, "time": "09:00", "description": "Event today"},
    ],
}

# ============================================================================
# HTML GENERATION SETTINGS
# ============================================================================
# Site branding
SITE_NAME = "{{SITE_NAME}}"  # e.g., "Example Events"
SITE_TAGLINE = "{{SITE_TAGLINE}}"  # e.g., "Never miss an event"
SITE_DESCRIPTION = "{{SITE_DESCRIPTION}}"  # e.g., "Subscribe to Example events calendar"

# Colors (for HTML theme)
PRIMARY_COLOR = "#00d4ff"  # Main accent color
SECONDARY_COLOR = "#a855f7"  # Secondary accent color

# Author/attribution
AUTHOR_NAME = "{{AUTHOR_NAME}}"  # Your name or GitHub username
AUTHOR_URL = "{{AUTHOR_URL}}"  # Your website or GitHub profile URL

# GitHub Pages URL (if hosting on GitHub Pages)
GITHUB_PAGES_URL = "{{GITHUB_PAGES_URL}}"  # e.g., "https://username.github.io/repo-name"

# ============================================================================
# EXTRACTION CONFIGURATION
# ============================================================================
# Extraction method: "json", "html", "text", or "api"
# This determines which extractor to use (see extractors/ folder)
EXTRACTION_METHOD = "json"  # Change based on your source

# JSON extraction settings (if using JSON method)
JSON_SCRIPT_ID = "__NEXT_DATA__"  # ID of script tag containing JSON
JSON_PATH = ["props", "pageProps", "events"]  # Path to events in JSON
JSON_UPCOMING_KEY = "upcoming"  # Key for upcoming events
JSON_PAST_KEY = "past"  # Key for past events

# HTML extraction settings (if using HTML method)
# These are CSS selectors or BeautifulSoup find patterns
HTML_EVENT_CONTAINER = ".event"  # Container for each event
HTML_TITLE_SELECTOR = "h2"  # Selector for event title
HTML_DATE_SELECTOR = ".date"  # Selector for event date
HTML_LOCATION_SELECTOR = ".location"  # Selector for event location

# Text extraction settings (if using text method)
# Regex patterns for extracting event data
TEXT_DATE_PATTERN = r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})"  # e.g., "10 October 2025"
TEXT_TITLE_PATTERN = r"^(.+?)\s*-\s*"  # Pattern for event title

# API extraction settings (if using API method)
API_ENDPOINT = ""  # API endpoint URL
API_HEADERS: Dict[str, str] = {}  # Request headers (e.g., {"Authorization": "Bearer token"})
API_PARAMS: Dict[str, str] = {}  # Query parameters

# ============================================================================
# EVENT VALIDATION
# ============================================================================
# Required fields that each event must have
REQUIRED_EVENT_FIELDS = ["title", "start_at"]

# Optional: Field mappings if your source uses different field names
# Maps source field names to standard field names
FIELD_MAPPINGS: Dict[str, str] = {
    # "source_title": "title",
    # "source_start": "start_at",
    # "source_end": "end_at",
    # "source_location": "location",
}

# ============================================================================
# MULTIPLE SOURCE SUPPORT
# ============================================================================
# If scraping multiple sources (e.g., multiple locations), define them here
# Set to None or empty dict if only scraping one source
MULTIPLE_SOURCES: Dict[str, Dict[str, Any]] = {
    # Example:
    # "location1": {
    #     "enabled": True,
    #     "name": "Location 1",
    #     "url": "https://example.com/location1/events",
    #     "ics_filename": "location1.ics",
    # },
    # "location2": {
    #     "enabled": True,
    #     "name": "Location 2",
    #     "url": "https://example.com/location2/events",
    #     "ics_filename": "location2.ics",
    # },
}

# ============================================================================
# ADVANCED SETTINGS
# ============================================================================
# Skip full scrape if no new events detected (saves resources)
SKIP_IF_NO_NEW_EVENTS = True

# Include past events in calendar
INCLUDE_PAST_EVENTS = True

# Maximum number of events to process (0 = unlimited)
MAX_EVENTS = 0

# Timezone for events without timezone info (ISO format, e.g., "UTC", "Europe/London")
DEFAULT_TIMEZONE = "UTC"
