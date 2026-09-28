"""Build the /html-report dashboard: applications from job_search_tracker.csv (+ outcome.md
files), the LinkedIn referral outreach from documents/context/network-queue.csv and the cold
email outreach from documents/context/cold-email-targets.csv.

Usage: python tools/html_report.py [output.html] [--open]
Self-contained output: inline CSS/JS/SVG, no external requests. Read-only on all inputs.
"""
import csv, html, math, re, json, sys, webbrowser
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUEUE = ROOT / "documents/context/network-queue.csv"
FIELDS = ["date", "company", "sector", "role", "role_type", "channel", "status", "contact_person",
          "fit_rating", "notes", "cv_file", "cover_letter_file", "source", "deadline"]
rows = []
with open(ROOT / "job_search_tracker.csv", encoding="utf-8") as f:
    r = csv.reader(f); next(r)
    for rec in r:
        if not any(rec): continue
        rec += [""] * (len(FIELDS) - len(rec))
        rows.append(dict(zip(FIELDS, rec)))

# outcome.md merge (none exist today, but handle them)
def norm(s): return re.sub(r"[^a-z0-9]", "", s.lower())
outcomes = {}
for p in (ROOT / "documents/applications").glob("*/outcome.md"):
    outcomes[norm(p.parent.name)] = p.read_text(encoding="utf-8")
for row in rows:
    key = norm(row["company"] + row["role"])
    row["_outcome"] = next((t for k, t in outcomes.items() if k in key or key in k), "")

BUCKET = {"drafted": "Drafted", "applied": "Active", "interview": "Interview", "offer": "Offer", "hired": "Hired"}
CLOSED = {"rejected", "no_response", "no response", "offer_declined", "offer declined", "withdrawn"}
unknown = set()
for row in rows:
    s = row["status"].strip().lower()
    if s in BUCKET: row["_b"] = BUCKET[s]
    else:
        row["_b"] = "Rejected/Closed"
        if s not in CLOSED: unknown.add(row["status"])

COL = {"Drafted": "#64748b", "Active": "#3b82f6", "Interview": "#f59e0b", "Offer": "#8b5cf6",
       "Hired": "#22c55e", "Rejected/Closed": "#ef4444"}
ORDER = list(COL)
sent = [r for r in rows if r["_b"] != "Drafted"]
drafted = len(rows) - len(sent)
by_bucket = Counter(r["_b"] for r in rows)

def reached(row, stage):
    s = row["status"].strip().lower()
    rank = {"applied": 0, "interview": 1, "offer": 2, "offer_declined": 2, "offer declined": 2, "hired": 3}
    need = {"Interview": 1, "Offer": 2, "Hired": 3}[stage]
    if rank.get(s, 0) >= need: return True
    o = row["_outcome"].lower()
    return bool(re.search(r"\[x\][^\n]*" + stage.lower(), o))

funnel = [("Applied", len(sent))] + [(st, sum(reached(r, st) for r in sent)) for st in ("Interview", "Offer", "Hired")]
past_screen = funnel[1][1]
pct = round(100 * past_screen / len(sent)) if sent else 0
true_rej = sum(r["status"].strip().lower() in ("rejected", "no_response", "no response") for r in sent)
final = sum(r["_b"] in ("Rejected/Closed", "Hired") for r in sent)
rej_rate = f"{round(100 * true_rej / final)}%" if final else "n/a (no final outcomes yet)"
by_sector = Counter(r["sector"] or "Unknown" for r in sent).most_common()
def chan(c):
    c = c.lower()
    return "Online / portal" if c in ("portal", "online") else "Referral" if c == "referral" else "Other"
by_channel = Counter(chan(r["channel"]) for r in sent).most_common()

e = lambda s: html.escape(str(s), quote=True)

