"""Extraction adapters for different data source types.

Choose the appropriate extractor based on your event source:
- json_extractor: For JSON embedded in HTML (e.g., __NEXT_DATA__)
- html_extractor: For HTML parsing with BeautifulSoup
- text_extractor: For regex-based text/line parsing
- api_extractor: For REST API endpoints

See each extractor file for usage examples and customization instructions.
"""
