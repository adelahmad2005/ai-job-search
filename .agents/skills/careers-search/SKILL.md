---
name: careers-search
version: 1.0.0
description: >
  Use this skill to check the target companies' own careers sites for open roles
  in the UAE - the employers listed in companies.json (NVIDIA, Red Hat, Broadcom/
  VMware, IBM, Cisco, CrowdStrike, Trend Micro, HPE, Fortinet, Oracle, Microsoft,
  AWS, the G42 group incl. CPX and Inception, PwC, EY, Capgemini, Ingram Micro).
  Trigger phrases: check company careers pages, any openings at <company>,
  target company jobs, career site search.
context: fork
enabled: true  # set to false to keep this portal installed but have /scrape skip it
allowed-tools: Bash(bun run .agents/skills/careers-search/cli/src/cli.ts *)
---

# Careers-Site Search Skill

Queries each target company's **own careers site** through the public JSON feed
its careers page already uses (Workday, Oracle HCM, SAP SuccessFactors, Phenom,
Microsoft, amazon.jobs, IBM, plus Greenhouse / Lever / SmartRecruiters / Ashby for
companies added later). No login, no API key, zero runtime dependencies - just `bun`.

Roles often appear here before (or instead of) LinkedIn and Indeed, and the URL is
the employer's real application page.

## The registry: `companies.json`

One entry per company. `location_pattern` scopes every search to the UAE.

| `ats` | Required fields | Where to find them |
|---|---|---|
| `workday` | `host`, `tenant`, `site` | job URL `https://{tenant}.wdN.myworkdayjobs.com/en-US/{site}/job/...` |
| `oracle` | `host`, `site` | job URL `https://{host}/hcmUI/CandidateExperience/en/sites/{site}/job/{id}` |
| `successfactors` | `host` | career site with `/search/?q=` and `jobTitle-link` rows |
| `phenom` | `host` | career site answering `POST /widgets` |
| `greenhouse` / `lever` / `ashby` / `smartrecruiters` | `board` | the board slug in the job URL |
| `microsoft`, `amazon`, `ibm` | none | built-in |
| `manual` | `careers_url` | the site can't be read automatically; listed for a human or Chrome check |

`network: true` marks referral-network companies (Dell, NVIDIA, Red Hat,
VMware/Broadcom, IBM) - `/scrape` flags them for a referral ask.

**Adding a company:** open one of its job postings, read the ATS from the URL, add
the entry, then verify with `search --company "<name>" --format table`. If a feed
returns errors (401/403/422, or results only render in-browser), register it as
`manual` with its `careers_url` and a `note`.

## Commands

### Search

```bash
bun run .agents/skills/careers-search/cli/src/cli.ts search [flags]
```

- `--query`, `-q <terms>` - comma-separated title terms; keeps a job when its title
  contains any term (case-insensitive). Omit to get every UAE role.
- `--company <names>` - comma-separated substrings of registry names.
- `--jobage <days>` - posted within N days, filtered client-side. Jobs without an
  exact date (IBM gives none; Workday says "Posted 30+ Days Ago") are kept, except a
  "30+" label is dropped for windows under 30 days.
- `--limit`, `-n <n>` - max postings fetched per company (default 100).
- `--format json|table` - default `json`.

JSON output:

```json
{
  "meta": { "count": 154, "companies_searched": 18, "per_company": [{ "company": "Cisco", "found": 3 }] },
  "results": [{ "id": "...", "title": "...", "company": "...", "location": "...", "date": "2026-09-25",
                "url": "...", "ats": "workday", "network": false, "posted_label": "Posted 2 Days Ago" }],
  "errors": [{ "company": "...", "ats": "...", "error": "HTTP 429 from ..." }],
  "manual": [{ "company": "Dell Technologies", "careers_url": "...", "network": true, "note": "..." }]
}
```

A company that fails lands in `errors`; the rest still return. Exit 1 only when
every company fails, or on a bad flag.

### Detail

```bash
bun run .agents/skills/careers-search/cli/src/cli.ts detail <posting-url> [--format json|plain]
```

Full description for a result URL. Workday, Oracle, Microsoft and Phenom (G42)
use their JSON data; other sites are read from the posting page as text.
IBM posting pages sit behind a bot check, so `detail` returns nothing useful for
them - open IBM URLs in Chrome instead.

### List

```bash
bun run .agents/skills/careers-search/cli/src/cli.ts list --format table
```

## Usage examples

```bash
# Everything open in the UAE across all target companies
bun run .agents/skills/careers-search/cli/src/cli.ts search --format table

# Early-career / technical titles from the last 14 days
bun run .agents/skills/careers-search/cli/src/cli.ts search -q "engineer,consultant,presales,architect,analyst,graduate,associate,intern" --jobage 14

# Referral-network companies only
bun run .agents/skills/careers-search/cli/src/cli.ts search --company "nvidia,red hat,broadcom,ibm"
```

## Notes

- Volume is small: one to a few requests per company per run. Keep it that way:
  no loops over `detail` for every hit.
- A 429 gets one retry after 10 s, then is reported - never retried in a loop.
- Many UAE postings are reserved for UAE Nationals ("UAE National", "UAEN",
  "Emirati", "Tomoh", "Watani"). These are deal-breakers for Adel; `/scrape` should drop them.