def doughnut():
    data = [(b, by_bucket[b]) for b in ORDER if by_bucket[b]]
    total = sum(v for _, v in data) or 1
    cx = cy = 90; R = 70; w = 26
    parts, a0 = [], -math.pi / 2
    for b, v in data:
        if v == total:
            parts.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{COL[b]}" stroke-width="{w}"><title>{e(b)}: {v}</title></circle>')
            break
        a1 = a0 + 2 * math.pi * v / total
        large = 1 if a1 - a0 > math.pi else 0
        x0, y0 = cx + R * math.cos(a0), cy + R * math.sin(a0)
        x1, y1 = cx + R * math.cos(a1), cy + R * math.sin(a1)
        parts.append(f'<path d="M{x0:.2f},{y0:.2f} A{R},{R} 0 {large} 1 {x1:.2f},{y1:.2f}" fill="none" stroke="{COL[b]}" stroke-width="{w}"><title>{e(b)}: {v}</title></path>')
        a0 = a1
    label = ", ".join(f"{v} {b}" for b, v in data)
    legend = "".join(f'<li><span class="sw" style="background:{COL[b]}"></span>{e(b)} <b>{v}</b></li>' for b, v in data)
    return (f'<div class="dn"><svg viewBox="0 0 180 180" width="180" height="180" role="img" aria-label="Status breakdown: {e(label)}">'
            f'{"".join(parts)}<text x="90" y="88" text-anchor="middle" class="big">{len(rows)}</text>'
            f'<text x="90" y="108" text-anchor="middle" class="small">rows</text></svg><ul class="legend">{legend}</ul></div>')

def hbar(data, title, color="var(--accent)", colors=None):
    mx = max([v for _, v in data] + [1])
    lw, bw, h = 190, 250, 26
    H = h * len(data) + 6
    out = []
    for i, (k, v) in enumerate(data):
        y = i * h + 3
        wpx = bw * v / mx if v else 0
        c = colors.get(k, color) if colors else color
        out.append(f'<text x="{lw - 8}" y="{y + 16}" text-anchor="end" class="lab">{e(k)}</text>'
                   f'<rect x="{lw}" y="{y + 3}" width="{max(wpx, 1.5):.1f}" height="{h - 8}" rx="3" fill="{c}"><title>{e(k)}: {v}</title></rect>'
                   f'<text x="{lw + wpx + 6:.1f}" y="{y + 16}" class="val">{v}</text>')
    label = ", ".join(f"{k} {v}" for k, v in data)
    return (f'<svg viewBox="0 0 {lw + bw + 40} {H}" width="100%" role="img" aria-label="{e(title)}: {e(label)}">'
            f'{"".join(out)}</svg>')

def dash(v): return e(v) if str(v).strip() else "—"

show_deadline = any(r["deadline"].strip() for r in rows)
cols = ["Date"] + (["Deadline"] if show_deadline else []) + ["Company", "Role", "Sector", "Channel", "Fit", "Status", "Notes", "Source"]
rows_sorted = sorted(rows, key=lambda r: r["company"].lower())
rows_sorted = sorted(rows_sorted, key=lambda r: r["date"], reverse=True)
trs = []
for r in rows_sorted:
    note = r["notes"]
    short = note if len(note) <= 80 else note[:79] + "…"
    src = r["source"].strip()
    src_html = f'<a href="{e(src)}" target="_blank" rel="noopener">posting</a>' if src.startswith("http") else dash(src)
    cells = [dash(r["date"])] + ([dash(r["deadline"])] if show_deadline else []) + [
        dash(r["company"]), dash(r["role"]), dash(r["sector"]), dash(r["channel"]), dash(r["fit_rating"]),
        f'<span class="pill" style="background:{COL[r["_b"]]}">{e(r["_b"])}</span>',
        f'<span title="{e(note)}">{dash(short)}</span>', src_html]
    trs.append(f'<tr data-status="{e(r["_b"])}" data-sector="{e(r["sector"])}" '
               f'data-q="{e((r["company"] + " " + r["role"] + " " + r["sector"]).lower())}">'
               + "".join(f"<td>{c}</td>" for c in cells) + "</tr>")

