# /followup - One Pass Over Replies, Quiet Applications and Deadlines

You are running the whole "chase" routine in one command. It adds no new rules: it runs three existing flows in order and merges their output into one short report. Every rule of the underlying commands still applies - above all, **nothing is sent**: follow-ups are drafts for the user to send, and tracker writes need the user's approval.

`$ARGUMENTS` may contain a number of days (e.g. `/followup 14`) to override the 10-day quiet threshold passed to Step 2.

Follow these steps **in order**.

---

## Step 1: Sync replies from Gmail

If the Gmail MCP tools (`mcp__claude_ai_Gmail__*`) are available and authenticated, run the `/gmail-sync` flow (`.claude/commands/gmail-sync.md`) with no arguments: classify replies, present the batch, and write only what the user approves. If Gmail is not connected, say so in one line (`gmail: not connected - statuses may be stale`) and continue; never fall back to IMAP or any other channel.

Running this first matters: an application that got a reply must not be chased in Step 2.

## Step 2: Chase quiet applications

Run the follow-up branch of `/outcome` (`.claude/commands/outcome.md`, Step 2b) over every open application, with the threshold from `$ARGUMENTS` or the default 10 days. Its rules apply unchanged: `drafted` rows are never chased, at most two follow-ups per application, no claims beyond the archived submitted materials, and log a follow-up only once the user confirms it was sent.

When the candidate table is presented, add one column the branch does not have: **channel to use** - `email` when the tracker's `contact_person` or the archive has a recruiter or hiring-manager email, otherwise `LinkedIn message` (the draft is the same text, trimmed under 300 characters for a connection note). Do not look up or guess contact details that are not already in the tracker or archive.

If no application is past the threshold, say when the next one becomes due (earliest `date` + threshold) and move on.

## Step 3: Deadlines and graduate programmes

Run `python tools/deadlines.py` and include its output. For every item under **SHOULD BE OPEN NOW** or **RE-CHECK**, check the programme's official page (WebFetch, then WebSearch for the official page if it is blocked) and update that row of `job_scraper/grad_programmes.csv`: `status`, `opens` / `closes` only when the source states them, `last_checked` = today, `source`. Never infer a date. Report what changed.

## Step 4: Report

End with one compact block:

```
## Follow-up pass - YYYY-MM-DD
gmail: <N changes applied | not connected>
follow-ups: <N drafted for: Company (Role), ...> | none due - next due YYYY-MM-DD (Company)
deadlines: <items from Step 3, most urgent first> | none
```

Blunt, no filler. If something needs the user today (a programme closing within 7 days, an interview invitation found in Gmail), put it first.
