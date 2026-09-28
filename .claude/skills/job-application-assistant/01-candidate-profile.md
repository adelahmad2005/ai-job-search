---
framework_version: 1.1.1
---

# Candidate Profile

<!-- Populated by /setup Path A on 2026-09-26 from documents/cv/ (two resumes: AI_Security, Services_Presales)
and documents/context/ (about-me.md, application-answers.md, internship-and-projects.md, outreach-log.md,
Internship_Report_Adel_Ahmad_NGN397.pdf). This file is the SINGLE SOURCE OF TRUTH for resume claims:
if a posting needs something not in here, it is a gap to report, never a sentence to invent. -->

## Identity
- **Name:** Adel Abdelmoaty (legal/academic records may show "Adel Ahmad", e.g. the NGN397 internship report)
- **Location:** Dubai, UAE
- **Phone:** +971 56 211 4556
- **Email:** adelahmad2005@gmail.com
- **LinkedIn:** https://linkedin.com/in/adel-abdelmoaty-25aa5424b
- **GitHub:** https://github.com/adelahmad2005
- **Website:** none. `by-adel.uk` was deliberately dropped on 2026-09-24. Do not add it back unless Adel says a portfolio is live there.
- **Status:** Final-year B.Sc. Computer Science student (Minor in Finance), graduating December 2026. Freelance AI Automation Engineer (The Bookkeeper UAE, ongoing). **Available full-time from January 2027**; part-time or project work possible before then.
- **Nationality:** Egyptian (confirmed by Adel 2026-09-26; answer when a form asks). Ethnicity questions: pick "Middle Eastern / North African" or "Arab" where offered.
- **Pronouns:** he/him (confirmed by Adel 2026-09-26). Gender on forms: Male.
- **Disability:** none, never had one (confirmed by Adel 2026-09-26; answer "No" when asked).
- **Work authorisation:** UAE resident. **No visa sponsorship required** (state this on applications, it is a real advantage in the UAE market).
- **Notice period:** none.
- **Constraints:** Based in Dubai. Willing to relocate within the UAE. Not seeking roles outside the UAE.

### Languages

| Language | Level | Notes |
|----------|-------|-------|
| Arabic | Native | |
| English | Fluent | All CVs, degree and professional work in English |

## Education

| Degree | Period | Institution | Key Topics |
|--------|--------|-------------|------------|
| B.Sc. Computer Science, Minor in Finance (**in progress, expected December 2026**) | 08/2022 - 12/2026 | American University of Sharjah, Sharjah, UAE | Network Security, Operating Systems, Databases, Distributed Systems, Computer Networks, Machine Learning, Financial Analysis |

- **GPA:** 2.79 / 4.0 (confirmed by Adel 2026-09-26). Do not put it on resumes. It is below the usual 3.0 / UK 2:1 cutoff, so flag any posting that states a GPA or degree-class minimum.
- **Senior Design Project (ongoing):** Assistive AI Perception & Navigation System. Real-time embedded system combining object detection, OCR and voice interaction for visually impaired users; edge-deployed models with privacy-aware data handling; secure SDLC with threat modelling and input sanitisation at each layer.
- **NGN397 internship course** (Dell placement), internship coordinator Dr. Almira Zholamanova. Full report with day-by-day journal: `documents/context/Internship_Report_Adel_Ahmad_NGN397.pdf`.

## Certifications
- **None held.** During the Dell internship he *studied* ISM and **ISC2 Certified in Cybersecurity (CC)** material; the exam is not recorded as passed. Never list ISC2 CC as a held certification. Can say "studying toward ISC2 CC" only if Adel confirms it is still in progress.
- Planned (from internship report): continue ISC2 certification, then an offensive-security certification and hands-on practice platforms.

## Professional Experience

### AI Automation Engineer (Freelance) - The Bookkeeper UAE (06/2026 - Present)
Dubai, UAE. Paid, ongoing.
- Built an end-to-end AI document pipeline (email intake, vision extraction, human review, posting to QuickBooks Online) on n8n, with direct REST and OAuth 2.0 integrations to the OpenAI, Google Drive, Google Sheets and QuickBooks APIs (four external APIs).
- Designed human-in-the-loop approval so no AI-extracted financial data posts without sign-off; prompt-engineered structured JSON extraction from PDFs and photographed receipts across multi-currency and tax-inclusive edge cases.
- Applied double-entry principles to route documents to the correct transaction type across multiple client entities.
- Fixed production failures including memory exhaustion on large mailbox scans and a per-item execution bug causing silent data loss.
- Scoped, priced and proposed the engagement himself to a non-technical client, milestone-based payment, benchmarked against agency rates; converted the proof of concept into a paid follow-on with expanded scope.

