import html
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import psycopg
from psycopg.rows import dict_row

FEATURES = (
    ("rank_initial_survey", "Initial Survey"),
    ("rank_rating_feature", "Rating Feature"),
    ("rank_top_5_for_you", "Top 5 For You"),
    ("rank_meta_score_and_explanation", "Meta Score & Explanation"),
    ("rank_friend_score", "Friend Score"),
    ("rank_scent_lookup", "Scent Lookup"),
    ("rank_not_for_me_button", "Not For Me"),
    ("rank_dupe_finder", "Dupe Finder"),
)


def feature_summary(rows):
    n = len(rows)
    summary = []
    for key, label in FEATURES:
        avg = sum(row[key] for row in rows) / n if n else 0
        summary.append((avg, label))
    summary.sort()
    return summary


def page(rows):
    summary = feature_summary(rows)
    bars = []
    for avg, label in summary:
        width = round((9 - avg) / 8 * 100, 1)
        bars.append(
            f"<tr><td>{html.escape(label)}</td>"
            f"<td class='num'>{avg:.1f}</td>"
            f"<td><span class='bar' style='width:{width}%'></span></td></tr>"
        )
    people = []
    for row in rows:
        cells = "".join(f"<td class='num'>{row[key]}</td>" for key, _ in FEATURES)
        feedback = html.escape(row["feedback"] or "")
        when = row["submitted_at"].strftime("%b %-d, %Y %-I:%M %p")
        people.append(
            "<tr>"
            f"<td>{html.escape(row['respondent_name'])}</td>"
            f"<td>{html.escape(row['user_type'])}</td>"
            f"<td>{when}</td>"
            f"{cells}<td>{feedback}</td></tr>"
        )
    heads = "".join(f"<th>{html.escape(label)}</th>" for _, label in FEATURES)
    return f"""<!doctype html>
<meta charset="utf-8">
<title>Scent Optimizer rankings</title>
<style>
  body {{ font: 15px/1.4 system-ui, sans-serif; margin: 2rem; color: #1c1917; background: #faf7f2; }}
  h1 {{ font-size: 1.4rem; margin: 0 0 .25rem; }}
  p {{ color: #57534e; margin: 0 0 1.5rem; }}
  h2 {{ font-size: 1rem; margin: 1.5rem 0 .5rem; }}
  table {{ border-collapse: collapse; width: 100%; background: #fff; }}
  th, td {{ border-bottom: 1px solid #e7e5e4; padding: .45rem .6rem; text-align: left; vertical-align: middle; white-space: nowrap; }}
  th {{ font-size: .75rem; letter-spacing: .02em; color: #78716c; }}
  .num {{ text-align: right; font-variant-numeric: tabular-nums; }}
  .bar {{ display: block; height: .55rem; background: #b45309; border-radius: 99px; }}
  .wrap {{ overflow-x: auto; }}
  .responses {{ width: max-content; min-width: 100%; }}
</style>
<h1>Scent Optimizer feature rankings</h1>
<p>{len(rows)} responses. Rank 1 is the feature they wanted most. Lower average is better.</p>
<h2>Average rank</h2>
<table>
  <tr><th>Feature</th><th class="num">Average</th><th>Preference</th></tr>
  {''.join(bars)}
</table>
<h2>Responses</h2>
<div class="wrap">
<table class="responses">
  <tr><th>Name</th><th>User type</th><th>Submitted</th>{heads}<th>Feedback</th></tr>
  {''.join(people)}
</table>
</div>
"""


def load_rows():
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("select * from feature_rankings order by submitted_at")
            return cur.fetchall()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.split("?", 1)[0] != "/":
            self.send_error(404)
            return
        try:
            body = page(load_rows()).encode()
            status = 200
        except Exception as exc:
            body = f"Could not read feature_rankings: {html.escape(str(exc))}".encode()
            status = 500
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print(fmt % args)


def _check():
    rows = [{key: i + 1 for i, (key, _) in enumerate(FEATURES)} for _ in range(2)]
    summary = feature_summary(rows)
    assert summary[0] == (1.0, "Initial Survey")
    assert summary[-1] == (8.0, "Dupe Finder")
    assert "Frank" in page([{
        **{key: i + 1 for i, (key, _) in enumerate(FEATURES)},
        "respondent_name": "Frank",
        "user_type": "Collector",
        "feedback": "<b>",
        "submitted_at": __import__("datetime").datetime(2026, 10, 6, 18, 45),
    }])
    assert "&lt;b&gt;" in page([{
        **{key: 1 for key, _ in FEATURES},
        "respondent_name": "A",
        "user_type": "B",
        "feedback": "<b>",
        "submitted_at": __import__("datetime").datetime(2026, 10, 6, 18, 45),
    }])


if __name__ == "__main__":
    _check()
    port = int(os.environ.get("PORT", "8000"))
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
