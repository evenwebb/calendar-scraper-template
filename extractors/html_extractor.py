"""HTML extraction adapter using BeautifulSoup.

Use this when events are in HTML format and need to be parsed with CSS selectors.

Requires: beautifulsoup4 (add to requirements.txt)

Example usage:
    from extractors.html_extractor import extract_events_from_page

    events = extract_events_from_page(html_content, config)
"""
import logging
from typing import Any, Dict, List

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None
    logging.warning("BeautifulSoup4 not installed. Install with: pip install beautifulsoup4")

logger = logging.getLogger(__name__)


def extract_events_from_page(html: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract events from HTML using BeautifulSoup.

    Customize the selectors based on your HTML structure.

    Args:
        html: HTML content
        config: Configuration dict with extraction settings:
            - html_event_container: CSS selector for event container (default: ".event")
            - html_title_selector: Selector for title (default: "h2")
            - html_date_selector: Selector for date (default: ".date")
            - html_location_selector: Selector for location (default: ".location")
            - html_description_selector: Selector for description (default: ".description")
            - html_url_selector: Selector for event URL (default: "a")

    Returns:
        List of event dicts
    """
    if BeautifulSoup is None:
        logger.error("BeautifulSoup4 is required for HTML extraction")
        return []

    soup = BeautifulSoup(html, "html.parser")

    # Get selectors from config
    container_selector = config.get("html_event_container", ".event")
    title_selector = config.get("html_title_selector", "h2")
    date_selector = config.get("html_date_selector", ".date")
    location_selector = config.get("html_location_selector", ".location")
    description_selector = config.get("html_description_selector", ".description")
    url_selector = config.get("html_url_selector", "a")

    events = []
    event_containers = soup.select(container_selector)

    for container in event_containers:
        event = {}

        # Extract title
        title_elem = container.select_one(title_selector)
        if title_elem:
            event["title"] = title_elem.get_text(strip=True)

        # Extract date
        date_elem = container.select_one(date_selector)
        if date_elem:
            event["date_text"] = date_elem.get_text(strip=True)
            # You'll need to parse this into start_at/end_at
            # See utils.parse_date_from_text() for help

        # Extract location
        location_elem = container.select_one(location_selector)
        if location_elem:
            event["location"] = location_elem.get_text(strip=True)

        # Extract description
        desc_elem = container.select_one(description_selector)
        if desc_elem:
            event["description"] = desc_elem.get_text(strip=True)

        # Extract URL
        url_elem = container.select_one(url_selector)
        if url_elem:
            href = url_elem.get("href", "")
            base_url = config.get("base_url", "")
            if href:
                if href.startswith("http"):
                    event["url"] = href
                else:
                    event["url"] = f"{base_url.rstrip('/')}/{href.lstrip('/')}"

        # Only add if we have at least a title
        if event.get("title"):
            events.append(event)

    logger.info(f"Extracted {len(events)} events from HTML")
    return events


def extract_event_from_detail_page(html: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Extract full event data from a detail page.

    Customize selectors based on your detail page structure.

    Args:
        html: HTML content of event detail page
        config: Configuration dict (same as extract_events_from_page)

    Returns:
        Event dict with enriched data
    """
    if BeautifulSoup is None:
        return {}

    soup = BeautifulSoup(html, "html.parser")
    event = {}

    # Customize these selectors for your detail page
    # Example:
    # title_elem = soup.select_one("h1.event-title")
    # if title_elem:
    #     event["title"] = title_elem.get_text(strip=True)

    # description_elem = soup.select_one(".event-description")
    # if description_elem:
    #     event["description"] = description_elem.get_text(strip=True)

    return event
