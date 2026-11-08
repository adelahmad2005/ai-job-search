"""Rank LinkedIn connections for referral outreach and keep a daily message queue.

Reads the official LinkedIn data export (Settings > Data privacy > Get a copy of
your data > Connections), keeps every employed connection except Dell and students, scores them
by company tier and role relevance, and drops anyone already in the outreach log.

The ranked list is split into daily batches (at most 2 people per company per day,
so one team doesn't get the same message on the same morning) and written to
documents/context/network-queue.csv. Re-running keeps each person's status
and tracking dates (sent, followed up, replied, outcome, notes), matched by profile URL.

Usage:
    python tools/network_rank.py [Connections.csv] [--per-day 10] [--top 30]
    python tools/network_rank.py --next                      # next day's batch
    python tools/network_rank.py --mark sent "Amit Menon" "Osama"   # also: drafted, followed_up, skipped
    python tools/network_rank.py --reply "Amit" --outcome call --note "call Tue 3pm"
    python tools/network_rank.py --report                    # follow-ups due, replies, waiting

No scraping: the input is LinkedIn's own export.
"""
import argparse
import csv
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CSV = ROOT / "documents/context/Connections.csv"
QUEUE_CSV = ROOT / "documents/context/network-queue.csv"
SUMMARY_MD = ROOT / "documents/context/network-by-company.md"
OUTREACH_LOG = ROOT / "documents/context/outreach-log.md"

# Everyone employed is kept; only Dell (Adel handles those himself, 2026-09-27),
# students and people with no employer listed are dropped.
DELL = r"\bdell\b"
STUDENT_ORG = (r"club|society|chapter|student|council|honou?r|tau beta|pi tau|beta gamma|"
               r"alpha lambda|google developers? groups?|180 degrees|launchpad|ieee|asme|aiche|"
               r"youth|medhack|techtatva|math challenge|ada club|aus press|aus racing|cultural")
ACADEMIC = r"universit|college|school|institute|academy|kaust|mbzuai|massachusetts"
STUDENT_ROLE = (r"student|research assistant|teaching assistant|resident assistant|lab assistant|"
                r"grader|peer|tutor|ambassador|club|president|treasurer|committee|member|"
                r"visiting|ecorep|leadership program|intern|professor's assistant|^assistant$|"
                r"orientation|team leader|sharakah|chapter|media coordinator|social media")
# Lowest tier: no employer who could refer (freelance, bug-bounty hunters, hidden).
LOW = (r"^(freelance|freelancer|self-employed|confidential|confidencial\.io|nda|undernda|"
       r"\[redacted\]|stealth.*)$|hackerone|bugcrowd|intigriti|synack|cobalt|0xl4ugh")

