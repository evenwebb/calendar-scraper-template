"""Calendar Scraper Template.

Scrapes events from a website and generates an iCalendar file.

CUSTOMIZATION REQUIRED:
1. Import and configure the appropriate extractor in extract_events_from_page()
2. Customize validate_event_data() for your event structure
3. Update make_ics_event() if your events have special fields
4. Customize HTML generation in html_templates.py
5. Update config.py with your site-specific settings

See TEMPLATE_GUIDE.md for detailed customization instructions.
"""
import datetime
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

import config
from utils import (
    escape_and_fold_ical_text,
    format_ical_datetime,
    parse_iso_datetime,
    strip_html,
)

# Import extractor based on config
if config.EXTRACTION_METHOD == "json":
    from extractors.json_extractor import extract_events_from_page, extract_event_from_detail_page
elif config.EXTRACTION_METHOD == "html":
    from extractors.html_extractor import extract_events_from_page, extract_event_from_detail_page
elif config.EXTRACTION_METHOD == "text":
    from extractors.text_extractor import extract_events_from_page, extract_event_from_detail_page
elif config.EXTRACTION_METHOD == "api":
    from extractors.api_extractor import extract_events_from_api, extract_event_from_api as extract_event_detail_from_api
    # For API, we don't have a page to extract from
    def extract_events_from_page(html: str, cfg: Dict[str, Any]) -> List[Dict[str, Any]]:
        return extract_events_from_api(cfg)
    def extract_event_from_detail_page(html: str, cfg: Dict[str, Any]) -> Dict[str, Any]:
        return {}
else:
    raise ValueError(f"Unknown extraction method: {config.EXTRACTION_METHOD}")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
error_handler = logging.FileHandler(config.LOG_FILE)
error_handler.setLevel(logging.ERROR)
logger.addHandler(error_handler)
ICAL_NEWLINE = "\r\n"


# ============================================================================
# HTTP REQUEST HELPERS
# ============================================================================

def fetch_with_retries(
    url: str,
    retries: int = config.HTTP_RETRIES,
    timeout: int = config.HTTP_TIMEOUT,
) -> requests.Response:
    """Return HTTP response, retrying with exponential backoff on errors."""
    headers = {"User-Agent": config.USER_AGENT}
    delay = config.HTTP_RETRY_DELAY

    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.RequestException as exc:
            logger.warning("Attempt %d failed: %s", attempt + 1, exc)
            if attempt == retries - 1:
                raise
            time.sleep(delay)
            delay *= config.HTTP_RETRY_MULTIPLIER

    raise requests.RequestException("All retries exhausted")


# ============================================================================
# EVENT VALIDATION
# ============================================================================

def validate_event_data(event: Dict[str, Any]) -> bool:
    """Validate that event dict has minimum required fields.

    CUSTOMIZE THIS based on your event structure.

    Args:
        event: Event dictionary to validate

    Returns:
        True if event has required fields, False otherwise
    """
    # Must have at least a title
    if not event.get("title"):
        logger.warning("Event missing title: %s", event)
        return False

    # Must have a start time
    if not event.get("start_at"):
        logger.warning("Event %s missing start_at", event.get("title"))
        return False

    # Add your own validation rules here
    # Example:
    # if not event.get("location"):
    #     logger.warning("Event %s missing location", event.get("title"))
    #     return False

    return True


# ============================================================================
# CACHE MANAGEMENT
# ============================================================================

def load_cache() -> Dict[str, dict]:
    """Load event detail cache from disk. Drops expired entries."""
    if not os.path.exists(config.CACHE_FILE):
        return {}
    try:
        with open(config.CACHE_FILE, "r", encoding="utf-8") as f:
            cache = json.load(f)
        cutoff = (
            datetime.datetime.now() - datetime.timedelta(days=config.CACHE_EXPIRY_DAYS)
        ).isoformat()
        cache = {k: v for k, v in cache.items() if v.get("cached_at", "") > cutoff}
        logger.info("Loaded event cache with %d entries", len(cache))
        return cache
    except (json.JSONDecodeError, OSError) as e:
        logger.warning("Cache load failed: %s", e)
        return {}


