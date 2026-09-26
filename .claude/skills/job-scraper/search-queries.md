# Search Queries for Job Scraper

<!-- Populated by /setup on 2026-09-26 for Adel Abdelmoaty (Dubai, UAE; graduating Dec 2026, full-time from Jan 2027). -->

## Installed portal CLIs (primary for `/scrape`)

`/scrape` discovers every portal skill under `.agents/skills/*/SKILL.md` and runs its CLI first. Enabled for this profile: **`linkedin-search`** (public guest endpoints, no login) and **`freehire-search`**. **`careers-search`** queries the target companies' own careers sites (registry: `.agents/skills/careers-search/companies.json`; add companies there). The **Indeed connector** (`search_jobs`, `country_code="AE"`) also runs as a primary source (see SKILL.md Step 1b-bis). The four Danish demo portals stay **disabled** (wrong market). Pass the location explicitly: `--location "Dubai, United Arab Emirates"` or `"United Arab Emirates"`; for freehire use the UAE country facet.

**Searching** uses public feeds and public search pages only. **Applying** is done by Claude through Adel's signed-in Chrome (rule changed 2026-09-26).

The `site:` query templates below are the **WebSearch fallback**, for portals without a CLI (Bayt, GulfTalent, Naukrigulf), for company career pages, or when a CLI fails.

**Language scope:** Arabic (native) and English (fluent). UAE tech and consulting postings are almost all in English, so write queries in **English**. Arabic-language postings are fine and pass the Language Gate.

## Search Sites

Primary (UAE market):
- **linkedin.com/jobs**: LinkedIn job listings (filter: United Arab Emirates / Dubai); also covered by the `linkedin-search` CLI
- **bayt.com**: largest Gulf job board
- **gulftalent.com**: strong for graduate, consulting and mid-level roles in the GCC
- **naukrigulf.com**: large volume, many systems-integrator and IT roles
- **ae.indeed.com**: Indeed UAE (covered by the Indeed connector as a primary source; read-only search, no login automation)

Secondary (company career pages via Google, high-priority targets):
- Network companies (warm referral route): **Dell Technologies**, **NVIDIA**, **Red Hat**, **VMware/Broadcom**, **IBM**
- AI and cyber in the UAE: G42 / Core42 / Inception, Help AG (e&), CPX, Presight, Digital14 successors, Microsoft, Cisco, Palo Alto Networks, Fortinet, Kaspersky, Trend Micro, Check Point, CrowdStrike, Oracle, AWS, HPE, Lenovo ISG
- Consulting: Deloitte, PwC, EY, KPMG (technology, cyber and AI practices), Accenture, Capgemini
- Distributors / systems integrators (presales-heavy): Ingram Micro, Redington Gulf, Mindware, Spectrum, Emitac, Gulf Business Machines (GBM), Injazat, Alpha Data, Condo Protego, StarLink, Seven Seas

## Query Categories

Organised by **function**, with several title variants per category. Always add graduate / junior / early-career variants, because Adel is a December 2026 graduate: `graduate`, `junior`, `associate`, `entry level`, `trainee`, `2027`.

### Priority 1: AI & Security Engineering / Consulting (deep-technical first role)

The career sequence starts here: deep technical work in AI and security.

```
site:linkedin.com/jobs "AI Engineer" (graduate OR junior OR associate) Dubai
site:linkedin.com/jobs "AI Security" OR "LLM Security" OR "AI Red Team" United Arab Emirates
site:linkedin.com/jobs "Cybersecurity Consultant" (graduate OR junior OR associate) Dubai
site:linkedin.com/jobs "Security Engineer" (graduate OR junior) United Arab Emirates
site:bayt.com "AI Engineer" Dubai
site:bayt.com "Cyber Security" graduate Dubai
site:gulftalent.com "AI" OR "Machine Learning" engineer graduate UAE
site:naukrigulf.com "Automation Engineer" Python Dubai
"Generative AI Engineer" OR "LLM Engineer" OR "Applied AI Engineer" junior Dubai
"Offensive Security" OR "Penetration Tester" junior OR graduate UAE
"AI Automation Engineer" OR "n8n" OR "Workflow Automation" Dubai
```

### Priority 2: Services Presales / Solution Consulting (security and AI)

The second lane. Acceptable as a first role if it stays technical.

