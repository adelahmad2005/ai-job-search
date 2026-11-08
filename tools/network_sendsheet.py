"""Turn a network-drafts-YYYY-MM-DD.md file into a one-page send sheet.

Each person gets an "Open profile" link and a "Copy message" button, plus a
checkbox. "Copy sent list" puts a line like `sent: Amit Menon, Osama Elsherbiny`
on the clipboard to paste back to Claude, which records it with
`network_rank.py --mark sent`. Nothing is sent automatically: every click is Adel's.

Usage:
    python tools/network_sendsheet.py [documents/context/network-drafts-YYYY-MM-DD.md]
Writes the same path with a .html extension and opens it in the default browser.
"""
import html
import json
import re
import sys
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTEXT = ROOT / "documents/context"


def parse(md):
    people = []
    for block in re.split(r"^## \d+\. ", md, flags=re.M)[1:]:
        head = block.splitlines()[0]
        name, _, role = head.partition(" - ")
        url = re.search(r"Profile: (\S+)", block).group(1)
        msg = re.search(r"```\n(.*?)\n```", block, re.S).group(1)
        people.append({"name": name.strip(), "role": role.strip(), "url": url, "msg": msg})
    follow = re.search(r"```\n(Hi \[first name\].*?)\n```", md, re.S)
    return people, follow.group(1) if follow else ""


PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Send Sheet</title>
<style>
:root {{ --bg:#f7f7f5; --card:#fff; --text:#1c1c1a; --muted:#6b6b66; --line:#e3e3de;
        --accent:#0a66c2; --accent-text:#fff; --done:#e8f3ec; --done-line:#9fcfb0; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg:#161615; --card:#20201e; --text:#ecece8; --muted:#9a9a94; --line:#33332f;
  --accent:#4d9de0; --accent-text:#0d1b2a; --done:#1d2b22; --done-line:#3f6b4e; }} }}
:root[data-theme="dark"] {{ --bg:#161615; --card:#20201e; --text:#ecece8; --muted:#9a9a94; --line:#33332f;
  --accent:#4d9de0; --accent-text:#0d1b2a; --done:#1d2b22; --done-line:#3f6b4e; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--text); font:15px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif; }}
main {{ max-width:760px; margin:0 auto; padding:24px 16px 96px; }}
h1 {{ font-size:22px; margin:0 0 4px; }}
.sub {{ color:var(--muted); margin:0 0 20px; }}
.card {{ background:var(--card); border:1px solid var(--line); border-radius:10px; padding:14px 16px; margin-bottom:12px; }}
.card.sent {{ background:var(--done); border-color:var(--done-line); }}
.top {{ display:flex; gap:10px; align-items:flex-start; }}
.top input {{ width:20px; height:20px; margin-top:3px; flex:none; accent-color:var(--accent); }}
.who {{ flex:1; min-width:0; }}
.name {{ font-weight:600; }}
.role {{ color:var(--muted); font-size:13px; }}
.msg {{ margin:10px 0; white-space:pre-wrap; font-size:14px; }}
.btns {{ display:flex; gap:8px; flex-wrap:wrap; }}
a.btn, button {{ font:inherit; font-size:14px; padding:7px 14px; border-radius:6px; cursor:pointer;
  border:1px solid var(--accent); text-decoration:none; }}
.primary {{ background:var(--accent); color:var(--accent-text); }}
.ghost {{ background:transparent; color:var(--accent); }}
.bar {{ position:fixed; left:0; right:0; bottom:0; background:var(--card); border-top:1px solid var(--line);
  padding:10px 16px; display:flex; gap:12px; align-items:center; justify-content:center; flex-wrap:wrap; }}
.count {{ color:var(--muted); }}
</style></head><body><main>
<h1>Send sheet: {title}</h1>
<p class="sub">For each person: Open profile, click Message, Copy message, paste, send, tick the box. At the end, Copy sent list and paste it to Claude.</p>
{cards}
{follow}
</main>
<div class="bar"><span class="count" id="count"></span>
<button class="primary" id="copysent">Copy sent list</button></div>
<script>
const PEOPLE = {people};
const KEY = "sendsheet-{key}";
let sent = {{}};
try {{ sent = JSON.parse(localStorage.getItem(KEY) || "{{}}"); }} catch (e) {{}}
function save() {{ try {{ localStorage.setItem(KEY, JSON.stringify(sent)); }} catch (e) {{}} }}
function copy(text, btn) {{
  navigator.clipboard.writeText(text).then(() => {{
    const t = btn.textContent; btn.textContent = "Copied"; setTimeout(() => btn.textContent = t, 1200);
  }});
}}
function render() {{
  document.querySelectorAll(".card[data-i]").forEach(c => {{
    const on = !!sent[c.dataset.i];
    c.classList.toggle("sent", on); c.querySelector("input").checked = on;
  }});
  const n = Object.values(sent).filter(Boolean).length;
  document.getElementById("count").textContent = n + " of " + PEOPLE.length + " sent";
}}
document.querySelectorAll(".card[data-i]").forEach(c => {{
  const i = c.dataset.i;
  c.querySelector("input").addEventListener("change", e => {{ sent[i] = e.target.checked; save(); render(); }});
  c.querySelector(".copy").addEventListener("click", e => copy(PEOPLE[i].msg, e.target));
}});
const fb = document.querySelector(".copyfollow");
if (fb) fb.addEventListener("click", e => copy(fb.dataset.text, e.target));
document.getElementById("copysent").addEventListener("click", e => {{
  const names = PEOPLE.filter((p, i) => sent[i]).map(p => p.name);
  copy("sent: " + (names.join(", ") || "none"), e.target);
}});
render();
</script></body></html>"""


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) > 1:
        src = Path(sys.argv[1])
    else:
        drafts = sorted(CONTEXT.glob("network-drafts-*.md"))
        if not drafts:
            sys.exit("No network-drafts-*.md found; run /network first.")
        src = drafts[-1]
    people, follow = parse(src.read_text(encoding="utf-8"))
    e = html.escape
    cards = "\n".join(
        f'<div class="card" data-i="{i}"><div class="top"><input type="checkbox" aria-label="Sent to {e(p["name"])}">'
        f'<div class="who"><div class="name">{i + 1}. {e(p["name"])}</div><div class="role">{e(p["role"])}</div></div></div>'
        f'<div class="msg">{e(p["msg"])}</div><div class="btns">'
        f'<a class="btn ghost" href="{e(p["url"])}" target="_blank" rel="noopener">Open profile</a>'
        f'<button class="primary copy">Copy message</button></div></div>'
        for i, p in enumerate(people))
    follow_html = ""  # no follow-ups, ever (Adel, 2026-10-19)
    out = src.with_suffix(".html")
    out.write_text(PAGE.format(title=e(src.stem.replace("network-drafts-", "")), cards=cards, follow=follow_html,
                               people=json.dumps(people, ensure_ascii=False).replace("</", "<\\/"),
                               key=e(src.stem)), encoding="utf-8")
    print(f"{len(people)} people -> {out.relative_to(ROOT)}")
    webbrowser.open(out.as_uri())


if __name__ == "__main__":
    main()
