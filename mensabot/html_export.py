"""Render the vegetarian/vegan menus of a week as a standalone HTML page."""

import re
from datetime import date
from html import escape

import pandas as pd

# CO2 thresholds (kg CO2eq) for the low / medium / high colour code
CO2_LOW = 0.8
CO2_HIGH = 1.5

CSS = """
:root {
  --bg: #f6f7f4;
  --card: #ffffff;
  --text: #1f2421;
  --muted: #5f6b64;
  --border: #e2e6e1;
  --accent: #2f7d4f;
  --chip-bg: #eef2ee;
  --low: #2f7d4f;    --low-bg: #e3f2e8;
  --veg: #b85c00;    --veg-bg: #fde8d2;
  --mid: #9a6a00;    --mid-bg: #fbf0d6;
  --high: #b3401f;   --high-bg: #fbe3dc;
  --error-bg: #fdecea; --error: #8a1c12;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #141715;
    --card: #1d211f;
    --text: #e7ebe8;
    --muted: #9aa59f;
    --border: #2c322e;
    --accent: #6cc18f;
    --chip-bg: #262b28;
    --low: #7fd3a1;    --low-bg: #1f3428;
    --veg: #f5a65b;    --veg-bg: #3d2a17;
    --mid: #e6c06a;    --mid-bg: #3a3020;
    --high: #f0937a;   --high-bg: #3d2520;
    --error-bg: #3d2220; --error: #f4b1a8;
  }
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font: 16px/1.5 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
}
main { max-width: 1100px; margin: 0 auto; padding: 32px 16px 48px; }
header { margin-bottom: 24px; }
header .eyebrow {
  color: var(--accent); font-weight: 600; font-size: 0.85rem;
  letter-spacing: 0.08em; text-transform: uppercase; margin: 0;
}
header h1 { margin: 4px 0 4px; font-size: 2rem; line-height: 1.2; }
header p { margin: 0; color: var(--muted); }
.table-wrap {
  background: var(--card); border: 1px solid var(--border); border-radius: 14px;
  overflow: hidden;
}
table { width: 100%; border-collapse: collapse; }
th {
  text-align: left; font-size: 0.75rem; font-weight: 600; letter-spacing: 0.06em;
  text-transform: uppercase; color: var(--muted); padding: 12px 16px;
  border-bottom: 1px solid var(--border);
}
td { padding: 14px 16px; vertical-align: top; border-bottom: 1px solid var(--border); }
tbody tr:last-child td { border-bottom: none; }
tbody tr:hover { background: var(--chip-bg); }
th.num, td.num { text-align: right; }
.restaurant {
  color: var(--accent); font-weight: 600; text-decoration: none; white-space: nowrap;
}
a.restaurant:hover { text-decoration: underline; }
.price { font-weight: 700; font-variant-numeric: tabular-nums; white-space: nowrap; }
.title { font-weight: 600; }
.description { color: var(--muted); font-size: 0.9rem; margin-top: 2px; }
.tags { display: flex; flex-wrap: wrap; gap: 6px; }
.tag {
  background: var(--chip-bg); border-radius: 999px; padding: 2px 10px;
  font-size: 0.8rem; font-weight: 500;
}
.tag.vegan { background: var(--low-bg); color: var(--low); }
.tag.vegetarian { background: var(--veg-bg); color: var(--veg); }
.co2 { font-variant-numeric: tabular-nums; white-space: nowrap; }
.co2.low { background: var(--low-bg); color: var(--low); }
.co2.mid { background: var(--mid-bg); color: var(--mid); }
.co2.high { background: var(--high-bg); color: var(--high); }
.empty { color: var(--muted); }
.errors {
  margin-top: 24px; background: var(--error-bg); color: var(--error);
  border-radius: 12px; padding: 12px 16px;
}
.errors h3 { margin: 0 0 6px; font-size: 1rem; }
.errors ul { margin: 0; padding-left: 20px; }
/* Day tabs: hidden without JS, where all days are listed one after the other */
.tabs { display: none; }
.js .tabs {
  display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 8px; margin-bottom: 24px;
}
.tab {
  display: flex; flex-direction: column; align-items: center;
  padding: 10px 4px; border-radius: 12px; border: 1px solid var(--border);
  background: var(--card); color: var(--text); font: inherit; cursor: pointer;
}
.tab:hover { border-color: var(--accent); }
.tab:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
.tab[aria-selected="true"] { background: var(--accent); border-color: var(--accent); color: var(--card); }
.tab-day { font-size: 0.75rem; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; }
.tab-date { font-size: 1.4rem; font-weight: 700; line-height: 1.2; font-variant-numeric: tabular-nums; }
.tab-count { font-size: 0.75rem; opacity: 0.8; white-space: nowrap; }
.tab.today .tab-day::after { content: " · today"; text-transform: none; letter-spacing: 0; }
.day { margin-bottom: 32px; }
.js .day { margin-bottom: 0; }
.day-head { margin-bottom: 12px; }
.day-head h2 { margin: 0; font-size: 1.3rem; }
.day-head p { margin: 0; color: var(--muted); }
footer { margin-top: 32px; color: var(--muted); font-size: 0.85rem; }
/* Phones: stack each row into a block instead of scrolling sideways */
@media (max-width: 640px) {
  main { padding-top: 20px; }
  header h1 { font-size: 1.6rem; }
  .js .tabs { gap: 4px; }
  .tab-count { display: none; }
  .tab.today .tab-day::after { content: " •"; }
  thead { display: none; }
  table, tbody, tr, td { display: block; width: 100%; }
  tr { padding: 12px 16px; border-bottom: 1px solid var(--border); }
  tbody tr:last-child { border-bottom: none; }
  td { padding: 2px 0; border: none; }
  td.num { text-align: left; }
  td.tags-cell, td.num, td.co2-cell { display: inline-block; width: auto; margin: 4px 8px 4px 0; vertical-align: middle; }
}
"""