# Tier 1: Adel's lanes (security, AI, infrastructure vendors, tech consulting,
# UAE integrators/distributors). Tier 2: large or well-known UAE employers.
TIER1 = {
    "NVIDIA": r"nvidia", "Red Hat": r"red ?hat", "VMware/Broadcom": r"vmware|broadcom",
    "IBM": r"\bibm\b", "Microsoft": r"^microsoft", "Cisco": r"cisco", "Palo Alto Networks": r"palo ?alto",
    "Fortinet": r"fortinet", "Help AG": r"help ?ag\b", "CPX": r"\bcpx\b", "G42/Core42": r"\bg42\b|core ?42",
    "Presight": r"presight", "Moro Hub": r"moro hub", "Digital Dubai": r"digital dubai",
    "Deloitte": r"deloitte", "PwC": r"\bpwc\b|pricewaterhouse", "EY": r"^ey\b|ernst", "KPMG": r"kpmg",
    "Accenture": r"accenture", "Capgemini": r"capgemini", "Protiviti": r"protiviti",
    "Grant Thornton": r"grant thornton", "BCG": r"boston consulting|\bbcg\b", "McKinsey": r"mckinsey",
    "Kaspersky": r"kaspersky|касперск", "Group-IB": r"group-ib", "Cipher": r"^cipher",
    "COGNNA": r"cognna", "Cyber 50 Defense": r"cyber 50", "CrowdStrike": r"crowdstrike",
    "Darktrace": r"darktrace", "Splunk": r"splunk", "Cloudflare": r"cloudflare", "F5": r"^f5$",
    "Nozomi Networks": r"nozomi", "Positive Technologies": r"positive technologies",
    "Thales": r"thales", "Check Point": r"check ?point", "Trend Micro": r"trend ?micro",
    "HPE": r"hewlett|\bhpe\b", "Nutanix": r"nutanix", "Databricks": r"databricks",
    "Canonical": r"canonical", "Cohere": r"^cohere$", "World Wide Technology": r"world wide technology",
    "Google": r"^google$|google cloud", "AWS/Amazon": r"^amazon|\baws\b", "Oracle": r"^oracle",
    "SAP": r"^sap\b", "Atos": r"^atos", "InterSystems": r"intersystems",
    "Mindware": r"mindware", "GulfIT": r"gulfit", "Beta IT": r"beta information technology",
    "Emircom": r"emircom", "Netways": r"^netways", "Spire Solutions": r"spire solutions",
    "Inspira": r"inspira enterprise", "BluSapphire": r"blusapphire", "Injazat": r"injazat",
    "GBM": r"gulf business machines|\bgbm\b", "Ingram Micro": r"ingram", "e&": r"^e&|etisalat|help ag",
    "du": r"^du$|emirates integrated telecom", "MBZUAI": r"mbzuai", "Odoo": r"^odoo",
}
TIER2 = {
    "Emirates Group": r"^emirates$|emirates group", "noon": r"^noon$", "Careem": r"careem",
    "Tabby": r"tabby", "Wio Bank": r"wio bank", "Emirates NBD": r"emirates nbd", "Mashreq": r"mashreq",
    "FAB": r"first abu dhabi", "ADCB": r"\badcb\b", "Standard Chartered": r"standard chartered",
    "CBI": r"commercial bank international", "Arab Bank": r"^arab bank", "Sharjah Islamic Bank": r"sharjah islamic",
    "Invest Bank": r"invest bank", "Visa": r"^visa\b", "Mastercard": r"mastercard", "geidea": r"geidea",
    "NymCard": r"nymcard", "Arqaam Capital": r"arqaam", "Dubai Financial Market": r"dubai financial market",
    "ADGM": r"^adgm", "DIFC": r"\bdifc\b", "Aon": r"^aon$",
    "ADNOC": r"adnoc", "ENOC": r"^enoc", "EGA": r"emirates global aluminium", "DEWA": r"dewa|dubai electricity",
    "RTA": r"roads and transport", "DP World": r"dp world", "Dubai Holding": r"dubai holding",
    "Emaar": r"^emaar", "Expo City Dubai": r"expo city", "Mubadala": r"mubadala",
    "Dubizzle/Bayut": r"dubizzle|bayut", "Chalhoub": r"chalhoub", "Al Tayer": r"al tayer",
    "Americana": r"americana", "Majid Al Futtaim": r"majid al futtaim",
    "Schneider Electric": r"schneider", "Siemens": r"^siemens", "Samsung": r"samsung", "Sony": r"^sony",
    "SLB": r"^slb$|schlumberger", "Emerson": r"^emerson", "Eaton": r"^eaton", "AVEVA": r"^aveva",
    "P&G": r"procter", "Unilever": r"unilever", "PepsiCo": r"pepsico", "L'Oréal": r"l.or[eé]al",
    "Henkel": r"henkel", "BMW": r"bmw", "General Motors": r"general motors",
    "TCS": r"tata consultancy", "HCLTech": r"hcltech", "Cognizant": r"cognizant",
    "Publicis Sapient": r"publicis sapient", "Synechron": r"synechron", "Transmed": r"transmed",
    "Khalifa University": r"khalifa university", "Federal Tax Authority": r"federal tax authority",
    "TDRA": r"telecommunications and digital government", "Sharjah Digital": r"sharjah digital",
    "Dubai Police": r"dubai police", "Al Tamimi": r"al tamimi", "A&O Shearman": r"a&o shearman",
}

HIRES = r"recruit|career services|talent|hiring|\bhr\b|human resources|people partner|campus|early careers"
LANE = (r"presales|pre-sales|solution|architect|security|cyber|\bai\b|machine learning|data|"
        r"engineer|consult|automation|cloud|infrastructure|services|customer success|analyst|"
        r"soc\b|grc|threat|incident|dfir|developer|software|finance|financial")
