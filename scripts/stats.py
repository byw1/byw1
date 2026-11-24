"""Write dist/stats.svg: current streak, longest streak and top languages.

Runs in the snake Action with GH_TOKEN set. Streaks come from the
contribution calendar (which includes private contributions when the
profile shows them); languages come from the owner's public, non-fork repos,
since the Action's token can't read private ones.

    python3 scripts/stats.py <login> <out.svg>
"""
import datetime as dt
import html
import json
import os
import sys
import urllib.request

LOGIN, OUT = sys.argv[1], sys.argv[2]
TOKEN = os.environ["GH_TOKEN"]


def gql(query, **variables):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as r:
        body = json.load(r)
    if body.get("errors"):
        raise SystemExit(json.dumps(body["errors"]))
    return body["data"]


# ------------------------------------------------------------------ streaks
years = gql(
    "query($l:String!){user(login:$l){contributionsCollection{contributionYears}}}", l=LOGIN
)["user"]["contributionsCollection"]["contributionYears"]

days = {}
for y in sorted(years):
    data = gql(
        """query($l:String!,$f:DateTime!,$t:DateTime!){user(login:$l){
          contributionsCollection(from:$f,to:$t){contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}""",
        l=LOGIN, f=f"{y}-01-01T00:00:00Z", t=f"{y}-12-31T23:59:59Z",
    )
    for w in data["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]:
        for d in w["contributionDays"]:
            days[d["date"]] = d["contributionCount"]

# The calendar runs to Dec 31, so drop days that haven't happened yet. Allow
# one day of slack for time zones ahead of UTC.
horizon = (dt.datetime.now(dt.timezone.utc).date() + dt.timedelta(days=1)).isoformat()
dates = sorted(d for d in days if d <= horizon)
while len(dates) > 1 and dates[-1] > dt.datetime.now(dt.timezone.utc).date().isoformat() and days[dates[-1]] == 0:
    dates.pop()
today = dates[-1]

longest, longest_span, run, run_start = 0, None, 0, None
for d in dates:
    if days[d] > 0:
        if run == 0:
            run_start = d
        run += 1
        if run > longest:
            longest, longest_span = run, (run_start, d)
    else:
        run = 0

# Current streak: today with nothing yet doesn't break it, like GitHub's own.
i = len(dates) - 1
if days[dates[i]] == 0:
    i -= 1
current, cur_end = 0, dates[i] if i >= 0 else today
while i >= 0 and days[dates[i]] > 0:
    current += 1
    i -= 1
cur_span = (dates[i + 1], cur_end) if current else None


def fmt(span):
    if not span:
        return "start one today"
    a, b = (dt.date.fromisoformat(x) for x in span)
    this_year = dt.date.fromisoformat(today).year
    f = lambda d: d.strftime("%b ") + str(d.day) + ("" if d.year == this_year else f", {d.year}")
    return f(a) if a == b else f"{f(a)} – {f(b)}"


# ------------------------------------------------------------------ languages
langs = {}
cursor = None
while True:
    data = gql(
        """query($l:String!,$c:String){user(login:$l){repositories(first:100,after:$c,ownerAffiliations:OWNER,isFork:false,privacy:PUBLIC){
          pageInfo{hasNextPage endCursor}
          nodes{languages(first:20,orderBy:{field:SIZE,direction:DESC}){edges{size node{name color}}}}}}}""",
        l=LOGIN, c=cursor,
    )
    repos = data["user"]["repositories"]
    for n in repos["nodes"]:
        for e in n["languages"]["edges"]:
            name = e["node"]["name"]
            size, color = langs.get(name, (0, e["node"]["color"] or "#8b949e"))
            langs[name] = (size + e["size"], color)
    if not repos["pageInfo"]["hasNextPage"]:
        break
    cursor = repos["pageInfo"]["endCursor"]

total = sum(s for s, _ in langs.values()) or 1
top = sorted(langs.items(), key=lambda kv: -kv[1][0])[:5]
shown = sum(s for _, (s, _) in top)
rows = [(n, c, s / total * 100) for n, (s, c) in top]
if total - shown > 0:
    rows.append(("Other", "#3f3f46", (total - shown) / total * 100))

# ------------------------------------------------------------------ svg
W, H = 1200, 300
esc = html.escape
FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"


def stat(x, label, value, unit, span, accent, delay):
    return f"""<g class="up" style="animation-delay:{delay}s">
  <text x="{x}" y="82" class="lbl">{label}</text>
  <text x="{x}" y="168" class="big" fill="{accent}">{value}</text>
  <text x="{x}" y="200" class="unit">{unit}</text>
  <text x="{x}" y="232" class="span">{esc(span)}</text>
</g>"""


bar_x, bar_w, bar_y = 600, 556, 108
segs, x = "", bar_x
for n, c, pct in rows:
    w = bar_w * pct / 100
    segs += f'<rect x="{x:.1f}" y="{bar_y}" width="{max(w, 0):.1f}" height="14" fill="{c}"/>'
    x += w

legend = ""
for k, (n, c, pct) in enumerate(rows):
    col, row = k % 2, k // 2
    lx, ly = bar_x + col * 290, 166 + row * 34
    legend += f"""<g class="up" style="animation-delay:{0.5 + k * 0.06:.2f}s">
  <circle cx="{lx + 6}" cy="{ly - 5}" r="6" fill="{c}"/>
  <text x="{lx + 22}" y="{ly}" class="lang">{esc(n)}</text>
  <text x="{lx + 270}" y="{ly}" class="pct" text-anchor="end">{pct:.1f}%</text>
</g>"""

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t">
<title id="t">Current streak {current} days. Longest streak {longest} days. Top languages: {esc(', '.join(f'{n} {p:.0f}%' for n, _, p in rows))}.</title>
<defs>
<style>
text{{font-family:{FONT}}}
.lbl{{font-size:12px;letter-spacing:3.5px;fill:#71717a;font-weight:600}}
.big{{font-size:84px;font-weight:700;letter-spacing:-3px}}
.unit{{font-size:15px;fill:#d4d4d8}}
.span{{font-size:13px;fill:#71717a}}
.lang{{font-size:15px;fill:#e4e4e7}}
.pct{{font-size:14px;fill:#71717a}}
.up{{opacity:0;animation:up .8s cubic-bezier(.22,1,.36,1) forwards}}
@keyframes up{{from{{opacity:0;transform:translateY(10px)}}to{{opacity:1;transform:none}}}}
.grow{{transform-origin:{bar_x}px 0;transform:scaleX(0);animation:grow 1.2s cubic-bezier(.22,1,.36,1) .35s forwards}}
@keyframes grow{{to{{transform:scaleX(1)}}}}
@media (prefers-reduced-motion:reduce){{.up,.grow{{animation:none;opacity:1;transform:none}}}}
</style>
<clipPath id="c"><rect width="{W}" height="{H}" rx="28"/></clipPath>
<clipPath id="bar"><rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="14" rx="7"/></clipPath>
<radialGradient id="g" cx="0%" cy="0%" r="60%"><stop offset="0" stop-color="#8b5cf6" stop-opacity=".22"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>
</defs>
<g clip-path="url(#c)">
 <rect width="{W}" height="{H}" fill="#000"/>
 <rect width="{W}" height="{H}" fill="url(#g)"/>
 {stat(48, "CURRENT STREAK", current, "day" if current == 1 else "days", fmt(cur_span), "#ffffff", 0.1)}
 {stat(300, "LONGEST STREAK", longest, "day" if longest == 1 else "days", fmt(longest_span), "#c4b5fd", 0.2)}
 <rect x="552" y="56" width="1" height="188" fill="#fff" fill-opacity=".1"/>
 <g class="up" style="animation-delay:.3s"><text x="{bar_x}" y="82" class="lbl">TOP LANGUAGES</text></g>
 <rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="14" rx="7" fill="#fff" fill-opacity=".06"/>
 <g clip-path="url(#bar)"><g class="grow">{segs}</g></g>
 {legend}
</g>
<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="27.5" fill="none" stroke="#fff" stroke-opacity=".1" stroke-width="1.5"/>
</svg>"""

with open(OUT, "w") as f:
    f.write(svg)
print(f"current {current}, longest {longest}, languages {rows}")
