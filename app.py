import html
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import psycopg
from psycopg.rows import dict_row

from load_schema import database_url


def item_scores(rows):
    """Average rating per item. 1 is Hate and 4 is Love, so higher is better."""
    buckets = {}
    for row in rows:
        key = (row["category"], row["item_number"], row["item_label"])
        buckets.setdefault(key, []).append(row["rating"])
    scores = []
    for (category, item_number, label), ratings in buckets.items():
        scores.append({
            "category": category,
            "item_number": item_number,
            "item_label": label,
            "n": len(ratings),
            "average": sum(ratings) / len(ratings),
        })
    scores.sort(key=lambda score: (-score["average"], score["category"], score["item_number"]))
    return scores


def options(values, selected):
    parts = ["<option value=''>All</option>"]
    for value in values:
        picked = " selected" if value == selected else ""
        escaped = html.escape(value)
        parts.append(f"<option value='{escaped}'{picked}>{escaped}</option>")
    return "".join(parts)


def page(rows, people, categories, person, category):
    scores = item_scores(rows)
    bars = []
    for score in scores:
        width = round(score["average"] / 4 * 100, 1)
        bars.append(
            "<tr>"
            f"<td>{html.escape(score['item_label'])}</td>"
            f"<td>{html.escape(score['category'])}</td>"
            f"<td class='num'>{score['average']:.1f}</td>"
            f"<td class='num'>{score['n']}</td>"
            f"<td><span class='bar' style='width:{width}%'></span></td>"
            "</tr>"
        )
    details = []
    for row in rows:
        brand = html.escape(row["brand"] or "")
        product = html.escape(row["product_name"] or "")
        details.append(
            "<tr>"
            f"<td>{html.escape(row['person'])}</td>"
            f"<td>{html.escape(row['category'])}</td>"
            f"<td>{html.escape(row['item_label'])}</td>"
            f"<td>{brand}</td>"
            f"<td>{product}</td>"
            f"<td class='num'>{row['rating']}</td>"
            f"<td>{html.escape(row['rating_label'])}</td>"
            "</tr>"
        )
    who = html.escape(person or "everyone")
    kind = html.escape(category or "every category")
    return f"""<!doctype html>
<meta charset="utf-8">
<title>Scent ratings</title>
<style>
  body {{ font: 15px/1.4 system-ui, sans-serif; margin: 2rem; color: #1c1917; background: #faf7f2; }}
  h1 {{ font-size: 1.4rem; margin: 0 0 .25rem; }}
  p {{ color: #57534e; margin: 0 0 1.5rem; }}
  h2 {{ font-size: 1rem; margin: 1.5rem 0 .5rem; }}
  form {{ display: flex; gap: .75rem; align-items: end; flex-wrap: wrap; margin: 0 0 1.5rem; }}
  label {{ display: grid; gap: .25rem; font-size: .8rem; color: #57534e; }}
  select, button {{ font: inherit; padding: .4rem .55rem; color: #1c1917; background: #fff; border: 1px solid #d6d3d1; border-radius: .35rem; }}
  button {{ background: #b45309; color: #fff; border-color: #b45309; cursor: pointer; }}
  table {{ border-collapse: collapse; width: 100%; background: #fff; }}
  th, td {{ border-bottom: 1px solid #e7e5e4; padding: .45rem .6rem; text-align: left; vertical-align: middle; white-space: nowrap; }}
  th {{ font-size: .75rem; letter-spacing: .02em; color: #78716c; }}
  .num {{ text-align: right; font-variant-numeric: tabular-nums; }}
  .bar {{ display: block; height: .55rem; background: #b45309; border-radius: 99px; }}
  .wrap {{ overflow-x: auto; }}
</style>
<h1>Scent ratings</h1>
<p>{len(rows)} ratings for {who}, {kind}. 1 is Hate and 4 is Love.</p>
<form method="get" action="/">
  <label>Person
    <select name="person">{options(people, person)}</select>
  </label>
  <label>Category
    <select name="category">{options(categories, category)}</select>
  </label>
  <button type="submit">Show ratings</button>
</form>
<h2>Average rating</h2>
<table>
  <tr><th>Item</th><th>Category</th><th class="num">Average</th><th class="num">Ratings</th><th>Score</th></tr>
  {''.join(bars)}
</table>
<h2>Ratings</h2>
<div class="wrap">
<table>
  <tr><th>Person</th><th>Category</th><th>Item</th><th>Brand</th><th>Product</th><th class="num">Rating</th><th>Label</th></tr>
  {''.join(details)}
</table>
</div>
"""


def load(person, category):
    with psycopg.connect(database_url()) as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                select person, category, item_number, item_label,
                       brand, product_name, rating, rating_label
                from scent_ratings
                where (%s = '' or person = %s)
                  and (%s = '' or category = %s)
                order by category, item_number, person
                """,
                (person, person, category, category),
            )
            rows = cur.fetchall()
            cur.execute("select distinct person from scent_ratings order by person")
            people = [row["person"] for row in cur.fetchall()]
            cur.execute("select distinct category from scent_ratings order by category")
            categories = [row["category"] for row in cur.fetchall()]
    return rows, people, categories


def filters_from_path(path):
    query = parse_qs(urlparse(path).query)
    person = query.get("person", [""])[0].strip()
    category = query.get("category", [""])[0].strip()
    return person, category


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if urlparse(self.path).path != "/":
            self.send_error(404)
            return
        person, category = filters_from_path(self.path)
        try:
            body = page(*load(person, category), person, category).encode()
            status = 200
        except Exception as exc:
            body = f"Could not read scent_ratings: {html.escape(str(exc))}".encode()
            status = 500
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print(fmt % args)


def _check():
    rows = [
        {"category": "Candle", "item_number": 1, "item_label": "Candle 1", "rating": 2, "person": "Layla", "brand": None, "product_name": None, "rating_label": "Dislike"},
        {"category": "Candle", "item_number": 1, "item_label": "Candle 1", "rating": 4, "person": "Owen", "brand": None, "product_name": None, "rating_label": "Love"},
        {"category": "Perfume", "item_number": 1, "item_label": "Perfume 1", "rating": 1, "person": "<b>", "brand": "A&B", "product_name": "X", "rating_label": "Hate"},
    ]
    scores = item_scores(rows)
    assert scores[0]["item_label"] == "Candle 1"
    assert scores[0]["average"] == 3
    assert scores[0]["n"] == 2
    html_page = page(rows, ["Layla", "Owen"], ["Candle", "Perfume"], "Owen", "Candle")
    assert "selected" in html_page
    assert "&lt;b&gt;" in html_page
    assert "A&amp;B" in html_page
    assert filters_from_path("/?person=Owen&category=Candle") == ("Owen", "Candle")
    assert filters_from_path("/") == ("", "")


if __name__ == "__main__":
    _check()
    port = int(os.environ.get("PORT", "8000"))
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