SENIOR = r"head|director|manager|lead|principal|vp|vice president|partner|chief"
TOP = r"\bchief\b|\bceo\b|\bcto\b|\bciso\b|\bsvp\b|\bevp\b|senior vice president|global head|founder"
JUNIOR = r"\bintern\b|internship|trainee|\bstudent\b|inten\b"
TECH_CO = (r"cyber|secur|\bsoc\b|tech|\bai\b|data|digital|software|\bit\b|infotech|"
           r"solutions|systems|cloud|network|redforce|haboob|callsign|consult|bank|capital|financ")
STATUSES = ("queued", "drafted", "sent", "followed_up", "replied", "no_reply", "skipped")
OUTCOMES = ("referral", "call", "advice", "pending", "not_hiring", "declined")
TRACK = ("sent_on", "followup_on", "replied_on", "outcome", "notes")
NO_REPLY_AFTER = 21   # days after sending with no reply: mark no_reply (never follow up - Adel, 2026-10-19)


def load_connections(path):
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    # The export starts with a "Notes:" preamble before the real header row.
    start = next((i for i, l in enumerate(lines) if l.startswith("First Name")), None)
    if start is None:
        sys.exit(f"No 'First Name' header found in {path}; is this LinkedIn's Connections.csv?")
    return list(csv.DictReader(lines[start:]))


def is_student(company, position):
    c, p = company.lower(), position.lower()
    if re.search(STUDENT_ORG, c) or re.search(r"\bstudent\b", p):
        return True
    return bool(re.search(ACADEMIC, c) and re.search(STUDENT_ROLE, p))


def match_company(company, position):
    """Return (tier, group). Tier 0 = drop."""
    c = company.lower().strip()
    if not c or re.search(DELL, c) or is_student(company, position):
        return 0, ""
    if re.search(LOW, c):
        return 4, company.strip()
    for tier, table in ((1, TIER1), (2, TIER2)):
        for name, pat in table.items():
            if re.search(pat, c):
                return tier, name
    if re.search(r"american university of sharjah|amerian university", c):
        return 3, "AUS (staff)"
    return 3, company.strip()


def score(tier, position, company=""):
    p = position.lower()
    s = {1: 6, 2: 4, 3: 1, 4: 0}[tier]
    reasons = []
    if tier == 3 and re.search(TECH_CO, company.lower()):
        s += 1; reasons.append("tech/security company")
    if re.search(HIRES, p):
        s += 3; reasons.append("hires")
    if re.search(LANE, p):
        s += 2; reasons.append("your lane")
    if re.search(TOP, p):
        s -= 2; reasons.append("very senior, harder ask")
    elif re.search(SENIOR, p):
        s += 1; reasons.append("senior")
    if re.search(JUNIOR, p):
        s -= 3; reasons.append("intern, can't refer much")
    return s, reasons


def already_contacted():
    if not OUTREACH_LOG.exists():
        return ""
    return OUTREACH_LOG.read_text(encoding="utf-8").lower()


def read_queue():
    if not QUEUE_CSV.exists():
        return []
    with QUEUE_CSV.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_queue(rows):
    with QUEUE_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)


def assign_days(rows, per_day, per_company=2):
    """Batch in rank order; cap each company per day so messages are spread out."""
    days = defaultdict(Counter)   # day -> company -> count
    size = Counter()              # day -> people
    for r in rows:
        d = 1
        while size[d] >= per_day or days[d][r["company_group"]] >= per_company:
            d += 1
        r["day"] = d
        size[d] += 1
        days[d][r["company_group"]] += 1