### Intern, Product Services (Infrastructure Solutions Group) - Dell Technologies (06/2026 - 08/2026)
Dubai, UAE. 10 weeks, 50 working days.
- **Nothing was assigned.** Delivered 12 projects (0 assigned), scoped directly with specialists through 60+ one-to-one sessions across 14 business functions. Twice built something first, then found someone who wanted it. (Context for interviews. **On resumes, never write "self-initiated"**: state it plainly as "Delivered 12 projects ... scoped directly with specialists through 60+ one-to-one sessions".)
- Wrote a weekly report to his mentor every Friday for 10 weeks; presented to four department heads plus a full team; observed all 8 stages of the enterprise deal lifecycle first hand; served on a SOC L1 hiring panel and ranked candidates; published 6 project write-ups on LinkedIn.
- Organised marketing, project management and legal learning sessions for the intern cohort (outside his own discipline, unasked).
- The 12 projects are detailed under "Dell Internship Projects" below.

### Automation & Data Systems Engineer (Freelance) - Gulf E-Gate (06/2023 - 12/2025)
Dubai, UAE. Ended.
- Designed and deployed Python automation for e-commerce warehouse operations; built data pipelines for inventory tracking, order reconciliation and financial reporting, with input validation, access controls and audit logging throughout.
- Automated accounting workflows with error handling and anomaly detection; translated operational and compliance requirements into technical solutions.
- Note: 2.5-year freelance span with two bullets of visible output. See `05-cv-templates.md` "Check tenure against visible output". Ask Adel for more detail before an application where this role matters.

## Dell Internship Projects (the 12)

