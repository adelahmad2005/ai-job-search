#!/usr/bin/env python3
"""AUS Symplicity job board via its own JSON API, no screenshots, no clicking.

Requests run inside Adel's signed-in Chrome through `opencli browser eval`, so the
session cookie never leaves the browser and nothing secret is stored on disk.
The API only needs the header `x-requested-system-user: students` (found 2026-11-08).

Usage:
  python tools/symplicity.py list                 # all jobs, compact table
  python tools/symplicity.py list --new           # only jobs not seen in the last run
  python tools/symplicity.py list -k cyber        # keyword filter (title/employer)
  python tools/symplicity.py list --uae --qualified --json
  python tools/symplicity.py show <job_id>        # full posting as plain text
  python tools/symplicity.py applications         # what has been applied to

Needs: opencli on PATH, its Browser Bridge extension connected (`opencli doctor`),
and Adel signed in to aus-csm.symplicity.com in Chrome.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

BASE = "https://aus-csm.symplicity.com"
SESSION = "symplicity"
REPO = Path(__file__).resolve().parent.parent
CACHE = REPO / "job_scraper" / "symplicity_seen.json"

HEADERS_JS = "{'Accept':'application/json','x-requested-system-user':'students'}"


class SymplicityError(RuntimeError):
    pass


def _opencli_cmd() -> list[str]:
    """Call opencli's Node entry directly. On Windows the npm .cmd shim goes through
    cmd.exe, which mangles newlines and `&` inside the JavaScript argument."""
    node = shutil.which("node")
    npm = shutil.which("npm")
    if node and npm:
        try:
            root = subprocess.run([npm, "root", "-g"], capture_output=True, text=True,
                                  timeout=30, shell=False).stdout.strip()
            entry = Path(root) / "@jackwener" / "opencli" / "dist" / "src" / "main.js"
            if entry.exists():
                return [node, str(entry)]
        except (OSError, subprocess.SubprocessError):
            pass
    exe = shutil.which("opencli")
    if not exe:
        raise SymplicityError("opencli not found (npm install -g @jackwener/opencli)")
    return [exe]


_CMD: list[str] | None = None


def _opencli(*args: str, timeout: int = 120) -> dict:
    global _CMD
    if _CMD is None:
        _CMD = _opencli_cmd()
    proc = subprocess.run([*_CMD, *args], capture_output=True, text=True,
                          encoding="utf-8", timeout=timeout)
    out = proc.stdout.strip()
    try:
        env = json.loads(out.splitlines()[-1] if out else "{}")
    except json.JSONDecodeError:
        raise SymplicityError(f"opencli returned non-JSON: {out[:300]} {proc.stderr[:300]}")
    if not env.get("ok"):
        err = env.get("error", {})
        raise SymplicityError(f"opencli error: {err.get('message')} {err.get('hint', '')}")
    return env


def _ensure_page() -> None:
    """Make sure the session tab is on the Symplicity origin (fetch is same-origin)."""
    try:
        env = _opencli("browser", "eval", "location.origin", "--session", SESSION, timeout=30)
        if env.get("data") == BASE:
            return
    except SymplicityError:
        pass
    _opencli("browser", "open", f"{BASE}/students/app/home", "--session", SESSION, timeout=60)


def _eval_json(js_body: str, timeout: int = 180):
    """Run an async JS body in the signed-in tab; it must `return` a JSON-serialisable value."""
    _ensure_page()
    js = f"(async()=>{{const H={HEADERS_JS};{js_body}}})().then(v=>JSON.stringify(v))"
    env = _opencli("browser", "eval", js, "--session", SESSION, timeout=timeout)
    data = env.get("data")
    if isinstance(data, str):
        data = json.loads(data)
    if isinstance(data, dict) and data.get("__error"):
        raise SymplicityError(data["__error"])
    return data


def fetch_jobs() -> list[dict]:
    js = """
    const out=[]; let page=1, total=0;
    while(true){
      const r=await fetch(`/api/v2/jobs?perPage=100&page=${page}&sort=!postdate&json_mode=read_only&enable_translation=false`,{headers:H});
      if(r.status===401||r.status===403) return {__error:'Not signed in to Symplicity (HTTP '+r.status+'). Sign in in Chrome and retry.'};
      const j=await r.json(); total=j.total||0;
      for(const m of j.models||[]) out.push({
        id:m.job_id, title:m.job_title, employer:m.name, location:m.job_location,
        type:(m.job_type||[]).join(', '), posted:m.postdate, deadline:m.deadline,
        qualified:m.qualified, pay_from:m.compensation_from, pay_to:m.compensation_to,
        pay_freq:m.compensation_frequency, favorite:m.favorite});
      if(!(j.models||[]).length || out.length>=total || page>=20) break;
      page++;
    }
    return {total, jobs:out};
    """
    data = _eval_json(js)
    return data["jobs"]


def fetch_job(job_id: str) -> dict:
    if not re.fullmatch(r"[0-9a-f]{32}", job_id):
        raise SymplicityError("job_id must be the 32-character hex id shown by `list`")
    js = f"""
    const r=await fetch('/api/v3/jobs/{job_id}',{{headers:H}});
    if(!r.ok) return {{__error:'HTTP '+r.status+' for job {job_id}'}};
    return await r.json();
    """
    return _eval_json(js)


def fetch_applications() -> list[dict]:
    """Applications live on a legacy PHP page; read its table text (no JSON endpoint seen)."""
    js = """
    const r=await fetch('/students/index.php?s=jobs&ss=applied&mode=list&subtab=nocr',{credentials:'include'});
    const doc=new DOMParser().parseFromString(await r.text(),'text/html');
    const rows=[...doc.querySelectorAll('.list-item, tr')].map(e=>e.innerText||e.textContent).map(t=>t.replace(/\\s+/g,' ').trim()).filter(t=>/submitted/i.test(t));
    return rows;
    """
    return _eval_json(js)


def strip_html(s: str | None) -> str:
    if not s:
        return ""
    s = re.sub(r"(?i)<br\s*/?>|</p>|</li>|</div>", "\n", s)
    s = re.sub(r"(?i)<li[^>]*>", "- ", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    return re.sub(r"\n\s*\n+", "\n\n", s).strip()


def _label(v):
    """Flatten Symplicity's {_id, _label} objects (and lists of them) to plain text."""
    if isinstance(v, dict):
        return str(v.get("_label") or v.get("name") or v.get("address_text") or "").replace("\n", ", ")
    if isinstance(v, list):
        return "; ".join(x for x in (_label(i) for i in v) if x)
    return "" if v is None else str(v)