def build(args):
    path = Path(args.csv)
    if not path.exists():
        sys.exit(f"{path} not found. Request the LinkedIn export and save Connections.csv there.")

    old = {r["url"]: r for r in read_queue()}
    log = already_contacted()
    rows, skipped = [], 0
    for c in load_connections(path):
        name = f"{c.get('First Name', '')} {c.get('Last Name', '')}".strip()
        position = c.get("Position", "").strip()
        tier, group = match_company(c.get("Company", ""), position)
        if not tier:
            continue
        if name and name.lower() in log:
            skipped += 1
            continue
        s, reasons = score(tier, position, c.get("Company", ""))
        url = c.get("URL", "")
        prev = old.get(url, {})
        rows.append({
            "rank": 0, "day": 0, "status": prev.get("status", "queued"),
            "score": s, "tier": tier, "name": name, "company_group": group,
            "company": c.get("Company", "").strip(), "position": position,
            "why": ", ".join(reasons), "url": url, "connected_on": c.get("Connected On", ""),
            **{k: prev.get(k, "") for k in TRACK},
        })

    rows.sort(key=lambda r: (-r["score"], r["tier"], r["company_group"], r["name"]))
    for i, r in enumerate(rows, 1):
        r["rank"] = i
    # People already handled keep their place; only queued people get (re)batched.
    done = [r for r in rows if r["status"] != "queued"]
    for r in done:
        r["day"] = old.get(r["url"], {}).get("day", 0)
    offset = max([int(r["day"] or 0) for r in done] + [0])
    queued = [r for r in rows if r["status"] == "queued"]
    assign_days(queued, args.per_day)
    for r in queued:
        r["day"] += offset
    QUEUE_CSV.parent.mkdir(parents=True, exist_ok=True)
    write_queue(rows)
    write_summary(rows)

    by_status = Counter(r["status"] for r in rows)
    last_day = max((int(r["day"]) for r in rows), default=0)
    print(f"{len(rows)} connections worth contacting ({skipped} skipped: already in outreach log)")
    print(f"Status: {dict(by_status)}. {args.per_day}/day -> {last_day} days.")
    print(f"Queue: {QUEUE_CSV.relative_to(ROOT)}  By company: {SUMMARY_MD.relative_to(ROOT)}\n")
    print_table(rows[: args.top])


def write_summary(rows):
    groups = defaultdict(list)
    for r in rows:
        groups[(r["tier"], r["company_group"])].append(r)
    label = {1: "Tier 1: your lanes", 2: "Tier 2: large UAE employers", 3: "Tier 3: other employers",
             4: "Tier 4: freelance, bug bounty, undisclosed"}
    out = ["# LinkedIn connections by company", "",
           "Generated by `tools/network_rank.py`. Dell excluded (Adel handles those himself).", ""]
    for tier in (1, 2, 3, 4):
        keys = sorted([k for k in groups if k[0] == tier], key=lambda k: -len(groups[k]))
        if not keys:
            continue
        out += [f"## {label[tier]} ({sum(len(groups[k]) for k in keys)} people)", ""]
        for k in keys:
            out += [f"### {k[1]} ({len(groups[k])})", "", "| Rank | Day | Name | Position | Status |",
                    "|---|---|---|---|---|"]
            for r in sorted(groups[k], key=lambda r: r["rank"]):
                out.append(f"| {r['rank']} | {r['day']} | [{cell(r['name'])}]({r['url']}) | {cell(r['position'])} | {r['status']} |")
            out.append("")
    SUMMARY_MD.write_text("\n".join(out), encoding="utf-8")


def cell(text):
    return str(text).replace("|", "/")


def print_table(rows):
    print("| # | Day | Score | Name | Company | Position | Status |")
    print("|---|---|---|---|---|---|---|")
    for r in rows:
        print(f"| {r['rank']} | {r['day']} | {r['score']} | {cell(r['name'])} | {cell(r['company'])} | {cell(r['position'])} | {r['status']} |")


def next_batch():
    rows = read_queue()
    queued = [r for r in rows if r["status"] == "queued"]
    if not queued:
        sys.exit("Queue empty: everyone has been drafted or skipped.")
    day = min(int(r["day"]) for r in queued)
    print(f"Day {day}:")
    print_table([r for r in queued if int(r["day"]) == day])


def find(rows, keys):
    """Match people by profile URL, or by a case-insensitive piece of their name."""
    hits = []
    for key in keys:
        k = key.lower().strip()
        m = [r for r in rows if r["url"].lower() == k] or [r for r in rows if k in r["name"].lower()]
        if len(m) > 1:  # prefer people already in play (drafted/sent) over the untouched queue
            m = [r for r in m if r["status"] != "queued"] or m
        if len(m) != 1:
            sys.exit(f"'{key}' matched {len(m)} people; use the profile URL or more of the name.")
        hits.append(m[0])
    return hits