# ---- LinkedIn outreach (network-queue.csv) ----
LI_COL = {"sent": "#3b82f6", "followed_up": "#f59e0b", "replied": "#22c55e", "no_reply": "#ef4444",
          "skipped": "#64748b", "drafted": "#94a3b8"}
LI_LABEL = {"sent": "Awaiting reply", "followed_up": "Followed up", "replied": "Replied",
            "no_reply": "No reply", "skipped": "Skipped", "drafted": "Drafted"}

def days_ago(d):
    try: return (date.today() - date.fromisoformat(d)).days
    except ValueError: return None

def linkedin_section():
    if not QUEUE.exists():
        return ""
    with open(QUEUE, encoding="utf-8") as f:
        q = list(csv.DictReader(f))
    msgd = [r for r in q if r.get("sent_on")]
    if not msgd and not any(r["status"] == "drafted" for r in q):
        return ""
    st = Counter(r["status"] for r in q)
    replied = [r for r in msgd if r["status"] == "replied"]
    waiting = [r for r in msgd if r["status"] in ("sent", "followed_up")]
    due = [r for r in msgd if r["status"] == "sent" and (days_ago(r["sent_on"]) or 0) >= 7]
    close = [r for r in msgd if r["status"] == "followed_up" and (days_ago(r["followup_on"]) or 0) >= 7]
    act = [r for r in replied if r.get("outcome") in ("referral", "call", "advice")]
    left = st["queued"]
    total_days = max([int(r["day"] or 0) for r in q] + [0])
    rate = f"{round(100 * len(replied) / len(msgd))}%" if msgd else "n/a"

    cards = [("Messaged", len(msgd), "#0f172a"), ("Replied", f"{len(replied)} <small>({rate})</small>", LI_COL["replied"]),
             ("Awaiting reply", len(waiting), LI_COL["sent"]), ("Follow-ups due", len(due), LI_COL["followed_up"]),
             ("Skipped", st["skipped"], LI_COL["skipped"]), ("Left in queue", left, "#94a3b8")]
    card_html = "".join(f'<div class="card" style="border-left-color:{c}"><div class="n">{n}</div>'
                        f'<div class="l">{e(t)}</div></div>' for t, n, c in cards)

    funnel_li = [("Messaged", len(msgd)), ("Replied", len(replied)),
                 ("Call / referral", sum(r.get("outcome") in ("call", "referral") for r in replied)),
                 ("Referral", sum(r.get("outcome") == "referral" for r in replied))]
    comp = Counter(r["company_group"] for r in msgd).most_common(8)

    def item(r, extra):
        return (f'<li><a href="{e(r["url"])}" target="_blank" rel="noopener">{e(r["name"].split(",")[0])}</a> '
                f'<span class="muted">· {e(r["company_group"])}</span> — {e(extra)}</li>')
    todo = ([item(r, f'{r["outcome"]}: {r.get("notes") or "reply received"}') for r in act]
            + [item(r, f'follow-up due, sent {days_ago(r["sent_on"])}d ago') for r in due]
            + [item(r, f'close as no reply, followed up {days_ago(r["followup_on"])}d ago') for r in close])
    next_due = min((date.fromisoformat(r["sent_on"]).toordinal() + 7 for r in waiting if r["status"] == "sent"), default=None)
    todo_html = ("<ul class=\"todo\">" + "".join(todo) + "</ul>") if todo else (
        f'<p class="muted">Nothing to act on today.'
        + (f' First follow-ups due {date.fromordinal(next_due).isoformat()}.' if next_due else "") + "</p>")

    trs = []
    for r in sorted(msgd, key=lambda r: (r["sent_on"], r["company_group"]), reverse=True):
        d = days_ago(r["sent_on"])
        stt = r["status"]
        trs.append(
            f'<tr><td><a href="{e(r["url"])}" target="_blank" rel="noopener">{e(r["name"].split(",")[0])}</a></td>'
            f'<td>{e(r["company_group"])}</td><td>{dash(r["position"])}</td>'
            f'<td>{e(r["sent_on"])} <span class="muted">({d}d)</span></td>'
            f'<td><span class="pill" style="background:{LI_COL.get(stt, "#64748b")}">{e(LI_LABEL.get(stt, stt))}</span></td>'
            f'<td>{dash(r.get("outcome", ""))}</td><td>{dash(r.get("notes", ""))}</td></tr>')

    return f"""
<h2 class="sec">LinkedIn outreach <span class="muted">· day {max([int(r["day"] or 0) for r in msgd] + [0])} of {total_days}</span></h2>
<section class="cards">{card_html}</section>
<section class="charts">
<div class="chart-card"><h3>Outreach funnel</h3>{hbar(funnel_li, "LinkedIn outreach funnel", colors={"Messaged": LI_COL["sent"], "Replied": LI_COL["replied"], "Call / referral": "#8b5cf6", "Referral": "#22c55e"})}</div>
<div class="chart-card"><h3>Needs action</h3>{todo_html}
<h3 style="margin-top:14px">Messaged by company</h3>{hbar(comp, "Messaged by company")}</div>
</section>
<section class="tablecard"><div class="tools"><h3>People messaged ({len(msgd)})</h3></div>
<div class="wrap"><table><thead><tr><th>Name</th><th>Company</th><th>Position</th><th>Sent</th><th>Status</th><th>Outcome</th><th>Notes</th></tr></thead>
<tbody>{"".join(trs)}</tbody></table></div>
<p class="note">One follow-up after 7 days with no reply; closed as no reply 7 days after that. Source: network-queue.csv.</p></section>"""


