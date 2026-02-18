"""Text/regex extraction adapter for plain text or line-based formats.

Use this when events are in plain text format (e.g., meeting minutes, lists)
and need to be parsed with regex patterns.

Example usage:
    from extractors.text_extractor import extract_events_from_page

    events = extract_events_from_page(text_content, config)
"""
import datetime
import logging
import re
from typing import Any, Dict, List

from utils import parse_date_from_text, parse_time_from_text

logger = logging.getLogger(__name__)


def extract_events_from_page(text: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract events from plain text using regex patterns.

    Customize the patterns based on your text format.

    Args:
        text: Plain text content
        config: Configuration dict with extraction settings:
            - text_date_pattern: Regex pattern for dates (default: r"(\\d{1,2})\\s+([A-Za-z]+)\\s+(\\d{4})")
            - text_title_pattern: Regex pattern for titles (default: r"^(.+?)\\s*-\\s*")
            - text_line_pattern: Regex pattern for entire event line (optional)
            - base_url: Base URL for building absolute URLs

    Returns:
        List of event dicts
    """
    date_pattern = config.get("text_date_pattern", r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})")
    title_pattern = config.get("text_title_pattern", r"^(.+?)\s*-\s*")
    line_pattern = config.get("text_line_pattern", None)
    base_url = config.get("base_url", "")

    events = []
    lines = text.split("\n")

    # If a line pattern is provided, use it
    if line_pattern:
        for line in lines:
            match = re.search(line_pattern, line)
            if match:
                event = {}
                # Extract groups from match
                # Customize based on your pattern
                # Example:
                # event["title"] = match.group(1)
                # event["date_text"] = match.group(2)
                # event["location"] = match.group(3)
                if event.get("title"):
                    events.append(event)
    else:
        # Parse line by line looking for date patterns
        current_event = {}
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Try to find date
            date_match = re.search(date_pattern, line)
            if date_match:
                # Save previous event if exists
                if current_event.get("title"):
                    events.append(current_event)
                current_event = {}
                date_obj = parse_date_from_text(line, date_pattern)
                if date_obj:
                    current_event["start_at"] = date_obj.isoformat()

            # Try to find title
            title_match = re.search(title_pattern, line)
            if title_match:
                current_event["title"] = title_match.group(1).strip()

            # Try to find time
            time_obj = parse_time_from_text(line)
            if time_obj:
                # Combine with date if we have one
                if current_event.get("start_at"):
                    try:
                        date_obj = datetime.datetime.fromisoformat(current_event["start_at"])
                        dt = datetime.datetime.combine(date_obj.date(), time_obj)
                        current_event["start_at"] = dt.isoformat()
                    except (ValueError, AttributeError):
                        pass

        # Don't forget the last event
        if current_event.get("title"):
            events.append(current_event)

    logger.info(f"Extracted {len(events)} events from text")
    return events


def extract_event_from_detail_page(text: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Extract full event data from detail text.

    Customize based on your detail text format.

    Args:
        text: Plain text content of event detail
        config: Configuration dict

    Returns:
        Event dict with enriched data
    """
    event = {}
    # Customize parsing logic here
    return event
