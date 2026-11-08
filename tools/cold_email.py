"""Cold-email outreach tracker for /coldemail.

Tracker: documents/context/cold-email-targets.csv (one row per person emailed or queued).
Status flow: queued -> sent -> (followed_up) -> replied | no_reply ; or bounced / skipped.

Usage:
  python tools/cold_email.py --report                    # replies to act on, follow-ups due, bounces, waiting
  python tools/cold_email.py --contacted "<name|email|company>"   # exit 0 + rows if already contacted (dedup)
  python tools/cold_email.py --sync-list                 # emails + sent dates to check for replies/bounces in Gmail
  python tools/cold_email.py --mark sent|bounced|followed_up|no_reply|skipped "<name or email>" ... [--note N] [--date D]
  python tools/cold_email.py --reply "<name or email>" --outcome interview|referral|call|advice|not_hiring|declined --note "..."
  python tools/cold_email.py --add-batch batch.json      # append rows (fields below) as status=sent, sent_on=today
  python tools/cold_email.py --compose-urls batch.json   # print Gmail compose URLs (one per line: index email url)

batch.json: list of {co,name,first,title,url,email,basis,conf,cv,subj,body} (body without the "Hi X," line).
"""
import argparse, csv, json, sys, urllib.parse
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRACKER = ROOT / "documents/context/cold-email-targets.csv"
FIELDS = ["date", "company", "name", "title", "contact_type", "location", "source", "email", "email_basis",
          "confidence", "status", "sent_on", "followup_on", "replied_on", "outcome", "notes"]
# contact_type: recruiter (TA / HR / campus), peer (someone in Adel's target role), lead (team lead / hiring manager / founder)
NO_REPLY_DAYS = 21


