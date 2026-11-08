"""Send a /coldemail batch from Adel's Gmail over SMTP. Plain text, NO attachments (Adel, 2026-11-08:
no CV on cold emails, ever; a brief, human referral ask instead).

Credentials come from the gitignored .env in the repo root (Adel fills it in himself):
  GMAIL_ADDRESS=adelahmad2005@gmail.com
  GMAIL_APP_PASSWORD=<16-character Google app password>

Usage:
  python tools/send_cold_emails.py <batch.json> --dry-run        # show what would be sent, send nothing
  python tools/send_cold_emails.py <batch.json> [--delay 20] [--limit N]

batch.json: list of {co,name,first,title,type,url,email,basis,conf,evidence,subj,body}; body excludes the "Hi X,"
line. Rows are refused unless conf is "verified" or "high" AND evidence (URLs proving the address/format) is set.
The whole run is refused if any email bounced in the last 7 days, unless --allow-after-bounce.
A `cv` key, if present in an old batch, is ignored: nothing is ever attached.
Every email sent is added to documents/context/cold-email-targets.csv (status sent). People already in the
tracker are skipped, so re-running a batch never double-sends. Emails land in Gmail's Sent folder as usual.
"""
import argparse, json, smtplib, sys, time
from datetime import date
from email.message import EmailMessage
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import cold_email  # noqa: E402

BOUNCE_PAUSE_DAYS = 7


def load_env():
    env = {}
    p = ROOT / ".env"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def build(e, sender):
    m = EmailMessage()
    m["From"] = f"Adel Abdelmoaty <{sender}>"
    m["To"] = e["email"]
    m["Subject"] = e["subj"]
    m.set_content(f"Hi {e['first']},\n\n{e['body']}\n")
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("batch")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--delay", type=float, default=20, help="seconds between emails (default 20)")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--allow-after-bounce", action="store_true",
                    help="send despite a bounce in the last 7 days (only with Adel's explicit OK)")
    ap.add_argument("--allow-company-repeat", action="store_true",
                    help="skip the 7-day gap between people at one company (only with Adel's explicit OK)")
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    batch = json.load(open(a.batch, encoding="utf-8"))
    rows = cold_email.load()

    # Deliverability guard (Adel, 2026-09-29): bounce budget is at most 1 per 1-2 weeks.
    recent = [r for r in rows if r["status"] == "bounced" and (cold_email.days_ago(r["sent_on"]) or 99) < BOUNCE_PAUSE_DAYS]
    if recent and not a.allow_after_bounce and not a.dry_run:
        last = max(r["sent_on"] for r in recent)
        sys.exit(f"Paused: {len(recent)} bounce(s) in the last {BOUNCE_PAUSE_DAYS} days (latest {last}). "
                 f"Re-verify formats, then ask Adel before re-running with --allow-after-bounce.")

    # queued rows were researched but never emailed, so they are still sendable
    done = {r["email"].lower() for r in rows if r["email"] and r["status"] != "queued"}
    todo, problems, batch_cos = [], [], set()
    for e in batch:
        if e["email"].lower() in done:
            print(f"  skip (already in tracker): {e['name']} <{e['email']}>")
            continue
        # One person per company per run, and 7+ days since the last email there (Adel, 2026-10-19)
        co = e["co"].casefold()
        if co in batch_cos:
            print(f"  REFUSED (second person at {e['co']} in one run): {e['name']} <{e['email']}>")
            continue
        last = [cold_email.days_ago(r["sent_on"]) for r in rows
                if r["sent_on"] and r["company"].casefold() == co]
        if last and min(d for d in last if d is not None) < 7 and not a.allow_company_repeat:
            print(f"  REFUSED ({e['co']} emailed under 7 days ago): {e['name']} <{e['email']}>")
            continue
        batch_cos.add(co)
        if e.get("conf") not in ("verified", "high") or not e.get("evidence"):
            print(f"  REFUSED (address not proven - conf={e.get('conf')!r}, evidence missing?): "
                  f"{e['name']} <{e['email']}> -> contact on LinkedIn instead")
            continue
        todo.append(e)
    if problems:
        sys.exit("\n".join(problems))
    if a.limit:
        todo = todo[: a.limit]

    if a.dry_run:
        for e in todo:
            print(f"- {e['name']} ({e['co']}) <{e['email']}> | {e['subj']} | no attachment")
            print(f"    Hi {e['first']},\n    " + e["body"].replace("\n", "\n    "))
        print(f"{len(todo)} would be sent")
        return

    env = load_env()
    sender, pw = env.get("GMAIL_ADDRESS"), env.get("GMAIL_APP_PASSWORD", "").replace(" ", "")
    if not sender or not pw or pw.startswith("PASTE"):
        sys.exit("Fill GMAIL_ADDRESS and GMAIL_APP_PASSWORD in .env first (see the header of this file).")

    sent = []
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=60) as s:
        s.login(sender, pw)
        for i, e in enumerate(todo):
            try:
                s.send_message(build(e, sender))
                sent.append(e)
                print(f"  sent {i + 1}/{len(todo)}: {e['name']} ({e['co']}) <{e['email']}>")
            except smtplib.SMTPRecipientsRefused as err:
                print(f"  refused: {e['email']} {err}")
            if i < len(todo) - 1:
                time.sleep(a.delay)

    if sent:
        rows = cold_email.load()
        by_email = {r["email"].lower(): r for r in rows if r["email"]}
        today = date.today().isoformat()
        for e in sent:
            row = by_email.get(e["email"].lower())
            if row:
                if row["status"] == "queued":
                    row.update(status="sent", sent_on=today, confidence=e.get("conf", ""),
                               notes=(row["notes"] + " | " if row["notes"] else "")
                               + f"subject: {e['subj']} | no CV")
                continue
            rows.append(dict(date=today, company=e["co"], name=e["name"], title=e.get("title", ""), location="UAE",
                             source="LinkedIn " + e.get("url", ""), email=e["email"], email_basis=e.get("basis", ""),
                             confidence=e.get("conf", ""), status="sent", sent_on=today, followup_on="",
                             replied_on="", outcome="", notes=f"type: {e.get('type', '')} | subject: {e['subj']} | no CV",
                             contact_type=e.get("type", "")))
        cold_email.save(rows)
    print(f"done: {len(sent)} sent, tracker updated. Check bounces in ~2 minutes: python tools/cold_email.py --report")


if __name__ == "__main__":
    main()
