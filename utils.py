"""Utility functions for calendar scrapers.

Reusable helper functions for common tasks like date parsing,
HTML cleaning, URL normalization, and text sanitization.
"""
import datetime
import re
from typing import Optional


def strip_html(html: str) -> str:
    """Remove HTML tags and decode common entities.

    Args:
        html: HTML string to clean

    Returns:
        Plain text with HTML removed
    """
    if not html:
        return ""
    # Remove markdown-style links [text](url) -> text
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", html)
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)
    # Decode common entities
    text = text.replace("&nbsp;", " ").replace("&amp;", "&")
    text = text.replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"')
    text = text.replace("&#39;", "'").replace("&apos;", "'")
    # Normalise whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_iso_datetime(iso_str: str) -> Optional[datetime.datetime]:
    """Parse ISO 8601 datetime string to datetime (timezone-aware or naive).

    Handles formats like:
    - 2026-03-16T11:30:00.000-06:00
    - 2026-03-28T10:30:00.000Z
    - 2026-03-16T11:30:00

    Args:
        iso_str: ISO 8601 datetime string

    Returns:
        Parsed datetime object, or None if parsing fails
    """
    if not iso_str:
        return None
    try:
        # Handle Z suffix and milliseconds
        dt = datetime.datetime.fromisoformat(
            iso_str.replace("Z", "+00:00").replace(".000", "")
        )
        return dt
    except (ValueError, TypeError):
        return None


def parse_date_from_text(text: str, pattern: Optional[str] = None) -> Optional[datetime.date]:
    """Parse date from text using regex pattern.

    Common patterns:
    - "DD Month YYYY" (e.g., "10 October 2025")
    - "DD/MM/YYYY" (e.g., "10/10/2025")
    - "YYYY-MM-DD" (e.g., "2025-10-10")

    Args:
        text: Text containing a date
        pattern: Optional regex pattern (defaults to common formats)

    Returns:
        Parsed date object, or None if parsing fails
    """
    if not text:
        return None

    if pattern:
        match = re.search(pattern, text)
        if match:
            # Custom pattern handling - adjust based on your pattern
            # This is a simple example
            try:
                day = int(match.group(1))
                month_str = match.group(2)
                year = int(match.group(3)) if len(match.groups()) > 2 else datetime.date.today().year
                month = datetime.datetime.strptime(month_str, "%B").month
                return datetime.date(year, month, day)
            except (ValueError, IndexError):
                return None

    # Try common formats
    formats = [
        "%d %B %Y",  # 10 October 2025
        "%d/%m/%Y",  # 10/10/2025
        "%Y-%m-%d",  # 2025-10-10
        "%d %b %Y",  # 10 Oct 2025
        "%B %d, %Y",  # October 10, 2025
    ]

    for fmt in formats:
        try:
            return datetime.datetime.strptime(text.strip(), fmt).date()
        except ValueError:
            continue

    return None


def parse_time_from_text(text: str) -> Optional[datetime.time]:
    """Parse time from text.

    Handles formats like:
    - "14:30"
    - "2:30 PM"
    - "14:30:00"

    Args:
        text: Text containing a time

    Returns:
        Parsed time object, or None if parsing fails
    """
    if not text:
        return None

    # Try 24-hour format first
    time_patterns = [
        r"(\d{1,2}):(\d{2})(?::(\d{2}))?",  # 14:30 or 14:30:00
        r"(\d{1,2}):(\d{2})\s*(AM|PM)",  # 2:30 PM
    ]

    for pattern in time_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                hour = int(match.group(1))
                minute = int(match.group(2))
                second = int(match.group(3)) if len(match.groups()) > 2 and match.group(3) else 0

                # Handle AM/PM
                if len(match.groups()) > 2 and match.group(len(match.groups())):
                    am_pm = match.group(len(match.groups())).upper()
                    if am_pm == "PM" and hour != 12:
                        hour += 12
                    elif am_pm == "AM" and hour == 12:
                        hour = 0

                return datetime.time(hour, minute, second)
            except (ValueError, IndexError):
                continue

    return None


def normalize_url(url: str, base_url: str = "") -> str:
    """Normalize and make URL absolute.

    Args:
        url: URL to normalize (may be relative)
        base_url: Base URL for making relative URLs absolute

    Returns:
        Normalized absolute URL
    """
    if not url:
        return ""

    # Already absolute
    if url.startswith(("http://", "https://")):
        return url

    # Remove duplicate slashes
    url = re.sub(r"([^:])//+", r"\1/", url)

    # Make absolute if base_url provided
    if base_url and not url.startswith("/"):
        return f"{base_url.rstrip('/')}/{url.lstrip('/')}"
    elif base_url:
        return f"{base_url.rstrip('/')}{url}"

    return url


def sanitize_ical_text(text: str) -> str:
    """Sanitize text for iCalendar format (RFC 5545).

    Escapes special characters and handles line length.

    Args:
        text: Text to sanitize

    Returns:
        Sanitized text safe for iCalendar
    """
    if not text:
        return ""

    # Escape special characters
    text = text.replace("\\", "\\\\")
    text = text.replace("\n", "\\n")
    text = text.replace(",", "\\,")
    text = text.replace(";", "\\;")

    return text


def escape_and_fold_ical_text(text: str, prefix: str = "", line_length: int = 75) -> str:
    """Escape and fold text for iCalendar format per RFC 5545.

    Args:
        text: Text to escape and fold
        prefix: Prefix for the line (e.g., "DESCRIPTION:")
        line_length: Maximum line length (default 75 per RFC 5545)

    Returns:
        Escaped and folded text with line breaks
    """
    escaped = sanitize_ical_text(text)
    full_line = prefix + escaped

    if len(full_line) <= line_length:
        return full_line

    result = [full_line[:line_length]]
    remaining = full_line[line_length:]
    while remaining:
        result.append(" " + remaining[: line_length - 1])
        remaining = remaining[line_length - 1 :]
    return "\n".join(result)


def format_ical_datetime(dt: datetime.datetime) -> str:
    """Format datetime for iCal (UTC with Z suffix).

    Args:
        dt: Datetime to format

    Returns:
        Formatted datetime string (YYYYMMDDTHHMMSSZ)
    """
    if dt.tzinfo:
        dt = dt.astimezone(datetime.timezone.utc)
    return dt.strftime("%Y%m%dT%H%M%SZ")


def format_ical_date(date: datetime.date) -> str:
    """Format date for iCal.

    Args:
        date: Date to format

    Returns:
        Formatted date string (YYYYMMDD)
    """
    return date.strftime("%Y%m%d")


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def extract_text_between(text: str, start: str, end: str) -> Optional[str]:
    """Extract text between two markers.

    Args:
        text: Text to search
        start: Start marker
        end: End marker

    Returns:
        Extracted text, or None if markers not found
    """
    start_idx = text.find(start)
    if start_idx == -1:
        return None
    start_idx += len(start)
    end_idx = text.find(end, start_idx)
    if end_idx == -1:
        return None
    return text[start_idx:end_idx].strip()
