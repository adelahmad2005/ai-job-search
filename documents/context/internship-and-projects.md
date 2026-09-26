# Dell Technologies internship, June to August 2026

**Intern, Product Services (Infrastructure Solutions Group), Dubai.**
Ten weeks, 50 working days.

## The thing that matters most

**Nothing was assigned to me.** There was no task list, no backlog, no ticket
queue. All 12 projects came from me identifying a specialist, reading about their
function, requesting a meeting, and asking at the end what I could build for them.
Twice I built something first and then found someone who wanted it.

That is the headline on my resume and the strongest thing I have. Lead with it.

## Final numbers

| | |
|---|---|
| Projects delivered | 12 in 10 weeks |
| Projects assigned to me | 0 |
| One-to-one specialist sessions | 60+ across 14 business functions |
| Senior audiences presented to | 4 department heads plus a full team |
| Deal lifecycle stages seen first hand | 8 of 8 |
| Weekly written reports to mentor | 10 |
| Public project write-ups on LinkedIn | 6 |

## The 12 projects

**1. Competitive Intelligence Agent.** Agentic RAG on n8n with OpenAI, a vector
store and Notion. Type a company name, get a cited displacement battlecard with a
four-tier confidence model that writes "insufficient data" rather than guessing.
Caught the agent claiming to use retrieval without calling the tool, by reading
execution logs. Deleted the most impressive component (inferring internal tech
from employee profiles) on accuracy and privacy grounds. Four versions, reached
sales leadership, taken forward for budget discussion.

**2. Dell Enterprise SONiC virtual switching lab.** GNS3 on VMware, nested
virtualization. Diagnosed a hypervisor path fault, a platform-security conflict
blocking virtualization, a cloud-sync corruption risk, and a wrong-artefact
problem where I'd downloaded the physical-switch installer instead of the
emulator appliance. Hit a hard 8 GB memory wall, documented it, escalated with
evidence rather than grinding, and completed the full curriculum on a hosted lab.

**3. Mid-point progress presentation.** Asked for the slot myself. 13 slides to my
mentor and the department head. Set four measurable targets there and reported
against all four at the end. Generated a further internal workstream.

**4. Intern programme, study and contribution.** Organised marketing, project
management and legal sessions for the other interns, in disciplines outside my own
interest. Sat on a SOC L1 hiring panel and ranked candidates. Studied ISM and
ISC2 CC alongside.

**5. Agent-to-agent communication and security.** 26 slides. Seven AI-specific
threat classes (prompt injection, agent impersonation, agent hijacking, data
poisoning, attack amplification, excessive access, privilege escalation) mapped to
a seven-layer zero-trust architecture: identity and trust with mTLS and OAuth
2.0/JWT, access control with RBAC then ABAC then least privilege, message
security, execution security with instruction isolation, human oversight with
maker-checker, WORM audit feeding SIEM and SOAR, and governance. Threw away a
finished 11-slide draft after critiquing my own structure.

**6. Enterprise AI Factory proposal and pitch.** 58 pages, customer-ready, for a
multinational banking scenario. **This one failed first.** The delivery went badly
because I had never said the material out loud. Wrote an honest retrospective the
same evening, rebuilt the document after review by four Dell specialists, built a
20-minute pitch from it, and re-pitched successfully two weeks later. The key note
that changed the document: lead with requirements and workload sizing, let the
hardware follow. Also caught my own accelerator-count error before presenting.

**7. AI operations suite** for a shipyard and manufacturing customer. 14 tools in
one Flask app, offline, on one laptop. Gradient-boosting predictive maintenance
ranking 118 assets over 45 days, validated on 11,196 post-cutoff readings so the
model never sees the future while learning. Workforce planning at 0.879 ROC AUC
with recall and precision stated in plain language above the number. Anomaly
detection where three rules and one model each report independently. An importer
that reads a German SAP-style export and works out the column meanings across six
languages. Outbound data boundary runs as an allowlist so a new column is excluded
by default. 74 automated tests, 195 cached answers, MIT licensed. Removed a rigged
demo cast and closed a scoring loophole after self-review.

**8. Home lab.** Self-directed, own time. Proxmox VE on single-disk ZFS, Docker,
Tailscale mesh with subnet routing, local LLMs. Debugged inference from 0.27 to 42
tokens/sec by finding that a container leaks the host CPU count so the runtime
sized 8 threads onto 4 cores. Then found a separate client-side fault injecting 15
tool schemas into every prompt, turning a two-letter message into 2,050 tokens.
173 seconds down to 3.1.

**9. Endpoint presentation series.** Same deck to four department heads and a full
team. Two full days of review and rehearsal before the first delivery, which was
the direct correction of the week-seven failure.

**10. Industry events.** Agentic AI Innovators Forum at Dtec, CyberE71, and a
Dubai digital authority session with Dell and Intel. Found and arranged myself.

**11. Production deployment.** n8n plus a FastAPI backend on a hardened VPS behind
Cloudflare: Nginx reverse proxy, Let's Encrypt TLS, systemd units, UFW
default-deny, key-only SSH. Three real incidents diagnosed with standard tooling.

**12. Playbook Builder.** Voice note to ready-to-run Excel batch for the Technical
Customer Success team. 3,908 lines of Python, 216 automated tests, **zero external
LLM calls** because the constraint prohibited them and a closed vocabulary of 11
values made a model unnecessary. Replaced roughly six hours of manual entry per
run. Refuses ambiguous input rather than padding it, after real dictation produced
a valid-looking account ID belonging to a different customer.

## Interview material

Best answers I have, use these:

- **Failure:** the week-seven presentation. Sound work, bad delivery, honest
  retrospective naming five root causes, corrections applied within one week,
  successful re-pitch within two. Most candidates cannot answer this question
  with a real arc.
- **Integrity:** deleting the profile-mining feature and the rigged demo cast when
  both made the work look better.
- **Judgement:** refusing to use a language model in the Playbook Builder because
  a closed vocabulary made one unnecessary.
- **Rigour:** catching my own accelerator-count error before presenting, and using
  a temporal holdout rather than a random split so the maintenance model couldn't
  leak the future.
- **Initiative:** all 12 projects self-sourced.

## Network

60+ people across 14 functions. Strongest routes:

- **Dell Technologies** — mentor in Product Services, Head of Services Presales,
  Head of Presales, Head of Deploy, UAE and Oman cybersecurity lead, a security
  and resilience consultant, an AI presales engineer, the TCSM AI adoption lead,
  and a senior AI consultant who advocated for me to a departmental lead unprompted.
- **Adjacent by association:** NVIDIA, Red Hat, VMware/Broadcom, IBM. My proposal
  work was built on their reference designs.

A referral through this network beats a cold application by a wide margin. When a
job comes up at any of these, flag it and offer to draft the ask.

The full internship report with a day-by-day journal is in this folder as
`Internship_Report_Adel_Ahmad_NGN397.pdf` if you need more detail on any project.
