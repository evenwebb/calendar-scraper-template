"""API extraction adapter for REST API endpoints.

Use this when events are available via a REST API.

Example usage:
    from extractors.api_extractor import extract_events_from_api

    events = extract_events_from_api(config)
"""
import logging
from typing import Any, Dict, List

import requests

logger = logging.getLogger(__name__)


def extract_events_from_api(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract events from a REST API endpoint.

    Customize based on your API structure.

    Args:
        config: Configuration dict with API settings:
            - api_endpoint: API endpoint URL
            - api_headers: Request headers (e.g., {"Authorization": "Bearer token"})
            - api_params: Query parameters
            - api_response_path: JSON path to events array (e.g., ["data", "events"])

    Returns:
        List of event dicts
    """
    endpoint = config.get("api_endpoint", "")
    headers = config.get("api_headers", {})
    params = config.get("api_params", {})
    response_path = config.get("api_response_path", [])

    if not endpoint:
        logger.error("API endpoint not configured")
        return []

    try:
        response = requests.get(endpoint, headers=headers, params=params, timeout=60)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        logger.error(f"API request failed: {e}")
        return []
    except ValueError as e:
        logger.error(f"Failed to parse API response as JSON: {e}")
        return []

    # Navigate to events array
    current = data
    for key in response_path:
        if not isinstance(current, dict):
            logger.error(f"Expected dict at path {response_path[:response_path.index(key)]}")
            return []
        current = current.get(key)
        if current is None:
            logger.warning(f"Path {response_path} not found in API response")
            return []

    if isinstance(current, list):
        events = current
    elif isinstance(current, dict):
        # If API returns a dict with events key
        events = current.get("events", [])
    else:
        logger.error(f"Events data is not a list or dict: {type(current)}")
        return []

    if not isinstance(events, list):
        events = []

    logger.info(f"Extracted {len(events)} events from API")
    return events


def extract_event_from_api(event_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Extract full event data from API detail endpoint.

    Args:
        event_id: Event identifier
        config: Configuration dict with:
            - api_detail_endpoint: Endpoint template (e.g., "https://api.com/events/{id}")
            - api_headers: Request headers

    Returns:
        Event dict with enriched data
    """
    endpoint_template = config.get("api_detail_endpoint", "")
    headers = config.get("api_headers", {})

    if not endpoint_template:
        return {}

    endpoint = endpoint_template.format(id=event_id)

    try:
        response = requests.get(endpoint, headers=headers, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.warning(f"Failed to fetch event detail {event_id}: {e}")
        return {}
