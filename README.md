<p align="center">
  <strong>📅 Calendar Scraper Template</strong>
</p>

<p align="center">
  <em>A reusable template for creating calendar scrapers that generate iCalendar (.ics) files from event websites</em>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-GPL--3.0-blue.svg" alt="License: GPL-3.0"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10+-green.svg" alt="Python 3.10+"></a>
  <a href="https://github.com"><img src="https://img.shields.io/badge/source-GitHub-black" alt="Source"></a>
</p>

---

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Features](#-features)
- [Installation](#-installation)
- [Usage](#-usage)
- [Extraction Methods](#-extraction-methods)
- [Customization](#-customization)
- [GitHub Actions](#-github-actions)
- [Examples](#-examples)
- [Project Structure](#-project-structure)
- [Documentation](#-documentation)
- [Contributing](#-contributing)
- [License](#-license)

---

## ⚡ Quick Start

Get your calendar scraper running in 5 minutes:

```bash
# 1. Copy the template
cp -r calendar-scraper-template my-calendar-scraper
cd my-calendar-scraper

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run interactive setup
python init_scraper.py

# 4. Test your scraper
python scraper.py
```

Your generated calendar files will be in the `docs/` directory:
- `calendar.ics` - iCalendar file ready to subscribe
- `index.html` - Beautiful calendar page
- `archive.html` - Past events archive

> 📖 **New to this?** Check out [QUICKSTART.md](QUICKSTART.md) for a detailed walkthrough.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔄 **Multiple Extraction Methods** | JSON, HTML, text parsing, or REST API - choose what fits your source |
| 💾 **Smart Caching** | Avoids re-scraping unchanged data with configurable cache expiry |
| ⚡ **Optimized Updates** | Skips full scrape when no new events detected (saves resources) |
| 📱 **Beautiful HTML Pages** | Responsive, modern calendar pages with search and filtering |
| 🤖 **GitHub Actions Ready** | Automated weekly updates with included workflow |
| 🔔 **Configurable Notifications** | Set up calendar reminders for events |
| 🌍 **Timezone Aware** | Handles timezones correctly for global events |
| 📊 **Health Monitoring** | Built-in health status tracking for monitoring |

---

## 📦 Installation

**Requirements:** Python 3.10+ and `requests`

```bash
pip install -r requirements.txt
```

**Optional dependencies** (uncomment in `requirements.txt` if needed):
- `beautifulsoup4` - For HTML extraction
- `python-dotenv` - For environment variable support

---

## 🚀 Usage

### Basic Usage

```bash
python scraper.py
```

This will:
1. Fetch events from your configured URL
2. Extract and validate event data
3. Generate `docs/calendar.ics` (iCalendar file)
4. Generate `docs/index.html` (calendar page)
5. Generate `docs/archive.html` (past events)

### Configuration

Edit `config.py` to customize:

```python
# Site Configuration
EVENTS_URL = "https://example.com/events"
BASE_URL = "https://example.com"

# Calendar Metadata
CALENDAR_NAME = "My Events Calendar"
CALENDAR_DESCRIPTION = "Upcoming events from Example Site"
UID_DOMAIN = "example.com"

# Extraction Method
EXTRACTION_METHOD = "json"  # or "html", "text", "api"
```

See [TEMPLATE_GUIDE.md](TEMPLATE_GUIDE.md) for detailed customization instructions.

---

## 🔍 Extraction Methods

The template supports four extraction methods:

### 1. JSON Extraction
**Best for:** Next.js sites, React SSR, JSON-LD structured data

```python
EXTRACTION_METHOD = "json"
JSON_SCRIPT_ID = "__NEXT_DATA__"
JSON_PATH = ["props", "pageProps", "events"]
```

### 2. HTML Extraction
**Best for:** Traditional HTML pages with CSS selectors

```python
EXTRACTION_METHOD = "html"
HTML_EVENT_CONTAINER = ".event"
HTML_TITLE_SELECTOR = "h2"
```

Requires: `beautifulsoup4` (uncomment in `requirements.txt`)

### 3. Text Extraction
**Best for:** Plain text, meeting minutes, simple lists

```python
EXTRACTION_METHOD = "text"
TEXT_DATE_PATTERN = r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})"
```

### 4. API Extraction
**Best for:** REST APIs, GraphQL endpoints

```python
EXTRACTION_METHOD = "api"
API_ENDPOINT = "https://api.example.com/events"
API_HEADERS = {"Authorization": "Bearer TOKEN"}
```

---

## 🎨 Customization

### Quick Customization Checklist

- [ ] Update `config.py` with your site URLs and settings
- [ ] Choose and customize an extractor in `extractors/`
- [ ] Customize `validate_event_data()` in `scraper.py`
- [ ] Update `make_ics_event()` for your event fields
- [ ] Customize HTML templates in `html_templates.py`
- [ ] Update GitHub Actions workflow schedule

See [`.template_checklist.md`](.template_checklist.md) for a complete checklist.

### Customization Examples

**Add custom event categorization:**
```python
def categorize_event(event):
    title = event.get("title", "").lower()
    if "meeting" in title:
        return "meeting"
    elif "workshop" in title:
        return "workshop"
    return "other"
```

**Configure calendar notifications:**
```python
NOTIFICATIONS = {
    "enabled": True,
    "alarms": [
        {"days_before": 1, "description": "Event tomorrow"},
        {"days_before": 0, "time": "09:00", "description": "Event today"},
    ],
}
```

---

## 🤖 GitHub Actions

The included workflow automatically updates your calendar weekly:

```yaml
# .github/workflows/scrape.yml
on:
  schedule:
    - cron: '0 9 * * 1'  # Every Monday at 9 AM UTC
  workflow_dispatch:  # Manual trigger
```

**Setup GitHub Pages:**
1. Go to **Settings → Pages**
2. **Deploy from a branch** → branch **main** → folder **/docs**
3. Your calendar will be at `https://username.github.io/repo-name/`

---

## 📚 Examples

Real-world examples built with this template:

| Project Type | Source Type | Extraction Method |
|--------------|------------|-------------------|
| Event Calendar | Next.js | JSON (`__NEXT_DATA__`) |
| Cinema Listings | HTML | BeautifulSoup |
| Meeting Calendar | Text | Regex parsing |

See [EXAMPLES.md](EXAMPLES.md) for detailed implementation examples.

---

## 📁 Project Structure

```
calendar-scraper-template/
├── scraper.py              # Main scraper script
├── config.py               # Configuration (CUSTOMIZE THIS)
├── utils.py                # Reusable helper functions
├── html_templates.py       # HTML generation (CUSTOMIZE THIS)
├── init_scraper.py         # Interactive setup script
│
├── extractors/             # Extraction adapters
│   ├── json_extractor.py  # JSON in HTML (e.g., __NEXT_DATA__)
│   ├── html_extractor.py  # HTML parsing (BeautifulSoup)
│   ├── text_extractor.py  # Regex/text parsing
│   └── api_extractor.py   # REST API endpoints
│
├── tests/                  # Example test structure
│   └── test_scraper.py
│
├── .github/workflows/      # GitHub Actions workflow
│   └── scrape.yml
│
├── docs/                   # Output directory (generated)
│   ├── calendar.ics       # iCalendar file
│   ├── index.html         # Calendar page
│   └── archive.html        # Past events
│
└── docs/                   # Documentation
    ├── README.md           # This file
    ├── QUICKSTART.md       # 5-minute setup guide
    ├── TEMPLATE_GUIDE.md   # Detailed customization guide
    └── EXAMPLES.md         # Real-world examples
```

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [QUICKSTART.md](QUICKSTART.md) | Get started in 5 minutes |
| [TEMPLATE_GUIDE.md](TEMPLATE_GUIDE.md) | Detailed customization guide |
| [EXAMPLES.md](EXAMPLES.md) | Real-world implementation examples |
| [.template_checklist.md](.template_checklist.md) | Customization checklist |

---

## 🛠️ Troubleshooting

<details>
<summary><strong>No events found?</strong></summary>

1. Check that `EVENTS_URL` in `config.py` is correct
2. Verify your extraction method matches the page structure
3. Look at `scraper_log.txt` for detailed error messages
4. Test your extractor with sample HTML/JSON from the page
</details>

<details>
<summary><strong>Events missing fields?</strong></summary>

1. Customize `validate_event_data()` in `scraper.py` if too strict
2. Update field mappings in `config.py` if source uses different names
3. Check that your extractor is capturing all needed fields
</details>

<details>
<summary><strong>iCal file won't import?</strong></summary>

1. Verify dates are valid ISO 8601 format
2. Check that each event has a unique UID
3. Validate the file with an online iCal validator
4. Ensure timezone handling is correct
</details>

<details>
<summary><strong>GitHub Actions failing?</strong></summary>

1. Check Actions tab for detailed error messages
2. Test locally first: `python scraper.py`
3. Ensure all dependencies are in `requirements.txt`
4. Verify workflow has `contents: write` permission
</details>

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Report bugs** - Open an issue with details
2. **Suggest features** - Share your ideas
3. **Submit pull requests** - Improvements and fixes
4. **Share examples** - Add your scraper to EXAMPLES.md

---

## 📄 License

This project is licensed under the **GPL-3.0 License** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built from patterns used in real-world calendar scrapers
- Inspired by the need for reusable, maintainable scraping templates
- Thanks to all contributors who've shared their implementations

---

## ⭐ Show Your Support

If this template helped you create a calendar scraper, consider:

- ⭐ Starring this repository
- 🐛 Reporting bugs or suggesting features
- 📝 Sharing your implementation in EXAMPLES.md
- 🔗 Linking back to this template

---

<p align="center">
  <strong>Happy Scraping! 📅</strong>
</p>

<p align="center">
  Made with ❤️ for the open source community
</p>