def _is_qualified(job: dict) -> bool:
    q = str(job.get("qualified", "")).strip().lower()
    return q not in ("0", "false", "no", "n", "not qualified")


def _is_uae(job: dict) -> bool:
    loc = (job.get("location") or "").lower()
    return any(w in loc for w in ("united arab emirates", "dubai", "abu dhabi", "sharjah",
                                  "ajman", "ras al", "fujairah", "umm al", "nationwide"))


def _load_seen() -> set[str]:
    try:
        return set(json.loads(CACHE.read_text(encoding="utf-8")))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()


def _save_seen(ids: set[str]) -> None:
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(sorted(ids)), encoding="utf-8")


def cmd_list(a) -> int:
    jobs = fetch_jobs()
    seen = _load_seen()
    all_ids = {j["id"] for j in jobs}
    for j in jobs:
        j["new"] = j["id"] not in seen
    if a.new:
        jobs = [j for j in jobs if j["new"]]
    if a.keyword:
        kw = a.keyword.lower()
        jobs = [j for j in jobs if kw in f"{j['title']} {j['employer']}".lower()]
    if a.uae:
        jobs = [j for j in jobs if _is_uae(j)]
    if a.qualified:
        jobs = [j for j in jobs if _is_qualified(j)]
    if not a.no_save:
        _save_seen(seen | all_ids)

    if a.json:
        print(json.dumps(jobs, ensure_ascii=False, indent=1))
        return 0
    for j in jobs:
        flags = ("NEW " if j["new"] else "") + ("" if _is_qualified(j) else "NOTQ ")
        dl = f" | due {j['deadline']}" if j.get("deadline") else ""
        print(f"{j['id']} | {flags}{j['title']} | {j['employer']} | {j['location']} | {j['type']} | posted {j['posted']}{dl}")
    print(f"-- {len(jobs)} shown / {len(all_ids)} on board", file=sys.stderr)
    return 0


def cmd_show(a) -> int:
    d = fetch_job(a.job_id)
    if a.json:
        print(json.dumps(d, ensure_ascii=False, indent=1))
        return 0
    pay = " ".join(x for x in (
        f"{d.get('compensation_from') or ''}-{d.get('compensation_to') or ''}".strip("-"),
        _label(d.get("compensation_currency")), _label(d.get("compensation_frequency"))) if x)
    quals = d.get("qualifications")
    fields = [("Title", d.get("job_title")), ("Employer", _label(d.get("job_emp"))),
              ("Location", _label(d.get("location"))), ("Type", _label(d.get("job_type"))),
              ("Deadline", _label(d.get("application_deadline") or d.get("job_end"))), ("Pay", pay),
              ("Qualifications", strip_html(quals) if isinstance(quals, str) else _label(quals)),
              ("Majors", _label(d.get("major"))), ("Graduation", _label(d.get("graduation_date")))]
    for k, v in fields:
        if v:
            print(f"{k}: {v}")
    print("\n" + strip_html(d.get("job_desc")))
    return 0


def cmd_applications(a) -> int:
    for row in fetch_applications():
        print(row)
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="AUS Symplicity jobs via API (through opencli)")
    sub = p.add_subparsers(dest="cmd", required=True)
    pl = sub.add_parser("list", help="list jobs on the board")
    pl.add_argument("-k", "--keyword")
    pl.add_argument("--new", action="store_true", help="only jobs not seen in a previous run")
    pl.add_argument("--uae", action="store_true", help="only UAE locations")
    pl.add_argument("--qualified", action="store_true", help="drop jobs the portal marks not qualified")
    pl.add_argument("--json", action="store_true")
    pl.add_argument("--no-save", action="store_true", help="do not update the seen-jobs cache")
    pl.set_defaults(fn=cmd_list)
    ps = sub.add_parser("show", help="full posting for one job")
    ps.add_argument("job_id")
    ps.add_argument("--json", action="store_true")
    ps.set_defaults(fn=cmd_show)
    pa = sub.add_parser("applications", help="list submitted applications")
    pa.set_defaults(fn=cmd_applications)
    a = p.parse_args(argv)
    try:
        return a.fn(a)
    except SymplicityError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
