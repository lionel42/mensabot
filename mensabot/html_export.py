"""Render the daily vegetarian/vegan menu as a standalone HTML page."""

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
.errors h2 { margin: 0 0 6px; font-size: 1rem; }
.errors ul { margin: 0; padding-left: 20px; }
footer { margin-top: 32px; color: var(--muted); font-size: 0.85rem; }
/* Phones: stack each row into a block instead of scrolling sideways */
@media (max-width: 640px) {
  main { padding-top: 20px; }
  header h1 { font-size: 1.6rem; }
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


def build_html_page(
    df: pd.DataFrame | None,
    day: date,
    uris: dict[str, str] | None = None,
    errors: list[str] | None = None,
) -> str:
    """Build the full HTML page for the vegetarian/vegan menu of `day`."""
    uris = uris or {}
    errors = errors or []
    day_str = day.strftime("%A %d %B")

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
            f'<section class="errors"><h2>Errors while processing the menus</h2>'
            f"<ul>{items}</ul></section>"
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Veggie Lunch – {escape(day_str)}</title>
  <style>{CSS}</style>
</head>
<body>
  <main>
    <header>
      <p class="eyebrow">Veggie lunch in Dübendorf</p>
      <h1>{escape(day_str)}</h1>
      <p>{subtitle}</p>
    </header>
    {body}
    {errors_html}
    <footer>CO₂: green &lt; {CO2_LOW} kg · yellow &lt; {CO2_HIGH} kg · red ≥ {CO2_HIGH} kg</footer>
  </main>
</body>
</html>
"""
