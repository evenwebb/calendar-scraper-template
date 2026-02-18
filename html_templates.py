"""HTML template generation for calendar pages.

CUSTOMIZE THIS to match your branding, colors, and layout preferences.
"""
import datetime
import json
from typing import Any, Dict, List, Optional

import config
from utils import parse_iso_datetime, strip_html


def build_index_html(
    events: List[Dict[str, Any]],
    upcoming_count: Optional[int] = None,
    health_status: Optional[Dict[str, Any]] = None
) -> str:
    """Build the index HTML page with calendar link and featured events.

    CUSTOMIZE: Colors, fonts, layout, branding
    """
    ics_url = f"{config.ICS_FILENAME}.ics"
    count = upcoming_count if upcoming_count is not None else len(events)

    # Build health status display
    health_html = ""
    if health_status:
        last_update = health_status.get("last_update", "")
        status = health_status.get("status", "unknown")
        message = health_status.get("message", "")
        error = health_status.get("error")

        if last_update:
            try:
                update_dt = datetime.datetime.fromisoformat(last_update.replace("Z", "+00:00"))
                now = datetime.datetime.now(datetime.timezone.utc)
                delta = now - update_dt
                if delta.total_seconds() < 3600:
                    time_ago = f"{int(delta.total_seconds() / 60)} minutes ago"
                elif delta.total_seconds() < 86400:
                    time_ago = f"{int(delta.total_seconds() / 3600)} hours ago"
                else:
                    time_ago = f"{int(delta.total_seconds() / 86400)} days ago"
            except (ValueError, TypeError):
                time_ago = "recently"
        else:
            time_ago = "unknown"

        status_emoji = "✅" if status == "success" else ("⚠️" if status == "partial" else "❌")
        status_class = "success" if status == "success" else ("warning" if status == "partial" else "error")

        health_html = f'''
    <div class="health-status {status_class}">
      <div class="health-icon">{status_emoji}</div>
      <div class="health-info">
        <div class="health-main">Last updated: <span id="healthTimestamp" data-timestamp="{last_update}">{time_ago}</span></div>
        <div class="health-message">{message}</div>
        {f'<div class="health-error">Error: {error}</div>' if error else ''}
      </div>
    </div>'''

    # Build event cards
    featured_html = ""
    events_json_data = []
    if events:
        today = datetime.datetime.now(datetime.timezone.utc)
        upcoming_first = []
        past = []
        for e in events:
            start = parse_iso_datetime(e.get("start_at"))
            if start:
                s = start.replace(tzinfo=datetime.timezone.utc) if start.tzinfo is None else start
                (upcoming_first if s >= today else past).append(e)
            else:
                upcoming_first.append(e)
        ordered = upcoming_first + past

        featured_items = []
        for idx, e in enumerate(ordered):
            start = parse_iso_datetime(e.get("start_at"))
            date_str = start.strftime("%d %b %Y") if start else ""
            time_str = start.strftime("%H:%M") if start else ""
            title = e.get("title", "Event")
            location = e.get("location", "")
            description = strip_html(e.get("description", ""))[:200]
            slug = e.get("slug", "")
            url = f"{config.BASE_URL}/events/{slug}" if slug else e.get("url", "")

            is_upcoming = start and (start.replace(tzinfo=datetime.timezone.utc) if start.tzinfo is None else start) >= today

            events_json_data.append({
                "title": title,
                "date": date_str,
                "time": time_str,
                "location": location,
                "description": description,
                "url": url,
                "upcoming": is_upcoming,
            })

            featured_items.append(
                f'<div class="featured-event" data-event-idx="{idx}" onclick="showEventModal({idx})">'
                f'<div class="event-content">'
                f'<span class="date">{date_str}</span>'
                f'<span class="title">{title}</span>'
                f'<span class="location-small">📍 {location[:50]}{"..." if len(location) > 50 else ""}</span>'
                f'</div>'
                f"</div>"
            )
        featured_html = "\n        ".join(featured_items)

    # CUSTOMIZE: Update colors, fonts, and branding here
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{config.SITE_NAME} – Events Calendar</title>
  <meta name="description" content="{config.SITE_DESCRIPTION}">
  <meta name="author" content="{config.AUTHOR_NAME}">
  <style>
    :root {{
      --bg: #0a0a0f;
      --surface: #12121a;
      --border: rgba(0,212,255,0.25);
      --text: #e2e8f0;
      --text-muted: #94a3b8;
      --accent: {config.PRIMARY_COLOR};
      --accent-dim: rgba(0,212,255,0.15);
      --radius: 16px;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: system-ui, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.6;
      min-height: 100vh;
    }}
    .page {{ max-width: 700px; margin: 0 auto; padding: 2rem 1.25rem 4rem; }}
    .hero {{
      text-align: center;
      padding: 3rem 0 2rem;
    }}
    .hero h1 {{ font-size: 2rem; margin-bottom: 0.5rem; }}
    .hero .tagline {{ color: var(--text-muted); }}
    .card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 2rem;
      margin: 2rem 0;
      text-align: center;
    }}
    .btn {{
      display: inline-block;
      padding: 0.75rem 1.5rem;
      background: var(--accent);
      color: var(--bg);
      text-decoration: none;
      border-radius: 8px;
      font-weight: 600;
      margin: 0.5rem;
    }}
    .featured-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
      gap: 1rem;
      margin: 2rem 0;
    }}
    .featured-event {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 1rem;
      cursor: pointer;
    }}
    .featured-event:hover {{ border-color: var(--accent); }}
    .featured-event .date {{ color: var(--accent); font-size: 0.85rem; }}
    .featured-event .title {{ font-weight: 600; margin: 0.5rem 0; }}
    .featured-event .location-small {{ font-size: 0.85rem; color: var(--text-muted); }}
    .health-status {{
      padding: 1rem;
      margin: 1rem 0;
      border-radius: 8px;
      display: flex;
      gap: 0.5rem;
      font-size: 0.85rem;
    }}
    .modal {{
      display: none;
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0,0,0,0.8);
      z-index: 1000;
      padding: 2rem;
    }}
    .modal.active {{ display: flex; align-items: center; justify-content: center; }}
    .modal-content {{
      background: var(--surface);
      border-radius: var(--radius);
      padding: 2rem;
      max-width: 600px;
      width: 100%;
      position: relative;
    }}
    footer {{
      text-align: center;
      padding: 2rem;
      color: var(--text-muted);
      margin-top: 3rem;
    }}
  </style>