# ---- Cold email outreach (cold-email-targets.csv, written by tools/cold_email.py) ----
COLD = ROOT / "documents/context/cold-email-targets.csv"
CE_COL = {"sent": "#3b82f6", "followed_up": "#f59e0b", "replied": "#22c55e", "no_reply": "#ef4444",
          "bounced": "#b91c1c", "skipped": "#64748b", "queued": "#94a3b8"}
CE_LABEL = {"sent": "Awaiting reply", "followed_up": "Followed up", "replied": "Replied", "no_reply": "No reply",
            "bounced": "Bounced", "skipped": "Skipped", "queued": "Queued"}

def cold_email_section():
    if not COLD.exists():
        return ""
    sys.path.insert(0, str(ROOT / "tools"))
    import cold_email
    q = cold_email.load()
    mailed = [r for r in q if r["sent_on"]]
    if not mailed:
        return ""
    delivered = [r for r in mailed if r["status"] != "bounced"]
    replied = [r for r in mailed if r["status"] == "replied"]
    waiting = [r for r in mailed if r["status"] in ("sent", "followed_up")]
    bounced = [r for r in mailed if r["status"] == "bounced"]
    due = [r for r in mailed if r["status"] == "sent" and (days_ago(r["sent_on"]) or 0) >= 7]
    close = [r for r in mailed if r["status"] == "followed_up" and (days_ago(r["followup_on"]) or 0) >= 7]
    act = [r for r in replied if r["outcome"] in ("interview", "referral", "call", "advice")]
    rate = f"{round(100 * len(replied) / len(delivered))}%" if delivered else "n/a"
    cards = [("Emailed", len(mailed), "#0f172a"), ("Delivered", len(delivered), CE_COL["sent"]),
             ("Replied", f"{len(replied)} <small>({rate})</small>", CE_COL["replied"]),
             ("Awaiting reply", len(waiting), CE_COL["sent"]), ("Follow-ups due", len(due), CE_COL["followed_up"]),
             ("Bounced", len(bounced), CE_COL["bounced"])]
    card_html = "".join(f'<div class="card" style="border-left-color:{c}"><div class="n">{n}</div>'
                        f'<div class="l">{e(t)}</div></div>' for t, n, c in cards)
    funnel = [("Emailed", len(mailed)), ("Delivered", len(delivered)), ("Replied", len(replied)),
              ("Call / interview / referral", sum(r["outcome"] in ("call", "interview", "referral") for r in replied))]
    comp = Counter(r["company"] for r in delivered).most_common(10)
    by_type = []
    for t in ("recruiter", "peer", "lead"):
        d = [r for r in delivered if r["contact_type"] == t]
        if d:
            by_type.append((f"{t} ({len(d)} sent)", round(100 * sum(r["status"] == "replied" for r in d) / len(d))))

    def item(r, extra):
        return (f'<li><b>{e(r["name"])}</b> <span class="muted">· {e(r["company"])}</span> — {e(extra)}</li>')
    todo = ([item(r, f'{r["outcome"]}: {r["notes"][-120:]}') for r in act]
            + [item(r, f'follow-up due, sent {days_ago(r["sent_on"])}d ago') for r in due]
            + [item(r, f'close as no reply, followed up {days_ago(r["followup_on"])}d ago') for r in close]
            + [item(r, 'bounced: reach on LinkedIn or find another contact') for r in bounced])
    todo_html = ('<ul class="todo">' + "".join(todo) + "</ul>") if todo else '<p class="muted">Nothing to act on today.</p>'
    trs = []
    for r in sorted(mailed, key=lambda r: (r["sent_on"], r["company"]), reverse=True):
        src = r["source"].replace("LinkedIn people search ", "").replace("LinkedIn ", "").split(" ")[-1]
        name = (f'<a href="{e(src)}" target="_blank" rel="noopener">{e(r["name"])}</a>'
                if src.startswith("http") else e(r["name"]))
        stt = r["status"]
        trs.append(f'<tr><td>{name}</td><td>{e(r["company"])}</td><td>{dash(r["title"])}</td><td>{dash(r["contact_type"])}</td>'
                   f'<td>{e(r["email"])} <span class="muted">({e(r["confidence"])})</span></td>'
                   f'<td>{e(r["sent_on"])} <span class="muted">({days_ago(r["sent_on"])}d)</span></td>'
                   f'<td><span class="pill" style="background:{CE_COL.get(stt, "#64748b")}">{e(CE_LABEL.get(stt, stt))}</span></td>'
                   f'<td>{dash(r["outcome"])}</td></tr>')
    return f"""
<h2 class="sec">Cold email outreach <span class="muted">· {len({r["company"] for r in delivered})} companies</span></h2>
<section class="cards">{card_html}</section>
<section class="charts">
<div class="chart-card"><h3>Cold email funnel</h3>{hbar(funnel, "Cold email funnel", colors={"Emailed": "#0f172a", "Delivered": CE_COL["sent"], "Replied": CE_COL["replied"], "Call / interview / referral": "#8b5cf6"})}</div>
<div class="chart-card"><h3>Needs action</h3>{todo_html}
<h3 style="margin-top:14px">Reply rate % by contact type</h3>{hbar(by_type, "Reply rate by contact type") if by_type else '<p class="muted">No data yet.</p>'}
<h3 style="margin-top:14px">Delivered by company</h3>{hbar(comp, "Delivered by company")}</div>
</section>
<section class="tablecard"><div class="tools"><h3>People emailed ({len(mailed)})</h3></div>
<div class="wrap"><table><thead><tr><th>Name</th><th>Company</th><th>Title</th><th>Type</th><th>Email</th><th>Sent</th><th>Status</th><th>Outcome</th></tr></thead>
<tbody>{"".join(trs)}</tbody></table></div>
<p class="note">One follow-up after 7 days with no reply; closed as no reply 7 days after that. Source: cold-email-targets.csv (/coldemail).</p></section>"""


