"""Send a /coldemail batch from Adel's Gmail over SMTP, each email with its tailored CV attached.

Credentials come from the gitignored .env in the repo root (Adel fills it in himself):
  GMAIL_ADDRESS=adelahmad2005@gmail.com
  GMAIL_APP_PASSWORD=<16-character Google app password>

Usage:
  python tools/send_cold_emails.py <batch.json> --dry-run        # show what would be sent, send nothing
  python tools/send_cold_emails.py <batch.json> [--delay 20] [--limit N]

batch.json: list of {co,name,first,title,url,email,basis,conf,cv,subj,body}; body excludes the "Hi X," line.
`cv` is a PDF path relative to cv/ (e.g. main_cold_g42.pdf); it is attached as Adel_Abdelmoaty_Resume.pdf.
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

ATTACH_NAME = "Adel_Abdelmoaty_Resume.pdf"


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
    pdf = ROOT / "cv" / e["cv"]
    m.add_attachment(pdf.read_bytes(), maintype="application", subtype="pdf", filename=ATTACH_NAME)
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("batch")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--delay", type=float, default=20, help="seconds between emails (default 20)")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    batch = json.load(open(a.batch, encoding="utf-8"))
    rows = cold_email.load()
    done = {r["email"].lower() for r in rows}
    todo, problems = [], []
    for e in batch:
        if e["email"].lower() in done:
            print(f"  skip (already in tracker): {e['name']} <{e['email']}>")
            continue
        if not (ROOT / "cv" / e["cv"]).exists():
            problems.append(f"missing CV cv/{e['cv']} for {e['name']}")
            continue
        todo.append(e)
    if problems:
        sys.exit("\n".join(problems))
    if a.limit:
        todo = todo[: a.limit]

    if a.dry_run:
        for e in todo:
            print(f"- {e['name']} ({e['co']}) <{e['email']}> | {e['subj']} | cv/{e['cv']}")
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
        seen = {r["email"].lower() for r in rows}
        today = date.today().isoformat()
        for e in sent:
            if e["email"].lower() in seen:
                continue
            rows.append(dict(date=today, company=e["co"], name=e["name"], title=e.get("title", ""), location="UAE",
                             source="LinkedIn " + e.get("url", ""), email=e["email"], email_basis=e.get("basis", ""),
                             confidence=e.get("conf", ""), status="sent", sent_on=today, followup_on="",
                             replied_on="", outcome="", notes=f"type: {e.get('type', '')} | subject: {e['subj']} | CV cv/{e['cv']}",
                             contact_type=e.get("type", "")))
        cold_email.save(rows)
    print(f"done: {len(sent)} sent, tracker updated. Check bounces in ~2 minutes: python tools/cold_email.py --report")


if __name__ == "__main__":
    main()
