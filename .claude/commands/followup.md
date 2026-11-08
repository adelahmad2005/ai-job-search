# /followup - One Pass Over Replies, Quiet Applications and Deadlines

You are running the whole "chase" routine in one command. It adds no new rules: it runs three existing flows in order and merges their output into one short report. Every rule of the underlying commands still applies - above all, **nothing is sent and no follow-ups are drafted** (Adel's rule, 2026-10-19), and tracker writes need the user's approval.

`$ARGUMENTS` may contain a number of days (e.g. `/followup 14`) to override the 10-day quiet threshold passed to Step 2.

Follow these steps **in order**.

---

## Step 1: Sync replies from Gmail

If the Gmail MCP tools (`mcp__claude_ai_Gmail__*`) are available and authenticated, run the `/gmail-sync` flow (`.claude/commands/gmail-sync.md`) with no arguments: classify replies, present the batch, and write only what the user approves. If Gmail is not connected, say so in one line (`gmail: not connected - statuses may be stale`) and continue; never fall back to IMAP or any other channel.

Running this first matters: an application that got a reply must not be chased in Step 2.

## Step 2: List quiet applications (no chasing)

**Never draft or send follow-ups to employers** (Adel, 2026-10-19: following up is harassment/spam; if they don't answer, so be it). Do not run `/outcome` Step 2b's follow-up drafting.

Instead, list open applications (`applied` / `submitted`) with no reply after the threshold from `$ARGUMENTS` (default 10 days) as information only, and ask whether any should be closed as `no response` via `/outcome`.

## Step 3: Deadlines and graduate programmes

Run `python tools/deadlines.py` and include its output. For every item under **SHOULD BE OPEN NOW** or **RE-CHECK**, check the programme's official page (WebFetch, then WebSearch for the official page if it is blocked) and update that row of `job_scraper/grad_programmes.csv`: `status`, `opens` / `closes` only when the source states them, `last_checked` = today, `source`. Never infer a date. Report what changed.

## Step 4: Report

End with one compact block:

```
## Follow-up pass - YYYY-MM-DD
gmail: <N changes applied | not connected>
quiet applications: <N listed: Company (Role), ...> | none (no follow-ups are ever sent)
deadlines: <items from Step 3, most urgent first> | none
```

Blunt, no filler. If something needs the user today (a programme closing within 7 days, an interview invitation found in Gmail), put it first.
