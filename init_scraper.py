#!/usr/bin/env python3
"""Interactive setup script for calendar scraper template.

Run this script to quickly configure your scraper with basic settings.
"""
import os
import sys
from pathlib import Path


def prompt(question: str, default: str = "") -> str:
    """Prompt user for input with optional default."""
    if default:
        response = input(f"{question} [{default}]: ").strip()
        return response if response else default
    return input(f"{question}: ").strip()


def main():
    """Interactive setup."""
    print("=" * 60)
    print("Calendar Scraper Template Setup")
    print("=" * 60)
    print()

    # Site configuration
    print("Site Configuration")
    print("-" * 60)
    events_url = prompt("Events page URL", "https://example.com/events")
    base_url = prompt("Base URL", events_url.rsplit("/", 1)[0] if "/" in events_url else events_url)
    print()

    # Calendar metadata
    print("Calendar Metadata")
    print("-" * 60)
    calendar_name = prompt("Calendar name", "My Events Calendar")
    calendar_description = prompt("Calendar description", f"Upcoming events from {base_url}")
    uid_domain = prompt("UID domain (for unique event IDs)", base_url.replace("https://", "").replace("http://", "").split("/")[0])
    print()

    # Extraction method
    print("Extraction Method")
    print("-" * 60)
    print("1. JSON (for JSON embedded in HTML, e.g., Next.js)")
    print("2. HTML (for HTML parsing with BeautifulSoup)")
    print("3. Text (for regex-based text parsing)")
    print("4. API (for REST API endpoints)")
    method_choice = prompt("Choose method (1-4)", "1")
    
    method_map = {"1": "json", "2": "html", "3": "text", "4": "api"}
    extraction_method = method_map.get(method_choice, "json")
    print()

    # Site branding
    print("Site Branding")
    print("-" * 60)
    site_name = prompt("Site name", calendar_name.replace(" Calendar", ""))
    site_tagline = prompt("Site tagline", "Never miss an event")
    author_name = prompt("Your name/GitHub username", "")
    author_url = prompt("Your website/GitHub URL", f"https://github.com/{author_name}" if author_name else "")
    print()

    # Generate config updates
    print("=" * 60)
    print("Configuration Summary")
    print("=" * 60)
    print(f"Events URL: {events_url}")
    print(f"Base URL: {base_url}")
    print(f"Calendar Name: {calendar_name}")
    print(f"Extraction Method: {extraction_method}")
    print(f"Site Name: {site_name}")
    print()

    confirm = prompt("Apply these settings? (y/n)", "y")
    if confirm.lower() != "y":
        print("Setup cancelled.")
        return

    # Update config.py
    config_path = Path("config.py")
    if not config_path.exists():
        print("Error: config.py not found!")
        return

    config_content = config_path.read_text()

    # Replace placeholders
    replacements = {
        "EVENTS_URL = os.getenv(\"EVENTS_URL\", \"https://example.com/events\")": f"EVENTS_URL = os.getenv(\"EVENTS_URL\", \"{events_url}\")",
        "BASE_URL = os.getenv(\"BASE_URL\", \"https://example.com\")": f"BASE_URL = os.getenv(\"BASE_URL\", \"{base_url}\")",
        "CALENDAR_NAME = \"{{CALENDAR_NAME}}\"": f"CALENDAR_NAME = \"{calendar_name}\"",
        "CALENDAR_DESCRIPTION = \"{{CALENDAR_DESCRIPTION}}\"": f"CALENDAR_DESCRIPTION = \"{calendar_description}\"",
        "UID_DOMAIN = \"{{UID_DOMAIN}}\"": f"UID_DOMAIN = \"{uid_domain}\"",
        "EXTRACTION_METHOD = \"json\"": f"EXTRACTION_METHOD = \"{extraction_method}\"",
        "SITE_NAME = \"{{SITE_NAME}}\"": f"SITE_NAME = \"{site_name}\"",
        "SITE_TAGLINE = \"{{SITE_TAGLINE}}\"": f"SITE_TAGLINE = \"{site_tagline}\"",
        "AUTHOR_NAME = \"{{AUTHOR_NAME}}\"": f"AUTHOR_NAME = \"{author_name}\"",
        "AUTHOR_URL = \"{{AUTHOR_URL}}\"": f"AUTHOR_URL = \"{author_url}\"",
    }

    for old, new in replacements.items():
        config_content = config_content.replace(old, new)

    config_path.write_text(config_content)

    print()
    print("✓ Configuration updated!")
    print()
    print("Next steps:")
    print("1. Review and customize config.py further if needed")
    print("2. Customize the extractor in extractors/ folder")
    print("3. Test with: python scraper.py")
    print("4. See QUICKSTART.md for more details")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")
        sys.exit(1)
