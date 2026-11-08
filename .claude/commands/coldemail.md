# /coldemail - Find Recruiters & Hiring Managers and Send Tailored Cold Emails

You are running Adel's cold-email outreach: find the people who hire for his lanes at target companies in the UAE, work out their work email, send each a short tailored email with a tailored one-page CV attached, and track delivery, bounces, replies and follow-ups in `documents/context/cold-email-targets.csv` (managed by `tools/cold_email.py`, shown in `/html-report`).

`$ARGUMENTS`:
- `go` (or empty): general run across target companies, **one person per company per run** across as many companies as have a proven email format.
- `<company>[, <company> ...]` (e.g. `/coldemail Palo Alto, IBM`): only those companies, one person each.
- `report`: only Step 0 (sync + report), no new emails.

Adel's standing rules (memory: cold-email-style, outreach-sending, claude-submits-applications). **Never send without Adel's explicit approval** (2026-10-19: "never send emails again unless i specifically say send wait for approval"). This replaces the 2026-09-28 standing approval. Draft the batch, run `--dry-run`, show him every recipient, address and email, then STOP and wait for him to say send. Approval covers that batch only.

Follow these steps **in order**.

---

## Step 0: Sync replies and bounces, then report

1. `python tools/cold_email.py --sync-list` prints every address awaiting a reply.
2. With the Gmail connector (`search_threads`), check:
   - **Bounces:** `from:mailer-daemon newer_than:14d`. For each bounce whose recipient is in the list: `python tools/cold_email.py --mark bounced "<email>" --note "<SMTP code>"`. A `550 5.4.1` / `5.1.1` means the address does not exist: **do not guess another variant** for that person (bounces hurt Gmail reputation); tell Adel to reach them on LinkedIn.
   - **Replies:** `from:(<addr1> OR <addr2> ...) newer_than:30d` (batch ~10 addresses per query). Read each reply (`get_thread`) and record it: `python tools/cold_email.py --reply "<email>" --outcome interview|referral|call|advice|not_hiring|declined --note "<what they said / next step>"`. Auto-replies (out of office) are not replies: add a note only.
3. `python tools/cold_email.py --report`. Show Adel: replies to act on first (draft his reply), people closed as no reply, bounces (with LinkedIn profile links), counts.
4. **Never send follow-ups.** Adel's rule (2026-10-19): following up on an unanswered cold email is harassment and spam; if they don't answer, so be it. Each person gets exactly one email, ever. Anyone the report lists under "Close as no reply" (21+ days, no reply) gets `--mark no_reply "<email>"` and nothing else.

If `$ARGUMENTS` is `report`, stop here.

## Step 1: Choose companies

Target list (CLAUDE.md Target Sectors + search-queries.md), UAE only, **Dell excluded** (Adel handles Dell himself):
G42 group (G42, Core42, Inception, Presight, AIQ, CPX), OpenAI (Abu Dhabi), Microsoft, NVIDIA, Red Hat, Broadcom/VMware, IBM, Cisco, Palo Alto Networks, Fortinet, CrowdStrike, Check Point, Trend Micro, Oracle, AWS, HPE, Help AG, e&, Deloitte, PwC, EY, KPMG, Accenture, Capgemini, Ingram Micro, GBM, Injazat, plus any company Adel names.

For `go`: skip people already contacted; a company can be revisited with new peers/leads, but not (`python tools/cold_email.py --contacted "<company>"`), unless the only contacts bounced. Prefer companies with a live UAE role from the latest `/scrape` or `careers-search` (name the role in the email).

## Step 2: Find the people (LinkedIn, logged in, via opencli)

Use Adel's signed-in LinkedIn in Chrome through **opencli** (text only; see the browser ladder in `~/.claude/CLAUDE.md`), not Claude in Chrome screenshots. People search filtered to the UAE (geoUrn 104305776):
`https://www.linkedin.com/search/results/people/?keywords=<Company>%20talent%20acquisition&geoUrn=%5B%22104305776%22%5D`
(also try `<Company> recruiter`, and for small teams `<Company> <lane>` e.g. `presales`, `security`). Open it with `opencli browser open <url> --session linkedin`, then extract name, headline, location and profile URL with one `opencli browser eval "<js>" --session linkedin` snippet that walks lines followed by `• 1st/2nd/3rd`. Keep volume low (a handful of searches per run): LinkedIn locks accounts that look automated.

