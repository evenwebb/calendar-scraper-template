<div align="center">

# 📅 Calendar Scraper Template

A reusable Python template for building event scrapers that generate iCalendar (`.ics`) feeds and static HTML calendar pages.

</div>

---

## 📚 Table of Contents

- [⚡ Quick Start](#-quick-start)
- [✨ Features](#-features)
- [📦 Installation](#-installation)
- [🚀 Usage](#-usage)
- [⚙️ Configuration](#️-configuration)
- [🤖 GitHub Actions Automation](#-github-actions-automation)
- [🗂️ Project Structure](#️-project-structure)
- [🧩 Dependencies](#-dependencies)
- [🛠️ Troubleshooting](#️-troubleshooting)
- [📄 License](#-license)

---

## ⚡ Quick Start

```bash
git clone https://github.com/evenwebb/calendar-scraper-template.git
cd calendar-scraper-template
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 init_scraper.py
python3 scraper.py
```

✅ Generated outputs are written to `docs/` by default.

---

## ✨ Features

| Feature | Description |
|---|---|
| `🔄 Multiple Extraction Methods` | JSON, HTML, text parsing, or REST API adapters depending on your source. |
| `💾 Smart Caching` | Event detail cache and state tracking reduce unnecessary re-scraping and writes. |
| `⚡ Optimized Updates` | Supports skipping full updates when no new upcoming events are detected. |
| `📱 HTML + iCal Output` | Generates both `.ics` feeds and static `index.html`/`archive.html` pages. |
| `🔔 Notification Support` | Optional VALARM notification blocks for event reminders in calendar clients. |
| `🌍 Timezone Aware` | Handles timezone-aware event serialization with configurable defaults. |
| `🤖 Automation Ready` | Includes GitHub Actions workflow with retries and optional failure issue creation. |

---

## 📦 Installation

```bash
git clone https://github.com/evenwebb/calendar-scraper-template.git
cd calendar-scraper-template
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Optional extras (enable in `requirements.txt` if needed):

- `beautifulsoup4` for HTML extraction
- `python-dotenv` for `.env` loading

---

## 🚀 Usage

```bash
python3 scraper.py
```

Typical output files:

- `docs/<ICS_FILENAME>.ics`
- `docs/index.html`
- `docs/archive.html`

---

## ⚙️ Configuration

Primary configuration lives in `config.py` (environment variables can override key values).

| Option | Default | Description |
|---|---|---|
| `EVENTS_URL` | `https://example.com/events` | Source events URL. |
| `BASE_URL` | `https://example.com` | Base URL for absolute links. |
| `OUTPUT_DIR` | `docs` | Output directory for generated files. |
| `ICS_FILENAME` | `calendar` | Output `.ics` base filename. |
| `EXTRACTION_METHOD` | `json` | One of `json`, `html`, `text`, `api`. |
| `HTTP_TIMEOUT` | `60` | HTTP timeout in seconds. |
| `HTTP_RETRIES` | `3` | Number of HTTP retries per request. |
| `CACHE_FILE` | `.event_cache.json` | Event detail cache file. |
| `CACHE_EXPIRY_DAYS` | `7` | Cache retention period. |
| `SKIP_IF_NO_NEW_EVENTS` | `True` | Skip full scrape when no new events are detected. |
| `INCLUDE_PAST_EVENTS` | `True` | Include past events in output. |
| `MAX_EVENTS` | `0` | Event cap (`0` = unlimited). |
| `DEFAULT_TIMEZONE` | `UTC` | Fallback timezone for events. |

### 🧱 Template placeholders to replace before production

- `CALENDAR_NAME`
- `CALENDAR_DESCRIPTION`
- `CALENDAR_PRODID`
- `UID_DOMAIN`
- `SITE_NAME`
- `SITE_TAGLINE`
- `SITE_DESCRIPTION`

---

## 🤖 GitHub Actions Automation

This template includes `.github/workflows/scrape.yml`:

- `⏰` Runs daily at `09:00 UTC`
- `🖱️` Supports manual runs (`workflow_dispatch`)
- `🔁` Retries scraper execution before failure (`SCRAPER_RUN_ATTEMPTS`, default `2`)
- `📝` Commits changed generated output/cache files
- `🚨` Optionally opens or updates a GitHub issue on failure (`CREATE_FAILURE_ISSUE=true`)

Recommended secrets:

- `CREATE_FAILURE_ISSUE` (`true`/`false`)
- `SCRAPER_RUN_ATTEMPTS` (integer)

---

## 🗂️ Project Structure

- `scraper.py`: Main orchestration and output generation.
- `config.py`: Template configuration and defaults.
- `init_scraper.py`: Interactive bootstrap helper.
- `extractors/`: Source-specific extraction adapters.
- `html_templates.py`: Static HTML rendering templates.
- `utils.py`: Shared utilities.
- `.github/workflows/scrape.yml`: Automation example.

---

## 🧩 Dependencies

| Package | Purpose |
|---|---|
| `requests` | HTTP requests for source data |
| `beautifulsoup4` (optional) | HTML parsing extractor |
| `python-dotenv` (optional) | Environment variable loading from `.env` |

---

## 🛠️ Troubleshooting

- `🔎` If no events are generated, verify extraction method and selectors/path config.
- `🧱` Replace all placeholders in `config.py` before production use.
- `📜` For CI failures, inspect workflow logs and raise `SCRAPER_RUN_ATTEMPTS` if needed.

---

## 📄 License

[GPL-3.0](LICENSE)