def _is_true(value) -> bool:
    """CSV booleans may come back as bool, string or NaN."""
    if isinstance(value, str):
        return value.strip().lower() == "true"
    return bool(value) if pd.notnull(value) else False


def _price(value) -> str:
    try:
        return f"CHF {float(value):.2f}"
    except (TypeError, ValueError):
        return ""


def _co2_tag(value) -> str:
    try:
        co2 = float(value)
    except (TypeError, ValueError):
        return ""
    if pd.isnull(co2):
        return ""
    level = "low" if co2 < CO2_LOW else "mid" if co2 < CO2_HIGH else "high"
    return f'<span class="tag co2 {level}">{co2:.1f} kg CO₂eq</span>'


def _row(row: pd.Series, uris: dict[str, str]) -> str:
    restaurant = escape(str(row.get("restaurant", "")))
    uri = uris.get(row.get("restaurant"))
    restaurant_html = (
        f'<a class="restaurant" href="{escape(uri, quote=True)}">{restaurant}</a>'
        if uri
        else f'<span class="restaurant">{restaurant}</span>'
    )

    description = row.get("description")
    description = (
        # Tidy spacing from the scraped text, e.g. "Erbsen , Tagessalat"
        re.sub(r"\s+", " ", re.sub(r"\s+,", ",", str(description))).strip()
        if pd.notnull(description)
        else ""
    )
    description_html = (
        f'<div class="description">{escape(description)}</div>' if description else ""
    )

    if _is_true(row.get("vegan")):
        tags_html = '<span class="tag vegan">Vegan</span>'
    else:
        tags_html = '<span class="tag vegetarian">Vegetarian</span>'
    if _is_true(row.get("glutenfree")):
        tags_html += '<span class="tag">Gluten-free</span>'

    return f"""
          <tr>
            <td>{restaurant_html}</td>
            <td class="tags-cell"><div class="tags">{tags_html}</div></td>
            <td class="num"><span class="price">{_price(row.get("price"))}</span></td>
            <td><div class="title">{escape(str(row.get("title", "")))}</div>{description_html}</td>
            <td class="co2-cell">{_co2_tag(row.get("co2_footprint"))}</td>
          </tr>"""


def _day_section(
    day: date,
    df: pd.DataFrame | None,
    uris: dict[str, str],
    errors: list[str],
) -> str:
    """One <section> holding the menu table of a single day."""
    if df is not None and not df.empty:
        rows = "".join(_row(row, uris) for _, row in df.iterrows())
        body = f"""<div class="table-wrap">
        <table>
          <thead>
            <tr><th>Restaurant</th><th>Diet</th><th class="num">Price</th><th>Dish</th><th>CO₂</th></tr>
          </thead>
          <tbody>{rows}
          </tbody>
        </table>
      </div>"""
        n = len(df)
        subtitle = f"{n} vegetarian or vegan dish{'es' if n != 1 else ''}"
    else:
        body = '<p class="empty">No vegetarian or vegan dishes found for this day.</p>'
        subtitle = "No menu available"

    errors_html = ""
    if errors:
        items = "".join(f"<li>{escape(e)}</li>" for e in errors)
        errors_html = (
            f'<section class="errors"><h3>Errors while processing the menus</h3>'
            f"<ul>{items}</ul></section>"
        )

    iso = day.isoformat()
    return f"""
    <section class="day" id="day-{iso}" data-date="{iso}"
             role="tabpanel" aria-labelledby="tab-{iso}">
      <div class="day-head">
        <h2>{escape(day.strftime("%A %d %B"))}</h2>
        <p>{subtitle}</p>
      </div>
      {body}
      {errors_html}
    </section>"""