**One person per company per run, never several at once** (Adel, 2026-10-19: emailing 3 people at the same company at the same time looks like spam and they compare notes). Wait at least 7 days after the last email to a company before emailing another person there. Pick the single best person (usually the peer in his target role, or the recruiter if there is a live posting), and record the type (`type` field in the batch JSON). Candidate types:
- `recruiter` (1): UAE recruiter / TA partner covering tech, AI, security, early careers or campus.
- `peer` (2-3): people in Adel's target roles at that company in the UAE: AI / ML engineer, solutions or presales engineer, security consultant or engineer, forward-deployed engineer. Search `<Company> <role>` with the UAE filter. Prefer 1-5 years' experience and anyone with a shared link (AUS alumni, ex-Dell, mutual connections).
- `lead` (1): team lead, engineering / presales manager, or head of the relevant practice (for startups: founder / CTO).
Skip: executive-search / C-suite recruiters, Emiratization-only recruiters, anyone already in the tracker (`--contacted`), Dell, and anyone in `outreach-log.md` or `network-queue.csv` with status sent/replied. "Meet the hiring team" on a live UAE posting is always worth including.

Keep extraction cheap: one search per company per type, pull name / headline / location / profile URL with a single `opencli browser eval` call, no screenshots.

## Step 3: Work email (deliverability is the top priority)

Adel's Gmail must never be flagged as spam. **Bounce budget: at most 1 bounce per 1-2 weeks.** An email is only sent when the address is highly certain; everyone else is handed to Adel as a LinkedIn contact instead.

0. **Clay first (Adel, 2026-10-22: use Clay instead of manual searching and guessing).** Look the person up with the Clay MCP: `search-contacts-by-name` (`contactName`, `companyIdentifier` = the company domain), then `add-contact-data-points` with `[{type: "Email"}]` on the returned `taskId`, then `get-task-context` until the Work Email enrichment is `completed` or `error`. Batch every person of the run into one search. Check the returned contact is the right person (title, location UAE, current employer) before trusting the email.
   - **Clay returns an address** on the person's current company domain → `conf: high`, `evidence: Clay work email <date> (task <taskId>)`. Skip steps 1-2 for that person, **except** on a domain listed in step 5 (G42 subsidiaries, Core42, CPX, Microsoft) or where the address contradicts a published example in `cold-email-formats.md`: there it also needs step 1 or 2 proof.
   - **Clay returns nothing / error** → fall back to step 1 (published address); no published address → LinkedIn list (Step 7). Never fall back to guessing a format for that person.
   - Clay costs credits per email lookup: only enrich the one chosen person per company, never whole search lists. If Clay reports insufficient credits, stop the Clay step and tell Adel; never upgrade or buy anything.
   - Validation 2026-10-22: Clay returned the exact delivered addresses for Abhinav Noronha (helpag.com) and John Canimo (g42.ai), and no address for Zulul Huma (cpx.net, the earlier bounce).