def mark(status, keys, when):
    if status not in STATUSES:
        sys.exit(f"Status must be one of {STATUSES}")
    rows = read_queue()
    for r in find(rows, keys):
        r["status"] = status
        if status == "sent":
            r["sent_on"] = when
        elif status == "followed_up":
            r["followup_on"] = when
        print(f"  {r['name']} ({r['company']}) -> {status}")
    write_queue(rows)
    write_summary(rows)


def reply(key, outcome, note, when):
    if outcome not in OUTCOMES:
        sys.exit(f"Outcome must be one of {OUTCOMES}")
    rows = read_queue()
    r = find(rows, [key])[0]
    r.update(status="replied", replied_on=when, outcome=outcome,
             notes="; ".join(x for x in (r.get("notes", ""), note) if x))
    write_queue(rows)
    write_summary(rows)
    print(f"  {r['name']} ({r['company']}) replied: {outcome}")


def days_since(d, today):
    return (today - date.fromisoformat(d)).days if d else None


def report(today):
    rows = read_queue()
    contacted = [r for r in rows if r["sent_on"]]
    replied = [r for r in contacted if r["status"] == "replied"]
    print(f"# Outreach report - {today}\n")
    rate = f"{len(replied) / len(contacted):.0%}" if contacted else "n/a"
    print(f"Sent {len(contacted)} | replied {len(replied)} ({rate}) | "
          f"outcomes {dict(Counter(r['outcome'] for r in replied))} | "
          f"queued {sum(r['status'] in ('queued', 'drafted') for r in rows)}\n")

    def table(title, rs, extra):
        print(f"## {title} ({len(rs)})")
        if not rs:
            print("none\n"); return
        for r in rs:
            print(f"- {r['name']} ({r['company']}): {extra(r)}")
        print()

    table("Replies to act on", [r for r in replied if r["outcome"] in ("referral", "call", "advice", "pending")],
          lambda r: f"{r['outcome']}, replied {days_since(r['replied_on'], today)}d ago. {r['notes']}")
    table(f"Close as no reply (sent {NO_REPLY_AFTER}+ days ago; never follow up)",
          [r for r in contacted if r["status"] in ("sent", "followed_up")
           and days_since(r["sent_on"], today) >= NO_REPLY_AFTER],
          lambda r: f"sent {days_since(r['sent_on'], today)}d ago")
    table("Waiting", [r for r in contacted if r["status"] in ("sent", "followed_up")
                      and days_since(r["sent_on"], today) < NO_REPLY_AFTER],
          lambda r: f"sent {days_since(r['sent_on'], today)}d ago"
                    + (f", followed up {days_since(r['followup_on'], today)}d ago" if r["followup_on"] else ""))
    table("Drafted, not yet sent", [r for r in rows if r["status"] == "drafted"], lambda r: f"day {r['day']}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv", nargs="?", default=str(DEFAULT_CSV))
    ap.add_argument("--top", type=int, default=30)
    ap.add_argument("--per-day", type=int, default=15)
    ap.add_argument("--next", action="store_true", help="print the next queued day")
    ap.add_argument("--mark", nargs="+", metavar=("STATUS", "PERSON"),
                    help="set status (e.g. sent, followed_up, skipped) by profile URL or part of the name")
    ap.add_argument("--reply", metavar="PERSON", help="record a reply from this person")
    ap.add_argument("--outcome", help=f"with --reply: one of {OUTCOMES}")
    ap.add_argument("--note", default="", help="with --reply: what they said / next step")
    ap.add_argument("--report", action="store_true", help="who to follow up, who replied, who is waiting")
    ap.add_argument("--date", default=date.today().isoformat(), help="date to record (YYYY-MM-DD), default today")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")  # Windows console defaults to cp1252

    if args.next:
        next_batch()
    elif args.mark:
        mark(args.mark[0], args.mark[1:], args.date)
    elif args.reply:
        reply(args.reply, args.outcome, args.note, args.date)
    elif args.report:
        report(date.fromisoformat(args.date))
    else:
        build(args)


if __name__ == "__main__":
    main()
