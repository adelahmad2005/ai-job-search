# /coldemail - Find Recruiters & Hiring Managers and Send Tailored Cold Emails

You are running Adel's cold-email outreach: find the people who hire for his lanes at target companies in the UAE, work out their work email, send each a short tailored email with a tailored one-page CV attached, and track delivery, bounces, replies and follow-ups in `documents/context/cold-email-targets.csv` (managed by `tools/cold_email.py`, shown in `/html-report`).

`$ARGUMENTS`:
- `go` (or empty): general run across target companies, about **30-40 people per run** (3-5 per company, mixed recruiter / peer / lead).
- `<company>[, <company> ...]` (e.g. `/coldemail Palo Alto, IBM`): only those companies, 3-5 people each.
- `report`: only Step 0 (sync + report), no new emails.

Adel's standing rules (memory: cold-email-style, outreach-sending, claude-submits-applications). He approved sending without review after the first batch (2026-09-28); do not ask before each batch.

Follow these steps **in order**.

---

## Step 0: Sync replies and bounces, then report

1. `python tools/cold_email.py --sync-list` prints every address awaiting a reply.
2. With the Gmail connector (`search_threads`), check:
   - **Bounces:** `from:mailer-daemon newer_than:14d`. For each bounce whose recipient is in the list: `python tools/cold_email.py --mark bounced "<email>" --note "<SMTP code>"`. A `550 5.4.1` / `5.1.1` means the address does not exist: **do not guess another variant** for that person (bounces hurt Gmail reputation); tell Adel to reach them on LinkedIn.
   - **Replies:** `from:(<addr1> OR <addr2> ...) newer_than:30d` (batch ~10 addresses per query). Read each reply (`get_thread`) and record it: `python tools/cold_email.py --reply "<email>" --outcome interview|referral|call|advice|not_hiring|declined --note "<what they said / next step>"`. Auto-replies (out of office) are not replies: add a note only.
3. `python tools/cold_email.py --report`. Show Adel: replies to act on first (draft his reply), follow-ups due, bounces (with LinkedIn profile links), counts.
4. **Follow-ups due** (sent 7+ days, no reply): send one follow-up per person as a reply in the same Gmail thread (`send_message` with `replyThreadId`; find the thread with `search_threads in:sent to:<email>`), text:
   `Hi <first>, just following up on my note last week in case it got buried. My CV is attached to the email below. Thank you for your time. Best regards, Adel` then `--mark followed_up "<email>"`. Never a second follow-up; 7 days after the follow-up, `--mark no_reply`.

If `$ARGUMENTS` is `report`, stop here.

## Step 1: Choose companies

Target list (CLAUDE.md Target Sectors + search-queries.md), UAE only, **Dell excluded** (Adel handles Dell himself):
G42 group (G42, Core42, Inception, Presight, AIQ, CPX), OpenAI (Abu Dhabi), Microsoft, NVIDIA, Red Hat, Broadcom/VMware, IBM, Cisco, Palo Alto Networks, Fortinet, CrowdStrike, Check Point, Trend Micro, Oracle, AWS, HPE, Help AG, e&, Deloitte, PwC, EY, KPMG, Accenture, Capgemini, Ingram Micro, GBM, Injazat, plus any company Adel names.

For `go`: skip people already contacted; a company can be revisited with new peers/leads, but not (`python tools/cold_email.py --contacted "<company>"`), unless the only contacts bounced. Prefer companies with a live UAE role from the latest `/scrape` or `careers-search` (name the role in the email).

## Step 2: Find the people (LinkedIn, logged in, via Claude in Chrome)

Use Adel's signed-in LinkedIn in Chrome. People search filtered to the UAE (geoUrn 104305776):
`https://www.linkedin.com/search/results/people/?keywords=<Company>%20talent%20acquisition&geoUrn=%5B%22104305776%22%5D`
(also try `<Company> recruiter`, and for small teams `<Company> <lane>` e.g. `presales`, `security`). Extract name, headline, location and profile URL with a `javascript_tool` snippet that walks lines followed by `• 1st/2nd/3rd`.

Strategy is **volume (spray and pray)**: per company pick **3-5 people** of mixed types and record the type (`type` field in the batch JSON):
- `recruiter` (1): UAE recruiter / TA partner covering tech, AI, security, early careers or campus.
- `peer` (2-3): people in Adel's target roles at that company in the UAE: AI / ML engineer, solutions or presales engineer, security consultant or engineer, forward-deployed engineer. Search `<Company> <role>` with the UAE filter. Prefer 1-5 years' experience and anyone with a shared link (AUS alumni, ex-Dell, mutual connections).
- `lead` (1): team lead, engineering / presales manager, or head of the relevant practice (for startups: founder / CTO).
Skip: executive-search / C-suite recruiters, Emiratization-only recruiters, anyone already in the tracker (`--contacted`), Dell, and anyone in `outreach-log.md` or `network-queue.csv` with status sent/replied. "Meet the hiring team" on a live UAE posting is always worth including.

Keep extraction cheap: one search per company per type, pull name / headline / location / profile URL with a single `javascript_tool` call, no screenshots.

## Step 3: Work email