```
site:linkedin.com/jobs "Presales Engineer" (graduate OR junior OR associate) Dubai
site:linkedin.com/jobs "Solutions Engineer" OR "Solution Consultant" United Arab Emirates
site:linkedin.com/jobs "Services Presales" OR "Solutions Architect" associate UAE
site:linkedin.com/jobs "Presales" cybersecurity Dubai
site:bayt.com "Presales Engineer" Dubai
site:gulftalent.com "Presales" graduate UAE
site:naukrigulf.com "Presales Engineer" security Dubai
"Sales Engineer" OR "Technical Consultant" AI Dubai
"Customer Engineer" OR "Associate Solutions Architect" UAE
```

### Priority 3: Graduate Programmes & Technical Consulting (2027 intake)

Breadth-building entry routes; rotations are a plus.

```
site:linkedin.com/jobs "graduate programme" technology OR cyber OR AI UAE 2027
"Graduate" "Technology Consulting" OR "Cyber" Deloitte OR PwC OR EY OR KPMG Dubai 2027
"Early Careers" OR "University Graduate" Dell OR NVIDIA OR "Red Hat" OR IBM OR Microsoft Dubai
site:gulftalent.com "graduate trainee" IT Dubai
"Technology Analyst" OR "Technology Consultant" graduate Dubai
```

### Priority 4: Software / Data / Platform Engineering

A wider technical net. Adel wants these surfaced, not hidden.

```
site:linkedin.com/jobs "Python Developer" (junior OR graduate) Dubai
site:linkedin.com/jobs "Software Engineer" graduate United Arab Emirates
site:linkedin.com/jobs "Data Engineer" OR "Data Analyst" junior Dubai
site:bayt.com "Python" developer junior Dubai
"DevOps Engineer" OR "Platform Engineer" OR "Cloud Engineer" junior Dubai
"Machine Learning Engineer" OR "Data Scientist" graduate UAE
```

### Priority 5: Financial / Business Analyst (Finance minor lane)

Finance minor plus accounting automation qualifies him. Flag the experience gap honestly.

```
site:linkedin.com/jobs "Financial Analyst" OR "Business Analyst" graduate Dubai
"FP&A Analyst" OR "Finance Automation" junior UAE
"Business Analyst" fintech OR "digital transformation" junior Dubai
"Finance Systems Analyst" OR "ERP Analyst" OR "RPA Developer" Dubai
```

## Location Filter

Adel lives in Dubai and is willing to relocate **within the UAE**.
- **Ideal:** Dubai (all areas: DIFC, Business Bay, Internet City, Media City, Silicon Oasis, JLT, Dubai South)
- **Acceptable:** Sharjah, Ajman (short commute; AUS is in Sharjah)
- **Acceptable (relocation within the UAE):** Abu Dhabi, Al Ain, Ras Al Khaimah, Umm Al Quwain, Fujairah
- **Borderline:** remote roles from Dubai for a non-UAE employer (check contract and payroll setup)
- **Too far:** anything requiring relocation outside the UAE (including elsewhere in the GCC: Riyadh, Doha and so on). Exclude unless it is explicitly remote from the UAE.

## Eligibility Filter
- Exclude **"UAE Nationals only" / Emirati only / Emiratisation / Tawteen / GCC nationals only** postings. Adel is a resident, not a national.
- Flag "UAE Nationals preferred".
- Positive signal: no sponsorship needed. He is a UAE resident.

## Experience Filter
- Keep: graduate, junior, associate, trainee, entry level, 0-2 years.
- Keep and flag as a stretch: exactly 2 years (the 2-3 year band only when strongly aligned with Priority 1-2).
- Drop: senior, lead, manager, principal, 3+ years (unless the posting is otherwise an exceptional match; then flag it).
- Start date: full-time from January 2027. Internships or part-time roles before then are fine; flag any full-time role needing an earlier start.

## Language Filter

Adel's working languages are in CLAUDE.md's Languages table (Arabic native, English fluent). When filtering scraped results, apply `04-job-evaluation.md`'s Language Gate: a posting requiring a language he hasn't declared at all is excluded (e.g. "fluent French required"); a posting requiring a higher level than declared is flagged, not excluded. Postings simply *written* in a language he doesn't work in are fine if the job doesn't require it.

## Date Filter

Only include jobs posted within the last 14 days, or with an application deadline that has not yet passed. If a posting date cannot be determined, include it but flag as "date unknown". Graduate programme listings for a 2027 intake stay relevant longer; keep them even when older than 14 days if the deadline is still open.

## Adapting Queries

If the user specifies a focus area, select queries from the matching category and also generate 2-3 custom queries for that focus. For example:
- "/scrape presales" -> Priority 2 queries + custom queries for specific vendors
- "/scrape dell" -> Dell careers page + LinkedIn "Dell Technologies" UAE + flag the referral route
- "/scrape finance" -> Priority 5 queries