def load():
    if not TRACKER.exists():
        return []
    with open(TRACKER, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for k in FIELDS:
            r.setdefault(k, "")
        if not r["contact_type"] and r["sent_on" if r.get("sent_on") else "date"]:
            t = r["title"].lower()
            r["contact_type"] = ("recruiter" if any(w in t for w in ("talent", "recruit", "hr", "people", "sourc", "ta leader", "ta partner"))
                                 else "lead" if any(w in t for w in ("head", "lead", "manager", "director", "founder", "vp"))
                                 else "peer")
        # legacy rows (before sent_on existed): status text like "sent" / "bounced (...)"
        if not r["sent_on"] and r["status"].startswith(("sent", "bounced")):
            r["sent_on"] = r["date"]
        if r["status"].startswith("bounced"):
            if r["status"] != "bounced":
                r["notes"] = (r["notes"] + " | " if r["notes"] else "") + r["status"]
            r["status"] = "bounced"
        if r["status"].startswith("not sent"):
            r["notes"] = (r["notes"] + " | " if r["notes"] else "") + r["status"]
            r["status"] = "skipped"
    return rows


def save(rows):
    TRACKER.parent.mkdir(parents=True, exist_ok=True)
    with open(TRACKER, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def days_ago(d):
    try:
        return (date.today() - date.fromisoformat(d)).days
    except ValueError:
        return None


def match(rows, key):
    k = key.lower().strip()
    hits = [r for r in rows if k in (r["name"].lower(), r["email"].lower())]
    if not hits:
        hits = [r for r in rows if k in r["name"].lower() or k in r["email"].lower()]
    return hits


def report(rows):
    sent = [r for r in rows if r["sent_on"] and r["status"] != "bounced"]
    replied = [r for r in rows if r["status"] == "replied"]
    act = [r for r in replied if r["outcome"] in ("interview", "referral", "call", "advice")]
    # No follow-ups (Adel, 2026-10-19: following up is spamming). Unanswered
    # emails are simply closed as no_reply after NO_REPLY_DAYS.
    close = [r for r in rows if r["status"] in ("sent", "followed_up")
             and (days_ago(r["sent_on"]) or 0) >= NO_REPLY_DAYS]
    waiting = [r for r in rows if r["status"] in ("sent", "followed_up")]
    bounced = [r for r in rows if r["status"] == "bounced"]
    rate = f"{round(100 * len(replied) / len(sent))}%" if sent else "n/a"
    print(f"# Cold email report - {date.today().isoformat()}\n")
    print(f"Delivered {len(sent)} | replied {len(replied)} ({rate}) | bounced {len(bounced)} | "
          f"companies {len({r['company'] for r in sent})}")
    for t in ("recruiter", "peer", "lead"):
        d = [r for r in sent if r["contact_type"] == t]
        if d:
            rr = sum(r["status"] == "replied" for r in d)
            print(f"  {t}: {len(d)} delivered, {rr} replied ({round(100 * rr / len(d))}%)")
    print()
    for title, lst, fmt in [
        ("Replies to act on", act, lambda r: f"{r['outcome']}: {r['notes'] or 'reply received'}"),
        (f"Close as no reply (sent {NO_REPLY_DAYS}+ days ago; never follow up)", close,
         lambda r: f"sent {days_ago(r['sent_on'])}d ago"),
        ("Bounced (find another route: LinkedIn / other contact)", bounced, lambda r: r["notes"][-80:]),
        ("Waiting", waiting, lambda r: f"sent {days_ago(r['sent_on'])}d ago"),
    ]:
        print(f"## {title} ({len(lst)})")
        for r in lst:
            print(f"- {r['name']} ({r['company']}, {r['email']}): {fmt(r)}")
        if not lst:
            print("none")
        print()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--contacted")
    ap.add_argument("--sync-list", action="store_true")
    ap.add_argument("--mark", nargs="+", metavar=("STATUS", "PERSON"))
    ap.add_argument("--reply")
    ap.add_argument("--outcome", choices=["interview", "referral", "call", "advice", "not_hiring", "declined"])
    ap.add_argument("--note", default="")
    ap.add_argument("--date", default=date.today().isoformat())
    ap.add_argument("--add-batch")
    ap.add_argument("--compose-urls")
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    rows = load()

    if a.report:
        report(rows)
    elif a.contacted:
        hits = match(rows, a.contacted) or [r for r in rows if a.contacted.lower() in r["company"].lower()]
        for r in hits:
            print(f"{r['status']}\t{r['sent_on']}\t{r['company']}\t{r['name']}\t{r['email']}")
        sys.exit(0 if hits else 1)
    elif a.sync_list:
        for r in rows:
            if r["status"] in ("sent", "followed_up"):
                print(f"{r['email']}\t{r['sent_on']}\t{r['name']}\t{r['company']}")
    elif a.mark:
        status, people = a.mark[0], a.mark[1:]
        for p in people:
            hits = match(rows, p)
            if len(hits) != 1:
                print(f"  ? {p}: {len(hits)} matches, skipped")
                continue
            r = hits[0]
            r["status"] = status
            if status == "sent" and not r["sent_on"]:
                r["sent_on"] = a.date
            if status == "followed_up":
                r["followup_on"] = a.date
            if a.note:
                r["notes"] = (r["notes"] + " | " if r["notes"] else "") + f"{a.date}: {a.note}"
            print(f"  {r['name']} ({r['company']}) -> {status}")
        save(rows)
    elif a.reply:
        hits = match(rows, a.reply)
        if len(hits) != 1:
            sys.exit(f"{a.reply}: {len(hits)} matches")
        r = hits[0]
        r.update(status="replied", replied_on=a.date, outcome=a.outcome or "")
        if a.note:
            r["notes"] = (r["notes"] + " | " if r["notes"] else "") + f"{a.date}: {a.note}"
        save(rows)
        print(f"  {r['name']} ({r['company']}) replied: {r['outcome']}")
    elif a.add_batch:
        batch = json.load(open(a.add_batch, encoding="utf-8"))
        seen = {r["email"].lower() for r in rows}
        n = 0
        for e in batch:
            if e["email"].lower() in seen:
                continue
            rows.append(dict(date=a.date, company=e["co"], name=e["name"], title=e.get("title", ""),
                             contact_type=e.get("type", ""), location="UAE",
                             source="LinkedIn " + e.get("url", ""), email=e["email"], email_basis=e.get("basis", ""),
                             confidence=e.get("conf", ""), status="sent", sent_on=a.date, followup_on="",
                             replied_on="", outcome="", notes=f"subject: {e['subj']} | CV cv/{e.get('cv', '')}"))
            n += 1
        save(rows)
        print(f"added {n}")
    elif a.compose_urls:
        batch = json.load(open(a.compose_urls, encoding="utf-8"))
        for i, e in enumerate(batch):
            body = f"Hi {e['first']},\n\n{e['body']}"
            url = ("https://mail.google.com/mail/u/0/?view=cm&fs=1&tf=1&to=" + urllib.parse.quote(e["email"])
                   + "&su=" + urllib.parse.quote(e["subj"]) + "&body=" + urllib.parse.quote(body))
            print(i, e["email"], url)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
