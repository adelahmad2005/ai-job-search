# /network - Rank LinkedIn Connections and Draft Referral Messages

You are turning Adel's LinkedIn connections into a short list of people worth asking for a referral, with one ready-to-paste message each. **LinkedIn is never scraped or messaged by automation**: the input is LinkedIn's own data export, and Adel copy-pastes the messages himself. That keeps the account safe.

It works as a **daily queue**: every connection worth contacting is ranked once into `documents/context/network-queue.csv` and split into days (10 a day by default, at most 2 people from the same company per day). Each run drafts the next day's batch, until everyone is done. `documents/context/network-by-company.md` shows the whole network grouped by company.

**Dell is excluded entirely.** Adel contacts his Dell people himself.

`$ARGUMENTS` may contain a number (e.g. `/network 15`) to draft more than one day's batch. Default: **the next day's batch**.

Follow these steps **in order**.

---

## Step 0: Report first

Run `python tools/network_rank.py --report` and show Adel, before any new drafting:
- **Replies to act on** (call / referral / advice): help him answer these first.
- **Close as no reply** (sent 21+ days ago, no reply): mark them `--mark no_reply "<name>"`. **Never draft or send a follow-up** (Adel, 2026-10-19: following up is harassment/spam; if they don't answer, so be it).

## Step 1: Get today's batch

If `documents/context/network-queue.csv` does not exist, or Adel has dropped in a newer export, build it: `python tools/network_rank.py --top 0` (statuses of people already drafted/sent are kept).

Then run `python tools/network_rank.py --next` to print the next day's batch.

If `documents/context/Connections.csv` is missing, stop and tell Adel how to get it: LinkedIn → Settings → Data privacy → Get a copy of your data → tick **Connections** → Request archive. The file arrives by email, usually within a day. Save `Connections.csv` into `documents/context/`.

## Step 2: Pick the people

Take the day's batch. Apply these checks, and mark anyone you drop with `python tools/network_rank.py --mark skipped "<profile URL>"` (say why):

- **Already contacted:** read `documents/context/outreach-log.md`. The script skips exact names, but the log also lists people by role (e.g. "Head of Presales, Dell"). If a connection matches one of those roles, skip them and say so.
- **NVIDIA / Red Hat / VMware-Broadcom / IBM:** flag these as referral priorities (CLAUDE.md).
- **Location:** the export has no location. Some connections (e.g. Kaspersky, Group-IB, Cipher) may sit outside the UAE. Keep them if the company hires in the UAE; the ask becomes "does your UAE team hire graduates?".
- **Live role:** look for an open posting at the person's company in `job_search_tracker.csv` or the latest scrape results. A message that names a real role gets far more replies than "any openings?". If none is on file, you may run one quick `careers-search` / `linkedin-search` for that company. Never invent a posting.
- **Seniority:** prefer recruiters and people in Adel's lanes (presales, security, AI, solutions, services). Skip C-level people at large companies unless Adel knows them.

Present the shortlist as a table: name, company, position, why picked, live role (or "none found"). Adel can drop names before you draft.

## Step 3: Draft

Write one message per person, following the Rules in `outreach-log.md` and the style in `.claude/skills/job-application-assistant/03-writing-style.md`:

- **About 300 characters, three sentences max**: who Adel is + one project clause, one question, "I'd be glad to share my CV. Thank you." Busy people must be able to read it in 15 seconds. No subject line, no attachments.
- **Shared context first.** Use the most specific real link: same university (AUS), met at Dell, same field. If there is none, say so plainly ("We're connected but haven't spoken").
- **One line on Adel:** final-year CS student at AUS (graduating Dec 2026, available Jan 2027) plus the **one project from `01-candidate-profile.md`** that best fits the person's team. Never claim anything not in that file.
- **One precise ask:** a referral for the named role, or 15 minutes on whether the team hires graduates. Never "do you have any positions?"
- **Easy exit:** e.g. "No worries if it's not a fit."
- Polite, professional, plain. No flattery, no "I hope this finds you well", no "passionate".

Save all drafts to `documents/context/network-drafts-YYYY-MM-DD.md` (gitignored), one section per person: name, profile URL, the message in a code block for easy copying. Then run `python tools/network_sendsheet.py`, which builds the matching `.html` send sheet (Open profile / Copy message / tick sent / Copy sent list) and opens it in Adel's browser. Never message or open LinkedIn pages by automation. Then mark them: `python tools/network_rank.py --mark drafted "<URL>" "<URL>" ...`.

## Step 4: Tracking

`documents/context/network-queue.csv` is the single tracker for LinkedIn outreach (opens in Excel). Columns: `status`, `sent_on`, `followup_on`, `replied_on`, `outcome`, `notes`. **Do not also add these people to `outreach-log.md`**: the ranker drops anyone named there, which would delete their tracking row. `outreach-log.md` stays for warm contacts and email.

Status flow: `queued -> drafted -> sent -> replied | no_reply` (or `skipped`). `followed_up` exists only on legacy rows.

When Adel reports what happened, record it (names can be partial; ambiguous names resolve to people already in play):
- Sent: `python tools/network_rank.py --mark sent "Amit Menon" "Osama" ...` (add `--date YYYY-MM-DD` if not today)
- Reply: `--reply "<name>" --outcome referral|call|advice|not_hiring|declined --note "<what they said / next step>"`

Rules: send by hand, weekdays. **No follow-ups**: one message per person; close as no reply 21 days after sending. Do not put a follow-up template in the drafts file.

End with one compact block:

```
## Network pass - YYYY-MM-DD
queue: day <D> of <total days>; sent <n>, replied <n> (<rate>)
drafted: <N> -> documents/context/network-drafts-YYYY-MM-DD.md
closed as no reply: <n>; replies to act on: <n>
```
