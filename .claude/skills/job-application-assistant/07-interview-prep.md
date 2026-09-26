---
framework_version: 1.0.0
---

# Interview Preparation Guide

<!-- SETUP: STAR examples are personalized by running /setup based on your actual experience -->

## STAR Format

Structure answers as: **Situation** (context), **Task** (your responsibility), **Action** (what you did), **Result** (outcome).

Keep answers to 1-2 minutes. Be specific. End with what you learned or would do differently.

## Ready-Made STAR Examples

<!-- Populated by /setup Path A on 2026-09-26 from the NGN397 internship report and internship-and-projects.md.
All facts are documented there; the full day-by-day journal is in documents/context/Internship_Report_Adel_Ahmad_NGN397.pdf. -->

### 1. The failed bank pitch (failure, learning, resilience)
**S:** Week 7 at Dell. He had written a 58-page enterprise AI Factory proposal for a multinational banking scenario and delivered it as a presentation.
**T:** Present the proposal convincingly to Dell specialists.
**A:** The delivery went badly: slides built for depth not speech, no rehearsal, and he understood the material at recognition level, not explanation level. He wrote a retrospective the same evening naming five root causes and six corrective actions. One week later he rehearsed out loud with the corporate presentation coach before the security presentation. He rebuilt the proposal after review by four Dell specialists, re-led it with requirements and workload sizing instead of hardware, and cut 58 pages to a 20-minute pitch.
**R:** The security presentation a week later went well; the re-pitch in week 9 succeeded; the endpoint series then landed with four department heads and a full team. Lesson: rehearsal is a design tool, not a final check.
**Use for:** "Tell me about a failure", "a time you received tough feedback", "biggest weakness", "how do you handle setbacks". **Do not soften this.** The arc is the point.

### 2. Twelve projects, zero assigned (initiative, self-direction)
**S:** Dell internship, Infrastructure Solutions Group. No task list, no backlog, nothing assigned.
**T:** Find valuable work on his own.
**A:** For each function: read about it for an hour, booked a meeting, arrived with a specific proposal and asked what he could build. 60+ one-to-one sessions across 14 functions. Twice he built something first, then found a user.
**R:** 12 projects delivered in 10 weeks, 0 assigned. One reached sales leadership and budget discussion; one replaced about six hours of manual work per run; the mid-point presentation generated a new internal workstream; a senior AI consultant advocated for him unprompted.
**Use for:** "greatest strength", "tell me about a time you took initiative", "working with ambiguity", "why should we hire you".

### 3. Deleting the most impressive feature (integrity, judgement, responsible AI)
**S:** Competitive Intelligence Agent (agentic RAG on n8n, OpenAI, vector store, Notion) for Dell sales. One component inferred a target company's internal tech stack from employees' public profiles. It was the most impressive-looking part.
**T:** Make the tool trustworthy enough for sales to act on.
**A:** Removed the profile-mining component on accuracy and privacy grounds. Added a four-tier confidence model that returns "insufficient data" rather than guessing. Read execution logs and caught the agent claiming to use retrieval without calling the tool. In a separate project (AI operations suite) also removed a rigged demo cast and closed a scoring loophole after self-review.
**R:** Four versions, presented to sales leadership, taken forward for budget discussion.
**Use for:** "an ethical dilemma", "responsible AI", "how do you handle hallucination", "a time you pushed back", "quality vs speed".

### 4. Playbook Builder without an LLM (technical judgement)
**S:** Technical Customer Success team entered batches into Excel by hand, about six hours per run. A data-governance constraint prohibited external LLM calls.
**T:** Automate voice note to ready-to-run Excel batch.
**A:** Saw that a closed vocabulary of 11 values made a model unnecessary; built 3,908 lines of Python with 216 automated tests, zero external LLM calls. After real dictation produced a valid-looking account ID that belonged to a different customer, made it refuse ambiguous input rather than pad it.
**R:** Replaced roughly six hours of manual entry per run; met the governance constraint by design. He calls it the best technical decision he made all summer.
**Use for:** "when not to use AI", "working within constraints", "a technical decision you're proud of", "handling edge cases".

### 5. Predictive maintenance without leaking the future (rigour, ML)
**S:** AI operations suite PoC for a shipyard / manufacturing customer: 14 tools in one offline Flask app.
**T:** Rank 118 assets by failure risk credibly.
**A:** Gradient boosting validated on 11,196 post-cutoff readings (temporal holdout, not random split) so the model never saw the future. Workforce model at 0.879 ROC AUC with recall and precision explained in plain language above the number. Allowlist-gated outbound data (new columns excluded by default), identity stripping before model calls, deterministic scoring. 74 automated tests. Also caught his own accelerator-count error in the bank proposal before presenting.
**R:** A defensible, offline, MIT-licensed PoC. "A prediction without its error rate is a claim."
**Use for:** "attention to detail", "explain a model to a non-technical stakeholder", "data leakage", "data privacy by design".

### 6. Home lab: 173 seconds to 3.1 (debugging, infrastructure)
**S:** Own-time Proxmox VE / ZFS / Docker / Tailscale home lab running local LLMs; inference at 0.27 tokens/sec.
**T:** Make local inference usable.
**A:** Found the container leaked the host CPU count so the runtime put 8 threads on 4 cores; fixed it, reaching 42 tokens/sec. Then found a client-side fault injecting 15 tool schemas into every prompt, turning a two-letter message into 2,050 tokens.
**R:** Response time from 173 seconds to 3.1.
**Use for:** "hardest bug", "systematic troubleshooting", "tell me about a personal project", Linux / infra / DevOps questions.