1. **Competitive Intelligence Agent.** Agentic RAG on n8n with OpenAI, a vector store and Notion. Company name in, cited displacement battlecard out, with a four-tier confidence model that returns "insufficient data" rather than guessing. Diagnosed the agent claiming retrieval without calling the tool, from execution logs. Deleted the most impressive component (inferring a company's internal tech from employee profiles) on accuracy and privacy grounds. Four versions, presented to sales leadership, taken forward for budget discussion.
2. **Dell Enterprise SONiC virtual switching lab.** GNS3 on VMware, nested virtualization. Diagnosed a hypervisor path fault, a platform-security conflict blocking virtualization, a cloud-sync corruption risk and a wrong-artefact download. Hit a hard 8 GB memory wall, documented it, escalated with evidence, completed the full curriculum on a hosted lab.
3. **Mid-point progress presentation.** Asked for the slot himself. 13 slides to mentor and department head; set four measurable targets and reported against all four at the end. Generated a further internal workstream (Head of Technical Customer Success Management).
4. **Intern programme contribution.** Organised sessions for other interns; SOC L1 hiring panel; studied ISM and ISC2 CC.
5. **Agent-to-agent communication and security.** 26 slides. Seven AI-specific threat classes (prompt injection, agent impersonation, agent hijacking, data poisoning, attack amplification, excessive access, privilege escalation) mapped to a seven-layer zero-trust architecture: mTLS and OAuth 2.0/JWT identity, RBAC then ABAC then least privilege, message security, execution security with instruction isolation, human oversight with maker-checker, WORM audit feeding SIEM/SOAR, governance. Threw away a finished 11-slide draft after self-critique.
6. **Enterprise AI Factory proposal and pitch.** 58-page customer-ready proposal for a multinational banking scenario: requirements analysis, nine-layer architecture, services scopes with assumptions and exclusions, RACI and L1/L2/L3 support model, model-agnostic serving, 11-stage RAG query and 8-stage ingestion architecture, four-phase roadmap with measurable exit criteria. Reviewed layer by layer by four Dell specialists. 20-minute customer pitch built on top. **Failed first delivery (week 7)**, retrospective the same evening, rebuilt to lead with requirements and workload sizing rather than hardware, re-pitched successfully in week 9. Caught his own accelerator-count error before presenting.
7. **AI operations suite** for a shipyard / manufacturing customer (customer proof of concept). 14 tools in one Flask app, offline, on one laptop (Python, Flask, scikit-learn). Gradient-boosting predictive maintenance ranking 118 assets over 45 days, validated on 11,196 post-cutoff readings (temporal holdout, no leakage). Workforce planning / attrition model at 0.879 ROC AUC with recall and precision stated in plain language. Anomaly detection where three rules and one model report independently. Importer that reads a German SAP-style export and infers column meanings across six languages. Responsible-AI controls in code: one allowlist-gated function on every outbound request (new columns excluded by default), identity stripping before model calls, provenance stamping, deterministic scoring so no ranking is decided by a model. 74 automated tests, 195 cached answers, MIT licensed. Removed a rigged demo cast and closed a scoring loophole after self-review.
8. **Home lab** (own time). Proxmox VE on single-disk ZFS, Docker, Tailscale mesh with subnet routing, local LLMs. Debugged inference from 0.27 to 42 tokens/sec (container leaked host CPU count, runtime put 8 threads on 4 cores), then found a client-side fault injecting 15 tool schemas into every prompt (two-letter message became 2,050 tokens). 173 seconds down to 3.1.
9. **Endpoint presentation series** (= the end-of-internship presentation, NOT endpoint security; write "final internship presentation" on resumes). Same deck to four department heads and a full team. Two full days of review and rehearsal first, the direct correction of the week-7 failure.
10. **Industry events.** Agentic AI Innovators Forum at Dtec, CyberE71, a Dubai digital authority session with Dell and Intel. Found and arranged himself.
11. **Production deployment.** n8n plus a FastAPI backend on a hardened VPS behind Cloudflare: Nginx reverse proxy, Let's Encrypt TLS, systemd units, UFW default-deny, key-only SSH. Three real incidents diagnosed with standard tooling. (Set by an AI presales engineer.)
12. **Playbook Builder.** Voice note to ready-to-run Excel batch for the Technical Customer Success team. 3,908 lines of Python, 216 automated tests, **zero external LLM calls** (data-governance constraint prohibited them, and a closed vocabulary of 11 values made a model unnecessary). Replaced roughly six hours of manual entry per run. Refuses ambiguous input after real dictation produced a valid-looking account ID belonging to a different customer.

## Independent Projects
- **Assistive AI Perception & Navigation System** (Senior Design Project, ongoing): real-time embedded object detection + OCR + voice interaction for visually impaired users, edge-deployed, privacy-aware, secure SDLC.
- **Home lab** (see Dell project 8): Proxmox/ZFS, Docker, Tailscale, local LLM inference tuning. Ongoing; planned toward multi-node orchestration and a segmented security testing environment.
- **Public technical writing:** 6 project write-ups on LinkedIn during the internship.

## Technical Skills

### Programming & ML
- **Python** (strongest; production code, 3,908-line tool with 216 tests, 74-test Flask suite): Flask, FastAPI, pandas, NumPy, scikit-learn, pytest
- **Other languages** (coursework / lighter use): JavaScript/Node.js, Java, SQL, C/C++
- **AI/ML:** gradient boosting, model evaluation (ROC AUC, precision/recall, temporal validation), RAG, vector stores & embeddings, agentic workflows, prompt engineering, structured extraction from unstructured documents, multimodal/vision models, local LLM inference, responsible-AI design
- **Automation:** n8n (primary), REST/OAuth 2.0 integrations (QuickBooks Online, Google Workspace, OpenAI, Notion)

### Security
- Threat modelling, zero-trust architecture, mTLS, OAuth 2.0/JWT, RBAC/ABAC, least privilege, SIEM/SOAR, WORM audit logging, AI/agent security (prompt injection, agent impersonation, data poisoning, privilege escalation), secure SDLC
- Knowledge-level (coursework / study, not production ownership): MITRE ATT&CK, OWASP Top 10, incident response, SOC operations, GRC
- **No offensive-security / pentest experience yet.** No held certification.
- Took a penetration-testing course in summer 2025, taught by Zaid Taha (now Security Delivery Specialist, Accenture) (confirmed by Adel 2026-09-28). Course content, format and any certificate not recorded; ask before putting it on a resume.

### Infrastructure
- Linux, Docker, Proxmox VE, ZFS, Nginx, Let's Encrypt/TLS, systemd, UFW, Cloudflare, Tailscale, VPS hardening, GNS3, VMware, Dell Enterprise SONiC, Red Hat OpenShift AI (exposure), Git

### Solutions & Presales
- Technical proposal writing, SOW and services scoping, level-of-effort estimation, pricing and commercial benchmarking, RACI and L1/L2/L3 support models, phased roadmaps with exit criteria, customer pitching, requirements discovery, deal-lifecycle understanding (all 8 stages observed)

### Domain Expertise
- Enterprise AI infrastructure (AI Factory / reference designs from Dell, NVIDIA, Red Hat, VMware/Broadcom, IBM)
- AI and agent security
- Finance / accounting automation (Finance minor, double-entry, QuickBooks, reconciliation, financial reporting)
- Predictive maintenance / manufacturing analytics (one PoC)

### Software & Tools
- n8n, Notion, QuickBooks Online, Google Workspace, OpenAI API, Excel automation, Claude Code (about 1 year, confirmed by Adel 2026-09-26)
- **Application-form answers confirmed by Adel (2026-09-26):** years of engineering experience = "0 (graduating 2026)" (counts full-time only); GCP experience = none.

## Publications
- None (academic). 6 public LinkedIn project write-ups.

## Awards
- None recorded.

## References
Available on request. No referee has yet agreed to be named with contact details on a CV; ask Adel before listing anyone.
Strongest potential referees (Dell Technologies, all warm; see `documents/context/outreach-log.md`):
- **Mentor / company supervisor, Product Services, Dell**: 10 weeks, read his Friday update every week. Strongest reference.
- **Senior AI consultant, Dell**: reviewed his portfolio and advocated for him to a departmental lead unprompted.
- **Head of Technical Customer Success Management, Dell**: generated a workstream from his mid-point presentation.
- Head of Services Presales, Head of Presales, Head of Deploy, UAE & Oman cybersecurity lead, security and resilience consultant, AI presales engineer, TCSM AI adoption lead.

More references available upon request.

## Network (use for referrals)
Dell Technologies (60+ people across 14 functions). Adjacent by association: NVIDIA, Red Hat, VMware/Broadcom, IBM (his proposal built on their reference designs). **When a role appears at any of these, flag it and offer to draft a referral ask.** Check `documents/context/outreach-log.md` before suggesting a contact, so the same person is not approached twice.