def _tab(day: date, df: pd.DataFrame | None, active: bool) -> str:
    iso = day.isoformat()
    n = 0 if df is None else len(df)
    return (
        f'<button type="button" class="tab" role="tab" id="tab-{iso}" data-date="{iso}" '
        f'aria-controls="day-{iso}" aria-selected="{"true" if active else "false"}">'
        f'<span class="tab-day">{day.strftime("%a")}</span>'
        f'<span class="tab-date">{day.day}</span>'
        f'<span class="tab-count">{n} dish{"es" if n != 1 else ""}</span>'
        f"</button>"
    )


# Picks the day to show: URL hash > viewer's "today" (or next workday from
# 14:00 on) > closest day available. Without JS all days are listed.
SCRIPT = """
(function () {
  var CUTOFF_HOUR = 14;
  var tabs = Array.prototype.slice.call(document.querySelectorAll(".tab"));
  var days = Array.prototype.slice.call(document.querySelectorAll(".day"));
  if (!tabs.length) return;
  document.documentElement.classList.add("js");

  function iso(d) {
    var m = d.getMonth() + 1, day = d.getDate();
    return d.getFullYear() + "-" + (m < 10 ? "0" : "") + m + "-" + (day < 10 ? "0" : "") + day;
  }
  function select(date, updateHash) {
    tabs.forEach(function (t) {
      t.setAttribute("aria-selected", t.dataset.date === date ? "true" : "false");
    });
    days.forEach(function (s) { s.hidden = s.dataset.date !== date; });
    if (updateHash && history.replaceState) history.replaceState(null, "", "#" + date);
  }

  var now = new Date();
  var todayIso = iso(now);
  var target = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  if (now.getHours() >= CUTOFF_HOUR) target.setDate(target.getDate() + 1);
  while (target.getDay() === 0 || target.getDay() === 6) target.setDate(target.getDate() + 1);
  var wanted = iso(target);

  var available = tabs.map(function (t) { return t.dataset.date; });
  tabs.forEach(function (t) {
    if (t.dataset.date === todayIso) t.classList.add("today");
  });

  var hash = location.hash.replace("#", "");
  var chosen;
  if (available.indexOf(hash) !== -1) chosen = hash;
  else if (available.indexOf(wanted) !== -1) chosen = wanted;
  else {
    // Closest available day: first upcoming one, otherwise the last one
    chosen = available[available.length - 1];
    for (var i = 0; i < available.length; i++) {
      if (available[i] >= wanted) { chosen = available[i]; break; }
    }
  }
  select(chosen, false);

  tabs.forEach(function (t, i) {
    t.addEventListener("click", function () { select(t.dataset.date, true); });
    t.addEventListener("keydown", function (e) {
      var j = e.key === "ArrowRight" ? i + 1 : e.key === "ArrowLeft" ? i - 1 : null;
      if (j === null || j < 0 || j >= tabs.length) return;
      tabs[j].focus();
      select(tabs[j].dataset.date, true);
    });
  });
})();
"""


def build_html_page(
    menus: dict[date, pd.DataFrame | None],
    default_day: date,
    uris: dict[str, str] | None = None,
    errors: dict[date, list[str]] | None = None,
) -> str:
    """Build the HTML page with the vegetarian/vegan menus of several days.

    `menus` maps each day to its menu (None if unavailable). `default_day` is
    shown when JavaScript is unavailable; with JavaScript the page selects
    today, or the next workday from 14:00 on, in the viewer's local time.
    """
    uris = uris or {}
    errors = errors or {}
    days = sorted(set(menus) | {default_day})

    tabs = "".join(_tab(d, menus.get(d), d == default_day) for d in days)
    sections = "".join(
        _day_section(d, menus.get(d), uris, errors.get(d, []))
        for d in days
    )

    first, last = days[0], days[-1]
    first_fmt = "%d" if (first.year, first.month) == (last.year, last.month) else "%d %B"
    week_str = f"{first.strftime(first_fmt).lstrip('0')} – {last.strftime('%d %B %Y').lstrip('0')}"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Veggie Lunch – {escape(week_str)}</title>
  <style>{CSS}</style>
</head>
<body>
  <main>
    <header>
      <p class="eyebrow">Veggie lunch in Dübendorf</p>
      <h1>{escape(week_str)}</h1>
    </header>
    <nav class="tabs" role="tablist" aria-label="Day of the week">{tabs}</nav>
    {sections}
    <footer>CO₂: green &lt; {CO2_LOW} kg · yellow &lt; {CO2_HIGH} kg · red ≥ {CO2_HIGH} kg</footer>
  </main>
  <script>{SCRIPT}</script>
</body>
</html>
"""