today = date.today().isoformat()
cards = [("Sent", len(sent), "#0f172a")] + [(b, by_bucket[b] if b != "Rejected/Closed" else by_bucket[b], COL[b]) for b in ORDER]
card_html = "".join(f'<div class="card" style="border-left-color:{c}"><div class="n">{n}</div><div class="l">{e(t)}</div></div>' for t, n, c in cards)
status_opts = "".join(f'<option>{e(b)}</option>' for b in ORDER if by_bucket[b])
sector_opts = "".join(f'<option>{e(s)}</option>' for s in sorted({r["sector"] for r in rows if r["sector"]}))
unk = f'<p class="note">Unrecognised status values counted as Rejected/Closed: {e(", ".join(sorted(unknown)))}</p>' if unknown else ""

page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Job Search Dashboard</title>
<style>
:root {{ --bg:#f5f6f8; --card:#fff; --text:#0f172a; --muted:#64748b; --line:#e2e8f0; --stripe:#f8fafc; --accent:#3b82f6; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg:#0f1115; --card:#181b21; --text:#e5e7eb; --muted:#94a3b8; --line:#2a2f38; --stripe:#1c2027; }} }}
:root[data-theme="dark"] {{ --bg:#0f1115; --card:#181b21; --text:#e5e7eb; --muted:#94a3b8; --line:#2a2f38; --stripe:#1c2027; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--text); font:14px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif; }}
main {{ max-width:1200px; margin:0 auto; padding:24px 16px; }}
header {{ display:flex; justify-content:space-between; align-items:baseline; flex-wrap:wrap; gap:8px; margin-bottom:18px; }}
h1 {{ margin:0; font-size:24px; }} .gen {{ color:var(--muted); }}
.cards {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(130px,1fr)); gap:12px; margin-bottom:18px; }}
.card {{ background:var(--card); border-radius:8px; box-shadow:0 1px 3px rgba(0,0,0,.08); padding:14px 16px; border-left:5px solid; }}
.card .n {{ font-size:28px; font-weight:700; line-height:1.1; }} .card .l {{ color:var(--muted); font-size:13px; }}
.charts {{ display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-bottom:18px; }}
@media (max-width:900px) {{ .charts {{ grid-template-columns:1fr; }} }}
.chart-card {{ background:var(--card); border-radius:8px; box-shadow:0 1px 3px rgba(0,0,0,.08); padding:14px 16px; min-width:0; }}
.chart-card h3 {{ margin:0 0 10px; font-size:15px; }}
.chart-card p {{ margin:8px 0 0; color:var(--muted); font-size:13px; }}
svg text {{ fill:var(--text); font-family:inherit; }} svg .lab {{ font-size:12px; }} svg .val {{ font-size:12px; font-weight:600; }}
svg .big {{ font-size:28px; font-weight:700; }} svg .small {{ font-size:12px; fill:var(--muted); }}
.dn {{ display:flex; align-items:center; gap:18px; flex-wrap:wrap; }}
.legend {{ list-style:none; margin:0; padding:0; }} .legend li {{ margin:4px 0; }}
.sw {{ display:inline-block; width:12px; height:12px; border-radius:3px; margin-right:8px; vertical-align:-1px; }}
.tablecard {{ background:var(--card); border-radius:8px; box-shadow:0 1px 3px rgba(0,0,0,.08); padding:14px 16px; }}
.tools {{ display:flex; gap:8px; flex-wrap:wrap; align-items:center; margin-bottom:10px; }}
.tools h3 {{ margin:0 auto 0 0; font-size:15px; }}
select, input {{ font:inherit; padding:6px 8px; border:1px solid var(--line); border-radius:6px; background:var(--card); color:var(--text); }}
.wrap {{ overflow-x:auto; }}
table {{ width:100%; border-collapse:collapse; font-size:13px; }}
th, td {{ text-align:left; padding:7px 8px; border-bottom:1px solid var(--line); vertical-align:top; }}
th {{ color:var(--muted); font-weight:600; white-space:nowrap; }}
tbody tr:nth-child(even) {{ background:var(--stripe); }}
td:first-child {{ white-space:nowrap; }}
.pill {{ color:#fff; padding:2px 9px; border-radius:999px; font-size:12px; white-space:nowrap; }}
a {{ color:var(--accent); }}
.note {{ color:var(--muted); font-size:13px; }}
.muted {{ color:var(--muted); }}
h2.sec {{ font-size:19px; margin:30px 0 12px; }} .card small {{ font-size:14px; color:var(--muted); font-weight:500; }}
.todo {{ margin:0; padding-left:18px; }} .todo li {{ margin:4px 0; }}
footer {{ color:var(--muted); text-align:center; margin:22px 0 6px; font-size:12px; }}
</style></head><body><main>
<header><h1>🔍 Job Search Dashboard</h1><span class="gen">Generated: {today}</span></header>
<h2 class="sec" style="margin-top:0">Applications</h2>
<section class="cards">{card_html}</section>
{unk}
<section class="charts">
<div class="chart-card"><h3>Status breakdown</h3>{doughnut()}</div>
<div class="chart-card"><h3>By sector</h3>{hbar(by_sector, "Applications by sector")}</div>
<div class="chart-card"><h3>By channel</h3>{hbar(by_channel, "Applications by channel")}</div>
<div class="chart-card"><h3>Application funnel</h3>{hbar(funnel, "Funnel", colors={"Applied": COL["Active"], "Interview": COL["Interview"], "Offer": COL["Offer"], "Hired": COL["Hired"]})}
<p>{pct}% progressed past resume screen · rejection rate: {e(rej_rate)}</p></div>
</section>
<section class="tablecard">
<div class="tools"><h3>Applications</h3>
<select id="fs" aria-label="Filter by status"><option value="">All statuses</option>{status_opts}</select>
<select id="fsec" aria-label="Filter by sector"><option value="">All sectors</option>{sector_opts}</select>
<input id="q" type="search" placeholder="🔍 Search company, role, sector" aria-label="Search"></div>
<div class="wrap"><table><thead><tr>{"".join(f"<th>{c}</th>" for c in cols)}</tr></thead>
<tbody id="tb">{"".join(trs)}</tbody></table></div>
<p class="note" id="shown"></p>
</section>
{linkedin_section()}
{cold_email_section()}
<footer>Generated by Claude Code · ai-job-search · {today}</footer>
</main>
<script>
const fs = document.getElementById("fs"), fsec = document.getElementById("fsec"), q = document.getElementById("q");
const rows = [...document.querySelectorAll("#tb tr")];
function apply() {{
  const s = fs.value, sec = fsec.value, t = q.value.trim().toLowerCase();
  let n = 0;
  rows.forEach(r => {{
    const ok = (!s || r.dataset.status === s) && (!sec || r.dataset.sector === sec) && (!t || r.dataset.q.includes(t));
    r.style.display = ok ? "" : "none"; if (ok) n++;
  }});
  document.getElementById("shown").textContent = n + " of " + rows.length + " shown";
}}
[fs, fsec].forEach(el => el.addEventListener("change", apply)); q.addEventListener("input", apply); apply();
</script></body></html>"""

args = [a for a in sys.argv[1:] if a != "--open"]
out = Path(args[0]).expanduser() if args else ROOT / "reports/application-dashboard.html"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(page, encoding="utf-8")
print(json.dumps({"rows": len(rows), "sent": len(sent), "drafted": drafted, "buckets": dict(by_bucket),
                  "funnel": funnel, "pct": pct, "rej": rej_rate, "channels": by_channel, "sectors": len(by_sector),
                  "outcomes_merged": sum(bool(r["_outcome"]) for r in rows), "unknown": sorted(unknown)}))

if "--open" in sys.argv:
    webbrowser.open(out.resolve().as_uri())