1. **Published address wins.** Search for the person's own address: their LinkedIn headline/about (some recruiters publish it, e.g. `suvjain@cisco.com`), company site, conference speaker pages, press releases, GitHub commits, public posts. Found → `conf: verified`, `evidence: <URL where it appears>`.
2. **Otherwise the format must be proven by real examples, not aggregator percentages.** Aggregator format shares (LeadIQ, RocketReach, email-format sites) are only a lead (a Clay per-person Work Email result is step 0, not a format share). Before using a format, find **at least 2 real, published addresses of other employees of the same company and same email domain**, ideally the same country/office and the same subsidiary (search e.g. `"@cpx.net"`, `"@core42.ai" email`, press-release contacts, event pages, PDF reports, GitHub). Record them in `documents/context/cold-email-formats.md` with their source URLs. Only when ≥2 real examples match the pattern and nothing contradicts it → `conf: high`, `evidence: <URLs of the examples>`.
3. **Subsidiaries and regional entities:** prove the domain for that exact entity (Core42 ≠ G42, Inception ≠ G42, Microsoft UAE staff may differ). A domain that is only "probably" right is not good enough.
4. **Anything less than verified/high is not emailed.** No `medium`, no "sources disagree", no names with particles/hyphens/double surnames unless an example shows how that company writes them. Put these people in the Step 7 LinkedIn list instead.
5. **Known failures** (bounced 2026-09-28, 550 5.4.1 recipient rejected): `ammar.mohammad@g42.ai`, `ammar.mohammad@core42.ai`, `nancy.naweto@microsoft.com`, `zulul.huma@cpx.net`. Also `nirmal.manoharan@g42.ai` (2026-10-20, 550 5.4.1 Access denied) despite first.last@g42.ai having 3 delivered examples: G42 rejects some real-format addresses, so **G42 itself** is on this list too. G42, Core42, CPX and Microsoft all reject unknown recipients, so any guess there is high risk: only published addresses or ≥2 matching examples from the same entity.
6. Never use personal (gmail/hotmail) addresses. Never more than one attempt per person; a bounced person is LinkedIn-only forever.

## Step 4: Tailored CV per company

**Properly tailored, one CV per person** (Adel, 2026-10-19: changing only the "Targeting" sentence is not tailoring). Decide the email's one project first (Step 5), then build the CV around the same person: `cv/main_cold_<company>_<surname>.tex`. **Never reuse** an earlier `main_cold_*` CV for a new person.

Start from the matching base:
- AI engineering lanes (G42, Core42, Inception, OpenAI, Microsoft, AWS, Oracle AI, Big Four AI & data...): base `cv/main_cohere_forward_deployed_engineer_agentic_platform.tex`
- Security lanes (CPX, Help AG, Palo Alto, Fortinet, CrowdStrike, Check Point, Big Four cyber): base `cv/main_example.tex`
- Presales / infrastructure lanes (Cisco, Red Hat, NVIDIA, Broadcom, HPE, distributors, SIs): base `cv/main_base_presales.tex`, or the tailored CV of a live application to that company if one exists

Then tailor all of the following, using only facts from `01-candidate-profile.md`:
1. **Summary:** 3-4 lines aimed at this person's team and lane (e.g. "AI and data consulting at Deloitte"), naming the project the email leads with. No sponsorship, residency or availability phrase.
2. **Bullet order:** in each role, the bullet for the email's project comes first, then the next most relevant to this person's work. A cold CV must never start with the same bullets as its base unless those really are the best fit.
3. **Bullet wording:** reword the top 2-3 bullets in this team's own terms where truthful (security: threat modelling, zero trust; consulting: client requirements, proposals, delivery; presales: solution design, sizing, PoC; AI engineering: agents, RAG, evaluation, production).
4. **Cut:** drop or shorten 1-2 bullets that don't serve this lane, to make room. Keep it to one page.
5. **Skills:** first skill line = this lane's skills; reorder the items within each line so the most relevant come first.
6. **Check:** `diff` the new `.tex` against its base and confirm changes beyond the Summary (at least the bullet order and the skills order). If only the Summary changed, it is not tailored: redo it.

Show each CV's Summary and top bullets to Adel together with the email in the approval step (Step 6). Compile with the adel-onepage command (`rm -f X.pdf && lualatex -interaction=nonstopmode X.tex && python ../tools/clean_pdf.py X.pdf` from `cv/`), then `python tools/verify_pdf.py cv/X.pdf --pages 1` must pass. Facts only from `01-candidate-profile.md`. The sender attaches it as `Adel_Abdelmoaty_Resume.pdf` automatically.

## Step 5: Write the emails (memory: cold-email-style)