def save_cache(cache: Dict[str, dict]) -> None:
    """Save event detail cache to disk."""
    try:
        with open(config.CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
        logger.info("Saved event cache with %d entries", len(cache))
    except OSError as e:
        logger.warning("Cache save failed: %s", e)


# ============================================================================
# STATE MANAGEMENT
# ============================================================================

def load_last_upcoming_slugs() -> set:
    """Load the set of upcoming event slugs from last run."""
    if not os.path.exists(config.STATE_FILE):
        return set()
    try:
        with open(config.STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        slugs = data.get("slugs", [])
        return set(slugs) if isinstance(slugs, list) else set()
    except (json.JSONDecodeError, OSError):
        return set()


def save_last_upcoming_slugs(slugs: List[str]) -> None:
    """Save the current upcoming event slugs for next run comparison."""
    Path(config.OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    try:
        with open(config.STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(
                {"slugs": slugs, "updated": datetime.datetime.now().isoformat()},
                f,
                indent=2,
            )
        logger.info("Saved state with %d upcoming slugs", len(slugs))
    except OSError as e:
        logger.warning("State save failed: %s", e)


def has_new_events(current_slugs: set, previous_slugs: set) -> bool:
    """True if there is at least one event in current that was not in previous."""
    return bool(current_slugs - previous_slugs)


# ============================================================================
# HEALTH STATUS
# ============================================================================

def save_health_status(
    status: str,
    event_count: int,
    message: str = "",
    error: Optional[str] = None
) -> None:
    """Save health status for monitoring and display."""
    Path(config.OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    health_data = {
        "status": status,
        "last_update": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "event_count": event_count,
        "message": message,
        "error": error,
    }
    try:
        with open(config.HEALTH_FILE, "w", encoding="utf-8") as f:
            json.dump(health_data, f, indent=2)
        logger.info("Saved health status: %s", status)
    except OSError as e:
        logger.warning("Health status save failed: %s", e)


def load_health_status() -> Optional[Dict[str, Any]]:
    """Load health status from disk."""
    if not os.path.exists(config.HEALTH_FILE):
        return None
    try:
        with open(config.HEALTH_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


# ============================================================================
# EVENT DETAIL FETCHING
# ============================================================================

def fetch_event_detail(identifier: str, cache: Dict[str, dict]) -> Optional[Dict[str, Any]]:
    """Fetch event detail from its page. Uses cache if available and not expired.

    CUSTOMIZE THIS based on how your site structures detail pages.

    Args:
        identifier: Event identifier (slug, id, etc.)
        cache: Cache dict to read/write

    Returns:
        Merged event dict with detail page data, or None on failure.
    """
    if not identifier:
        return None

    if identifier in cache:
        entry = {k: v for k, v in cache[identifier].items() if k != "cached_at"}
        logger.info("Using cached detail for: %s", identifier)
        return entry

    # Build detail URL - CUSTOMIZE THIS
    # Example: url = f"{config.BASE_URL}/events/{identifier}"
    url = f"{config.BASE_URL}/events/{identifier}"

    try:
        time.sleep(config.FETCH_DELAY_SEC)
        response = fetch_with_retries(url)
        
        # Extract detail based on extraction method
        if config.EXTRACTION_METHOD == "api":
            detail = extract_event_detail_from_api(identifier, {
                "api_detail_endpoint": f"{config.BASE_URL}/api/events/{{id}}",
                "api_headers": config.API_HEADERS,
            })
        else:
            detail = extract_event_from_detail_page(response.text, {
                "json_script_id": config.JSON_SCRIPT_ID,
                "json_detail_path": config.JSON_PATH + ["event"],
                "base_url": config.BASE_URL,
            })

        if detail:
            cache[identifier] = {**detail, "cached_at": datetime.datetime.now().isoformat()}
            logger.info("Fetched detail for: %s", identifier)
            return detail
    except requests.RequestException as e:
        logger.warning("Failed to fetch event detail %s: %s", identifier, e)
    return None


def merge_event_detail(
    list_event: Dict[str, Any], detail_event: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """Merge detail page data into list event. Detail overrides where richer.

    CUSTOMIZE THIS to merge fields specific to your events.
    """
    if not detail_event:
        return list_event
    merged = dict(list_event)
    
    # Prefer detail page for description (often fuller)
    if detail_event.get("description"):
        merged["description"] = detail_event["description"]
    
    # Prefer detail location if list is empty
    if detail_event.get("location") and not merged.get("location"):
        merged["location"] = detail_event["location"]
    
    # Merge other fields - CUSTOMIZE based on your event structure
    # Example:
    # if detail_event.get("map_latitude") is not None:
    #     merged["map_latitude"] = detail_event["map_latitude"]
    # if detail_event.get("map_longitude") is not None:
    #     merged["map_longitude"] = detail_event["map_longitude"]
    
    # Copy all other fields from detail
    for key, value in detail_event.items():
        if value is not None and key not in ["cached_at"]:
            merged[key] = value
    
    return merged


# ============================================================================
# ICALENDAR GENERATION
# ============================================================================

def generate_alarm(alarm_config: Dict[str, Any], event_start: datetime.datetime) -> str:
    """Generate a VALARM component for iCalendar using RFC 5545 duration format."""
    days = alarm_config.get("days_before", 1)
    time_str = alarm_config.get("time", config.NOTIFICATION_TIME)
    time_parts = time_str.split(":")
    hours = int(time_parts[0])
    minutes = int(time_parts[1]) if len(time_parts) > 1 else 0

    if days == 0:
        # On event day - use hours before if time is specified
        event_hour = event_start.hour if hasattr(event_start, 'hour') else 0
        event_minute = event_start.minute if hasattr(event_start, 'minute') else 0

        hours_before = event_hour - hours
        minutes_before = event_minute - minutes

        if hours_before < 0 or (hours_before == 0 and minutes_before <= 0):
            trigger_line = "TRIGGER:-PT1H"
        else:
            total_minutes = hours_before * 60 + minutes_before
            if total_minutes >= 60:
                trigger_line = f"TRIGGER:-PT{total_minutes // 60}H"
            else:
                trigger_line = f"TRIGGER:-PT{total_minutes}M"
    else:
        trigger_line = f"TRIGGER:-P{days}D"

    description = alarm_config.get("description", "Event Reminder")
    alarm_lines = [
        "BEGIN:VALARM",
        "ACTION:DISPLAY",
        escape_and_fold_ical_text(description, "DESCRIPTION:", config.ICAL_LINE_LENGTH),
        trigger_line,
        "END:VALARM",
        "",
    ]
    return ICAL_NEWLINE.join(alarm_lines)


def make_ics_event(event: Dict[str, Any]) -> str:
    """Return an iCalendar VEVENT string for an event.

    CUSTOMIZE THIS to handle fields specific to your events.

    Args:
        event: Event dictionary

    Returns:
        iCalendar VEVENT string
    """
    title = event.get("title", "Untitled Event")
    start_at = event.get("start_at")
    end_at = event.get("end_at")
    location = event.get("location", "")
    description_raw = event.get("description", "")
    slug = event.get("slug", "")
    url = event.get("url", "")
    event_id = event.get("id")

    # Build event URL
    if slug:
        event_url = f"{config.BASE_URL}/events/{slug}"
    elif url:
        event_url = url
    else:
        event_url = ""

    start_dt = parse_iso_datetime(start_at)
    end_dt = parse_iso_datetime(end_at)

    if not start_dt:
        logger.warning("Skipping event %s: no valid start time", title)
        return ""

    # Use end_dt if valid, otherwise default to start + 1 hour
    if end_dt and end_dt > start_dt:
        end_dt_use = end_dt
    else:
        end_dt_use = start_dt + datetime.timedelta(hours=1)

    # Format for iCal: convert to UTC
    if start_dt.tzinfo:
        start_utc = start_dt.astimezone(datetime.timezone.utc)
        end_utc = end_dt_use.astimezone(datetime.timezone.utc)
        start_str = start_utc.strftime("%Y%m%dT%H%M%SZ")
        end_str = end_utc.strftime("%Y%m%dT%H%M%SZ")
    else:
        start_str = start_dt.strftime("%Y%m%dT%H%M%S")
        end_str = end_dt_use.strftime("%Y%m%dT%H%M%S")

    # Build description
    description = strip_html(description_raw)
    desc_parts = [description] if description else []
    if event_url:
        desc_parts.append(f"\nEvent details: {event_url}")
    description_text = "\n".join(desc_parts)

    # UID (required): stable unique identifier
    uid = f"{event_id or slug}@{config.UID_DOMAIN}" if (event_id or slug) else None
    if not uid:
        uid = f"{start_str}-{slug or title[:20]}@{config.UID_DOMAIN}"

    # DTSTAMP (required): when the event was created/updated
    dtstamp_str = format_ical_datetime(datetime.datetime.now(datetime.timezone.utc))
    updated_at = event.get("updated_at")
    if updated_at:
        upd_dt = parse_iso_datetime(updated_at)
        if upd_dt:
            dtstamp_str = format_ical_datetime(upd_dt)

    # Build VEVENT
    summary_line = escape_and_fold_ical_text(title, "SUMMARY:", config.ICAL_LINE_LENGTH)
    description_line = escape_and_fold_ical_text(
        description_text,
        "DESCRIPTION:",
        config.ICAL_LINE_LENGTH,
    )
    lines = [
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{dtstamp_str}",
        f"DTSTART:{start_str}",
        f"DTEND:{end_str}",
        summary_line,
        description_line,
    ]

    # LOCATION
    if location:
        lines.append(
            escape_and_fold_ical_text(location, "LOCATION:", config.ICAL_LINE_LENGTH)
        )

    # URL
    if event_url:
        lines.append(
            escape_and_fold_ical_text(event_url, "URL:", config.ICAL_LINE_LENGTH)
        )

    # GEO (if coordinates available) - CUSTOMIZE if your events have coordinates
    lat, lon = event.get("map_latitude"), event.get("map_longitude")
    if lat is not None and lon is not None:
        try:
            lines.append(f"GEO:{float(lat)};{float(lon)}")
        except (TypeError, ValueError):
            pass

    # STATUS
    lines.append("STATUS:CONFIRMED")

    # VALARMs (nested components)
    if config.NOTIFICATIONS.get("enabled", False):
        for alarm in config.NOTIFICATIONS.get("alarms", []):
            lines.extend(
                line for line in generate_alarm(alarm, start_dt).splitlines() if line.strip()
            )

    lines.append("END:VEVENT")
    return ICAL_NEWLINE.join(lines) + ICAL_NEWLINE


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main() -> None:
    """Main function to scrape events and generate iCal file."""
    try:
        logger.info("Fetching events from %s", config.EVENTS_URL)
        
        # Fetch events based on extraction method
        if config.EXTRACTION_METHOD == "api":
            events = extract_events_from_api({
                "api_endpoint": config.API_ENDPOINT,
                "api_headers": config.API_HEADERS,
                "api_params": config.API_PARAMS,
                "api_response_path": config.JSON_PATH,
            })
        else:
            response = fetch_with_retries(config.EVENTS_URL)
            events = extract_events_from_page(response.text, {
                "json_script_id": config.JSON_SCRIPT_ID,
                "json_path": config.JSON_PATH,
                "json_upcoming_key": config.JSON_UPCOMING_KEY,
                "json_past_key": config.JSON_PAST_KEY,
                "base_url": config.BASE_URL,
                "html_event_container": config.HTML_EVENT_CONTAINER,
                "html_title_selector": config.HTML_TITLE_SELECTOR,
                "html_date_selector": config.HTML_DATE_SELECTOR,
                "html_location_selector": config.HTML_LOCATION_SELECTOR,
                "text_date_pattern": config.TEXT_DATE_PATTERN,
                "text_title_pattern": config.TEXT_TITLE_PATTERN,
            })

        # Validate events
        valid_events = [e for e in events if validate_event_data(e)]
        invalid_count = len(events) - len(valid_events)
        if invalid_count > 0:
            logger.warning("Skipped %d invalid events", invalid_count)
        events = valid_events

        if not events:
            logger.warning("No events found")
            print("No events found.")
            save_health_status(
                "error",
                0,
                "No events found on website",
                "Event extraction returned empty list"
            )
            return
    except Exception as e:
        logger.error("Failed to fetch or parse events: %s", e)
        save_health_status(
            "error",
            0,
            "Failed to fetch events from website",
            str(e)
        )
        sys.exit(1)

    # Split into future and past
    today = datetime.datetime.now(datetime.timezone.utc)
    future_events = []
    past_events = []
    for e in events:
        start = parse_iso_datetime(e.get("start_at"))
        if start:
            if start.tzinfo is None:
                start = start.replace(tzinfo=datetime.timezone.utc)
            if start >= today:
                future_events.append(e)
            else:
                past_events.append(e)
        else:
            future_events.append(e)  # No start = treat as future

    # Skip full scrape if no NEW upcoming events
    if config.SKIP_IF_NO_NEW_EVENTS:
        current_upcoming_slugs = {e.get("slug") or e.get("id") or e.get("title") for e in future_events}
        previous_slugs = load_last_upcoming_slugs()
        if not has_new_events(current_upcoming_slugs, previous_slugs):
            logger.info("No new events (current=%d, previous=%d), skipping full scrape", 
                       len(current_upcoming_slugs), len(previous_slugs))
            print("No new events. Skipping update.")
            save_last_upcoming_slugs(list(current_upcoming_slugs))
            save_health_status(
                "success",
                len(current_upcoming_slugs),
                f"No new events detected ({len(current_upcoming_slugs)} upcoming events)"
            )
            return

    # All events to output
    all_events = (past_events if config.INCLUDE_PAST_EVENTS else []) + future_events
    all_events.sort(key=lambda x: parse_iso_datetime(x.get("start_at", "")) or datetime.datetime.min.replace(tzinfo=datetime.timezone.utc))

    # Fetch detail pages and merge
    cache = load_cache()
    enriched_events = []
    for event in all_events:
        identifier = event.get("slug") or event.get("id")
        detail = fetch_event_detail(identifier, cache) if identifier else None
        enriched_events.append(merge_event_detail(event, detail))
    save_cache(cache)

    Path(config.OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    # Generate iCal
    event_lines = []
    for event in enriched_events[:config.MAX_EVENTS if config.MAX_EVENTS > 0 else len(enriched_events)]:
        ical = make_ics_event(event)
        if ical:
            event_lines.append(ical)

    ical_content = (
        ICAL_NEWLINE.join(
            [
                "BEGIN:VCALENDAR",
                "VERSION:2.0",
                f"PRODID:{config.CALENDAR_PRODID}",
                "CALSCALE:GREGORIAN",
                "METHOD:PUBLISH",
                f"X-WR-CALNAME:{config.CALENDAR_NAME}",
                f"X-WR-CALDESC:{config.CALENDAR_DESCRIPTION}",
                f"X-WR-TIMEZONE:{config.DEFAULT_TIMEZONE}",
            ]
        )
        + ICAL_NEWLINE
        + "".join(event_lines)
        + f"END:VCALENDAR{ICAL_NEWLINE}"
    )

    ics_path = Path(config.OUTPUT_DIR) / f"{config.ICS_FILENAME}.ics"
    ics_path.write_text(ical_content, encoding="utf-8")
    logger.info("Wrote %s (%d events)", ics_path, len(event_lines))

    # Save state
    current_upcoming_slugs = {e.get("slug") or e.get("id") or e.get("title") for e in future_events}
    save_last_upcoming_slugs(list(current_upcoming_slugs))

    # Save health status
    save_health_status(
        "success",
        len(event_lines),
        f"Successfully processed {len(event_lines)} events ({len(current_upcoming_slugs)} upcoming)"
    )

    # Generate HTML pages (import from html_templates)
    try:
        from html_templates import build_index_html, build_archive_html
        
        health_status = load_health_status()
        index_path = Path(config.OUTPUT_DIR) / "index.html"
        index_path.write_text(
            build_index_html(enriched_events, upcoming_count=len(current_upcoming_slugs), health_status=health_status),
            encoding="utf-8"
        )
        logger.info("Wrote %s", index_path)

        if config.INCLUDE_PAST_EVENTS:
            past_enriched = [e for e in enriched_events 
                           if parse_iso_datetime(e.get("start_at")) and 
                           parse_iso_datetime(e.get("start_at")).replace(tzinfo=datetime.timezone.utc) < today]
            archive_path = Path(config.OUTPUT_DIR) / "archive.html"
            archive_path.write_text(build_archive_html(past_enriched), encoding="utf-8")
            logger.info("Wrote %s with %d past events", archive_path, len(past_enriched))
    except ImportError:
        logger.warning("html_templates module not found, skipping HTML generation")

    print(f"\n✓ Created {config.OUTPUT_DIR}/ with {config.ICS_FILENAME}.ics ({len(event_lines)} events)\n")
    for event in enriched_events[:10]:  # Show first 10
        start = parse_iso_datetime(event.get("start_at"))
        date_str = start.strftime("%d %B %Y %H:%M") if start else "?"
        print(f"  • {event.get('title')} – {date_str} @ {event.get('location', 'TBC')}")


if __name__ == "__main__":
    main()
