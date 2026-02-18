"""JSON extraction adapter for events embedded in HTML.

Use this when events are stored as JSON in a <script> tag in the HTML.
Common examples:
- Next.js __NEXT_DATA__
- React/Next.js server-side rendered data
- JSON-LD structured data

Example usage:
    from extractors.json_extractor import extract_events_from_page

    events = extract_events_from_page(html_content)
"""
import json
import logging
import re
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def extract_events_from_page(html: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract events from JSON embedded in HTML page.

    This is a template implementation. Customize based on your source's JSON structure.

    Args:
        html: HTML content containing JSON
        config: Configuration dict with extraction settings:
            - json_script_id: ID of script tag (default: "__NEXT_DATA__")
            - json_path: List of keys to navigate to events (default: ["props", "pageProps", "events"])
            - json_upcoming_key: Key for upcoming events (default: "upcoming")
            - json_past_key: Key for past events (default: "past")

    Returns:
        List of event dicts with at least: title, start_at, end_at, location, description, url, slug
    """
    script_id = config.get("json_script_id", "__NEXT_DATA__")
    json_path = config.get("json_path", ["props", "pageProps", "events"])
    upcoming_key = config.get("json_upcoming_key", "upcoming")
    past_key = config.get("json_past_key", "past")

    # Find JSON script tag
    pattern = rf'<script id="{re.escape(script_id)}" type="application/json">(.+?)</script>'
    match = re.search(pattern, html, re.DOTALL)
    if not match:
        logger.error(f"Could not find script tag with id '{script_id}'")
        return []

    # Parse JSON
    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON: {e}")
        return []

    # Navigate to events using json_path
    current = data
    for key in json_path:
        if not isinstance(current, dict):
            logger.error(f"Expected dict at path {json_path[:json_path.index(key)]}")
            return []
        current = current.get(key)
        if current is None:
            logger.warning(f"Path {json_path} not found in JSON")
            return []

    # Extract upcoming and past events
    if isinstance(current, dict):
        upcoming = current.get(upcoming_key, [])
        past = current.get(past_key, [])
    elif isinstance(current, list):
        # If path leads directly to a list
        upcoming = current
        past = []
    else:
        logger.error(f"Events data is not a dict or list: {type(current)}")
        return []

    # Ensure lists
    if not isinstance(upcoming, list):
        upcoming = []
    if not isinstance(past, list):
        past = []

    # Merge and deduplicate
    seen = set()
    merged = []
    for event in upcoming + past:
        if not isinstance(event, dict):
            continue

        # Use slug or id for deduplication
        identifier = event.get("slug") or event.get("id") or event.get("title")
        if identifier and identifier in seen:
            continue
        if identifier:
            seen.add(identifier)

        merged.append(event)

    logger.info(f"Extracted {len(merged)} events from JSON")
    return merged


def extract_event_from_detail_page(html: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Extract full event data from a detail page.

    Customize this based on your detail page structure.

    Args:
        html: HTML content of event detail page
        config: Configuration dict (same as extract_events_from_page)

    Returns:
        Event dict with enriched data, or empty dict if not found
    """
    script_id = config.get("json_script_id", "__NEXT_DATA__")
    detail_path = config.get("json_detail_path", ["props", "pageProps", "event"])

    # Find JSON script tag
    pattern = rf'<script id="{re.escape(script_id)}" type="application/json">(.+?)</script>'
    match = re.search(pattern, html, re.DOTALL)
    if not match:
        return {}

    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError:
        return {}

    # Navigate to event data
    current = data
    for key in detail_path:
        if not isinstance(current, dict):
            return {}
        current = current.get(key)
        if current is None:
            return {}

    if isinstance(current, dict):
        return current

    return {}