1. Look for a **published** address first (their LinkedIn headline/about, company site, a public post). Use it if found (confidence: verified).
2. Otherwise use the company format from `documents/context/cold-email-formats.md`. If the company is not there, find it (search "<company> email format", read LeadIQ / RocketReach / Clay results), add a row to that file with the share, then build the address. Subsidiaries often have their own domain (Core42 staff are not all on g42.ai; Inception uses inceptionai.ai).
3. Label confidence: `high` (format ≥90%), `medium-high` (70-90%), `medium` (sources disagree / <70%). Never use personal (gmail/hotmail) addresses. Never send more than one guess per person.

## Step 4: Tailored CV per company

One PDF per company: `cv/main_cold_<company>.tex`, built from the matching base and a company-specific `Targeting ...` sentence in the Summary:
- AI engineering lanes (G42, Core42, Inception, OpenAI, Microsoft, AWS, Oracle AI...): base `cv/main_cohere_forward_deployed_engineer_agentic_platform.tex`
- Security lanes (CPX, Help AG, Palo Alto, Fortinet, CrowdStrike, Check Point, Big Four cyber): base `cv/main_example.tex`
- Presales / infrastructure lanes (Cisco, Red Hat, NVIDIA, Broadcom, HPE, distributors, SIs): base `cv/main_base_presales.tex`
Remove any sponsorship / residency phrase. Reuse an existing `main_cold_<company>.pdf` if it is already there. Compile with the adel-onepage command (`rm -f X.pdf && lualatex -interaction=nonstopmode X.tex && python ../tools/clean_pdf.py X.pdf` from `cv/`), then `python tools/verify_pdf.py cv/X.pdf --pages 1` must pass. Facts only from `01-candidate-profile.md`. The sender attaches it as `Adel_Abdelmoaty_Resume.pdf` automatically.

## Step 5: Write the emails (memory: cold-email-style)

- **Subject:** a direct request, e.g. `Request for Consideration: Entry-Level AI Engineering at Inception`; `Request for Referral: <Role>, <Company> <City>` when asking the person to route him to a named role's hiring team. Never "would love to join", never "Role - Name (credentials)".
- **Body:** `Hi <first>,` then three short paragraphs:
  1. `I'm a Computer Science student at the American University of Sharjah, graduating in December 2026. This summer I interned at Dell Technologies' Infrastructure Solutions Group, where I <one or two projects from the profile that fit this company>.`
  2. Specific enthusiasm for **this** company tied to what it actually does (verify any company fact you use), then the ask (be considered for entry-level X / point me to the hiring team for <named live role>).
  3. `My CV is attached. Thank you for your time.`
  Signature: `Best regards,` / `Adel Abdelmoaty` / `linkedin.com/in/adel-abdelmoaty-25aa5424b | github.com/adelahmad2005 | +971 56 211 4556`.
- **Never** mention visa sponsorship, residency, nationality, "available full-time", or salary. No em-dashes, no banned words (05-cv-templates.md list). Every claim must be in `01-candidate-profile.md`.
- Vary the enthusiasm sentence between companies so no two emails read identically.
- By `type`: **recruiter** asks to be considered for entry-level roles / a named programme; **peer** asks, peer to peer, whether they'd be open to referring him (or pointing him to the right team) for a named role or entry-level openings, subject `Request for Referral: <Role/Team> at <Company>`; **lead** leads with the single strongest matching project and asks whether the team takes graduates, subject `Request for Consideration: <Team> at <Company>`.

Write the batch as JSON (fields `co,name,first,title,type,url,email,basis,conf,cv,subj,body`, body without the `Hi X,` line) to `<scratchpad>/coldbatch.json` and save a readable copy to `documents/context/cold-emails-YYYY-MM-DD.md`.

## Step 6: Send (local SMTP script, CV attached)

`python tools/send_cold_emails.py <scratchpad>/coldbatch.json --dry-run` to check, then without `--dry-run`. It sends from Adel's Gmail over SMTP using the app password in the gitignored `.env` (Adel filled it in; never read, print or echo `.env`), attaches `cv/<cv>` as `Adel_Abdelmoaty_Resume.pdf`, waits 20 s between emails, skips anyone already in the tracker, and adds every sent email to `cold-email-targets.csv` with its `contact_type`. Sent mail appears in Gmail's Sent folder.
If it exits asking for credentials, tell Adel to paste his app password into `.env` (https://myaccount.google.com/apppasswords). Do not fall back to Chrome unless he asks.
After the run: append the batch to `documents/context/outreach-log.md` (Email channel), wait ~2 minutes, check `from:mailer-daemon newer_than:1h` with the Gmail connector and `--mark bounced` any bounce.

Pace: up to ~30-40 emails per day, at most 5 people per company per run. Stop the day early if more than 3 bounces come back (bad guesses hurt deliverability).

## Step 7: Report to Adel

Short table: person, company, email (confidence), status (delivered / bounced). Then the LinkedIn profile links of everyone emailed so he can send connection requests himself (he connects on LinkedIn regardless; Claude does not). Bounced people: say LinkedIn is the only route now. End with:

```
## Cold email - YYYY-MM-DD
emailed <n> (<companies>) ; delivered <d>, bounced <b>
total delivered <D>, replied <R> (<rate>) ; follow-ups due <f>
```

Mention that `/html-report` now shows the Cold email section.