</head>
<body>
  <div class="page">
    <header class="hero">
      <h1>{config.SITE_NAME}</h1>
      <p class="tagline">{config.SITE_TAGLINE}</p>
    </header>
{health_html}
    <section class="card">
      <h2>Subscribe to the calendar</h2>
      <p>{count} upcoming event{'' if count == 1 else 's'}</p>
      <a href="{ics_url}" class="btn">📅 Subscribe</a>
      <a href="{ics_url}" class="btn" download>💾 Download .ics</a>
    </section>

    <section>
      <h2>Upcoming events</h2>
      <div class="featured-grid" id="eventGrid">
        {featured_html}
      </div>
    </section>

    <footer>
      <p>Created by <a href="{config.AUTHOR_URL}" target="_blank">{config.AUTHOR_NAME}</a></p>
    </footer>
  </div>

  <div id="eventModal" class="modal" onclick="if(event.target===this) closeModal()">
    <div class="modal-content">
      <button onclick="closeModal()" style="float: right; background: none; border: none; font-size: 1.5rem; cursor: pointer;">&times;</button>
      <h2 id="modalTitle"></h2>
      <div id="modalDate"></div>
      <div id="modalLocation"></div>
      <div id="modalDescription"></div>
      <a id="modalLink" href="#" target="_blank" class="btn">View details →</a>
    </div>
  </div>

  <script>
  const eventsData = {json.dumps(events_json_data)};
  function showEventModal(idx) {{
    const event = eventsData[idx];
    document.getElementById('modalTitle').textContent = event.title;
    document.getElementById('modalDate').textContent = event.date + ' ' + event.time;
    document.getElementById('modalLocation').textContent = event.location;
    document.getElementById('modalDescription').textContent = event.description;
    document.getElementById('modalLink').href = event.url;
    document.getElementById('eventModal').classList.add('active');
  }}
  function closeModal() {{
    document.getElementById('eventModal').classList.remove('active');
  }}
  </script>
</body>
</html>"""


def build_archive_html(past_events: List[Dict[str, Any]]) -> str:
    """Build the archive HTML page with past events."""
    if not past_events:
        events_html = '<p class="no-events">No past events in archive yet.</p>'
    else:
        events_by_year_month = {}
        for e in past_events:
            start = parse_iso_datetime(e.get("start_at"))
            if not start:
                continue
            year = start.year
            month = start.strftime("%B")
            key = (year, month, start.month)
            if key not in events_by_year_month:
                events_by_year_month[key] = []
            events_by_year_month[key].append((e, start))

        sorted_groups = sorted(events_by_year_month.items(), key=lambda x: (x[0][0], x[0][2]), reverse=True)

        events_html = ""
        for (year, month_name, _), events_list in sorted_groups:
            events_html += f'<div class="archive-group"><h3>{month_name} {year}</h3><div class="archive-events">'
            events_list.sort(key=lambda x: x[1], reverse=True)
            for event, start in events_list:
                title = event.get("title", "Untitled Event")
                location = event.get("location", "")
                date_str = start.strftime("%d %b %Y")
                slug = event.get("slug", "")
                url = f"{config.BASE_URL}/events/{slug}" if slug else ""

                location_html = f'<span class="location">{location}</span>' if location else ''
                link_html = f'<a href="{url}" target="_blank">View details →</a>' if url else ''

                events_html += f'''
        <div class="archive-event">
          <div class="archive-date">{date_str}</div>
          <div class="archive-details">
            <div class="archive-title">{title}</div>
            {location_html}
          </div>
          {link_html}
        </div>'''
            events_html += '</div></div>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Archive – {config.SITE_NAME}</title>
  <style>
    :root {{
      --bg: #0a0a0f;
      --surface: #12121a;
      --border: rgba(0,212,255,0.25);
      --text: #e2e8f0;
      --text-muted: #94a3b8;
      --accent: {config.PRIMARY_COLOR};
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: system-ui, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.6;
    }}
    .page {{ max-width: 800px; margin: 0 auto; padding: 2rem 1.25rem; }}
    .header {{ text-align: center; padding: 2rem 0; border-bottom: 1px solid var(--border); }}
    .archive-group {{ margin-bottom: 2rem; }}
    .archive-group h3 {{ margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid var(--border); }}
    .archive-event {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 1rem;
      margin-bottom: 0.75rem;
      display: grid;
      grid-template-columns: auto 1fr auto;
      gap: 1rem;
    }}
    .archive-date {{ color: var(--accent); font-weight: 600; }}
    .archive-title {{ font-weight: 600; }}
    .location {{ font-size: 0.85rem; color: var(--text-muted); }}
  </style>
</head>
<body>
  <div class="page">
    <header class="header">
      <h1>Event Archive</h1>
      <p>Past {config.SITE_NAME} events</p>
      <a href="index.html">← Back to calendar</a>
    </header>
    {events_html}
  </div>
</body>
</html>"""