- **Subject:** a direct request, e.g. `Request for Consideration: Entry-Level AI Engineering at Inception`; `Request for Referral: <Role>, <Company> <City>` when asking the person to route him to a named role's hiring team. Never "would love to join", never "Role - Name (credentials)".
- **Length (Adel, 2026-10-22: "too long ... AI slop"): about 60-70 words before the signature.** Use the short shape below, not the long three-paragraph one: `I'm a final-year Computer Science student at AUS and interned at Dell Technologies this summer, where I <one project in plain words>.` / one plain sentence on why this company + the ask (`Would you be open to referring me, or pointing me to the right person? My CV is attached.`) / `Thank you,` + signature lines (name, phone, LinkedIn | GitHub). The sender does not add a signature, so it must be in `body`. Mix lanes and contact types across the run (Adel wants variety).
- **Older long form (superseded, kept for reference):** `Hi <first>,` then three short paragraphs:
  1. `I'm a Computer Science student at the American University of Sharjah, graduating in December 2026. This summer I interned at Dell Technologies' Infrastructure Solutions Group, where I <one or two projects from the profile that fit this company>.`
  2. Specific enthusiasm for **this** company tied to what it actually does (verify any company fact you use), then the ask (be considered for entry-level X / point me to the hiring team for <named live role>).
  3. `My CV is attached. Thank you for your time.`
  Signature: `Best regards,` / `Adel Abdelmoaty` / `linkedin.com/in/adel-abdelmoaty-25aa5424b | github.com/adelahmad2005 | +971 56 211 4556`.
- **Never** mention visa sponsorship, residency, nationality, "available full-time", or salary. No em-dashes, no banned words (05-cv-templates.md list). Every claim must be in `01-candidate-profile.md`.
- Vary the enthusiasm sentence between companies so no two emails read identically.
- By `type`: **recruiter** asks to be considered for entry-level roles / a named programme; **peer** asks, peer to peer, whether they'd be open to referring him (or pointing him to the right team) for a named role or entry-level openings, subject `Request for Referral: <Role/Team> at <Company>`; **lead** leads with the single strongest matching project and asks whether the team takes graduates, subject `Request for Consideration: <Team> at <Company>`.

Write the batch as JSON (fields `co,name,first,title,type,url,email,basis,conf,evidence,cv,subj,body`; `conf` must be `verified` or `high`, `evidence` the URL(s) proving it, body without the `Hi X,` line) to `<scratchpad>/coldbatch.json` and save a readable copy to `documents/context/cold-emails-YYYY-MM-DD.md`.

## Step 6: Send (local SMTP script, CV attached)

`python tools/send_cold_emails.py <scratchpad>/coldbatch.json --dry-run` to check, show Adel the batch, and **wait for his explicit "send"**. Only then run it without `--dry-run`. It sends from Adel's Gmail over SMTP using the app password in the gitignored `.env` (Adel filled it in; never read, print or echo `.env`), attaches `cv/<cv>` as `Adel_Abdelmoaty_Resume.pdf`, waits 20 s between emails, skips anyone already in the tracker, and adds every sent email to `cold-email-targets.csv` with its `contact_type`. Sent mail appears in Gmail's Sent folder.
If it exits asking for credentials, tell Adel to paste his app password into `.env` (https://myaccount.google.com/apppasswords). Do not fall back to Chrome unless he asks.
After the run: append the batch to `documents/context/outreach-log.md` (Email channel), wait ~2 minutes, check `from:mailer-daemon newer_than:1h` with the Gmail connector and `--mark bounced` any bounce.

Pace: one person per company per run, 7+ days between people at the same company. The sender refuses any row that is not `verified`/`high` with evidence, and refuses to send at all if there was a bounce in the last 7 days (Adel's bounce budget); after a bounce, re-check that company's format with fresh examples before emailing it again.

## Step 7: Report to Adel

Short table: person, company, email (confidence), status (delivered / bounced). Then the LinkedIn profile links of everyone emailed so he can send connection requests himself (he connects on LinkedIn regardless; Claude does not). Bounced people: say LinkedIn is the only route now. End with:

```
## Cold email - YYYY-MM-DD
emailed <n> (<companies>) ; delivered <d>, bounced <b>
total delivered <D>, replied <R> (<rate>) ; closed as no reply <c>
```

Mention that `/html-report` now shows the Cold email section.