### 7. Hitting the 8 GB wall (escalation with evidence)
**S:** Dell Enterprise SONiC virtual switching lab (GNS3 on VMware, nested virtualization) set by a senior systems engineer.
**T:** Complete the lab curriculum.
**A:** Fixed a hypervisor path fault, a platform-security conflict and a wrong-artefact download. Then hit an 8 GB memory ceiling. He admits he lost time tuning before seeing it was arithmetic. Documented the full build so it would transfer, escalated to the engineer with evidence, kept working on the unblocked parts.
**R:** Given a hosted lab; completed the full curriculum.
**Use for:** "a time you were blocked", "when to ask for help", "managing constraints".

### 8. Scoping and pricing a paid engagement (commercial, client-facing)
**S:** The Bookkeeper UAE, an accounting firm, with manual document handling and a non-technical owner.
**T:** Win and deliver an AI automation engagement.
**A:** Scoped, priced and proposed it himself (milestone-based payment, benchmarked against agency rates). Built an n8n pipeline (email intake, vision extraction, human review, QuickBooks Online posting) with OAuth 2.0 across four APIs; human-in-the-loop so no AI-extracted financial data posts without sign-off; fixed memory exhaustion and a silent data-loss bug in production.
**R:** Proof of concept converted into a paid follow-on with expanded scope; ongoing.
**Use for:** presales / consulting "tell me about working with a client", "requirements gathering", "commercial awareness", "delivering under real stakes".

## Common Tough Questions

### "Why did you leave [previous company]?"
> Dell was a fixed 10-week internship (June to August 2026), finished as planned; he returns to complete his degree in December. Gulf E-Gate freelance ended December 2025. The Bookkeeper UAE is ongoing freelance.

### "You don't have [specific skill/experience]."
> Name the gap plainly, then the closest real evidence and how fast he closed a comparable gap (e.g. from no enterprise infrastructure knowledge to a 58-page reviewed proposal in 10 weeks). Never bluff a certification or tool.

### "You're a fresh graduate. Why should we trust you with this?"
> Volume and completeness of shipped work: 12 projects in 10 weeks with tests and real users, plus a paid engagement he scoped and priced. Point to one project that matches the role.

### "Where do you see yourself in 5 years?"
> Deep technical first (AI and security), then services presales or consulting specialised in security, because moving from technical to commercial is straightforward and the reverse is very hard. Several senior people at Dell independently recommended that sequence.

### "What's your biggest weakness?"
> Live verbal delivery, evidenced by the week-7 pitch (STAR 1). Show the fix: rehearsal as design, 11 presentations delivered by the end, endpoint series landed.

### "Why this company specifically?"
> Customize per company. Must reference: specific projects, company values, market position, or team structure. Never give a generic answer.

### "Salary expectations?"
> Handle in conversation; do not state a number without Adel deciding one first. Reference: Dubai cybersecurity presales, 2 years' experience, published at AED 15,000-18,000/month.

## Questions You Should Ask Interviewers

### About the Role
- "What does a typical week look like in this role?"
- "What would success look like in the first 6 months?"
- "What's the biggest challenge the team is facing right now?"

### About the Team
- "How big is the team, and how do you divide work?"
- "What does the development/project lifecycle look like, from idea to production?"
- "How do you onboard new team members?"

### About Tech & Growth
- "What's your current tech stack for [relevant area]?"
- "Is there room to grow into more architectural or strategic decisions?"
- "How does the team stay current with new tools and methods?"

### About Culture (use these to prevent disappointment)
- "How would you describe the team culture?"
- "What does professional development look like here?"
- "Is there flexibility for remote/hybrid work?"
- "What's the balance between development/new projects and maintenance work?"
- "How would you describe the leadership style in this team?"
- "What do people who thrive here have in common?"

## Phone/Video Interview Tips
- Have STAR examples written out (use this file)
- Keep a glass of water nearby
- Smile when speaking (it changes your tone)
- Ask for clarification if a question is vague
- It's OK to take 5 seconds to think before answering
- End with: "Is there anything else you'd like to know about my background?"

## After the Application (Best Practice)

### Follow-Up Etiquette
- **Don't call to "stand out"** or to learn more about the role post-submission - this risks a negative impression
- If the employer specified a timeline, respect it and wait
- If no timeline was given and significant time has passed (2+ weeks), a brief call to ask about status is acceptable
- If you have genuinely new, relevant information to share, a short follow-up is fine

### Thank-You Notes
- When you receive any update (interview invitation, rejection, or status update), send a brief thank-you message
- Express appreciation for their time and the process
- Keep it short (2-3 sentences)

## Roleplay Guidelines
When the user asks for interview practice:
1. Ask which role/company to simulate
2. Start with easy warm-up questions ("Tell me about yourself")
3. Progress to role-specific technical questions
4. Include 1-2 behavioral questions using the competencies from the job posting
5. End with a tough question or curveball
6. After each answer, give brief feedback: what worked, what to sharpen
7. Suggest which STAR example would work best for each question
