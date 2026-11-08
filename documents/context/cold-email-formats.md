# Company email formats (for cold outreach)

Evidence (2026-09-28): public email-format aggregators only (LeadIQ, RocketReach, Clay, email-format.com).
**Since 2026-09-29 aggregator shares are NOT enough to send:** a format needs >=2 real published example
addresses from the same company/domain/subsidiary (add them below with source URLs) before /coldemail may use it.
Share = how often the pattern appears in their samples. A guessed address is only as good as this share;
anything under ~80% is labelled "low confidence" in `cold-email-targets.csv`.

| Company | Domain | Primary pattern | Example | Share | Notes |
|---|---|---|---|---|---|
| OpenAI | openai.com | first | jane@openai.com | ~85% | sources disagree (one says flast); treat as medium |
| NVIDIA | nvidia.com | flast | jdoe@nvidia.com | ~94% | |
| Red Hat | redhat.com | flast | jdoe@redhat.com | ~80% | |
| Cisco | cisco.com | flast | jdoe@cisco.com | ~92% | |
| Palo Alto Networks | paloaltonetworks.com | flast | jdoe@paloaltonetworks.com | 75-97% | PANW warns candidates about recruiter impersonation from other domains |
| Fortinet | fortinet.com | flast | jdoe@fortinet.com | 79-90% | |
| CrowdStrike | crowdstrike.com | first.last | jane.doe@crowdstrike.com | ~94% | |
| CPX | cpx.net | first.last | jane.doe@cpx.net | 70-98% | |
| G42 (group) | g42.ai | first.last | jane.doe@g42.ai | 83-95% | subsidiaries may use their own domains |
| Help AG | helpag.com | first.last | jane.doe@helpag.com | ~100% | |

To add: Microsoft, IBM, Broadcom, AWS, Oracle, Deloitte, PwC, EY, KPMG, Core42, Presight, Inception.

## Proven failures (bounced, 550 5.4.1 recipient rejected, 2026-09-28)

| Address tried | Aggregator claim | Lesson |
|---|---|---|
| ammar.mohammad@g42.ai | first.last 83-95% | recipient does not exist; person is Core42-side |
| ammar.mohammad@core42.ai | first.last 95% | also rejected; real format for this person unknown |
| nancy.naweto@microsoft.com | first.last 53-92% | Microsoft aliases vary; never guess |
| zulul.huma@cpx.net | first.last 70-98% | rejected despite "98%"; needs real CPX examples |

Delivered without bounce (not proof of the format, only of these addresses): tabbashum.khan@g42.ai, john.canimo@g42.ai,
ekta.sharma@inceptionai.ai, stephan@openai.com, abhinav.noronha@helpag.com, salameh@cisco.com, ssuhaib@redhat.com, mmichel@nvidia.com.

## Real published examples (required before sending)

| Company / domain | Example address | Source URL |
|---|---|---|
| Cisco (cisco.com) | suvjain@cisco.com (Suvidha Jain = first 3 letters + last name, NOT flast: Cisco aliases vary per person, so only published Cisco addresses are safe) | Her own LinkedIn headline |
| G42 (g42.ai, G42 group staff only, not Core42/CPX) | ulviyya.hasanzade@g42.ai (Director of Corporate Communications) | G42 press release media contact (via Presight/G42 releases, 2025) |
| G42 (g42.ai) | tabbashum.khan@g42.ai, john.canimo@g42.ai | Delivered 2026-09-28 with no bounce; g42.ai's server rejects unknown recipients (550 5.4.1 on ammar.mohammad@g42.ai), so acceptance proves these mailboxes exist |
| Presight | media@presight.ai (role address only, no personal example yet) | Presight press releases |

**Status 2026-09-29:** first.last@g42.ai is PROVEN (3 examples) for people employed by G42 itself (headline says G42, not Core42/CPX/Inception). All other domains still need 2 real examples before any send.

## Formats proven 2026-10-19 (>=2 real published addresses, same domain)

| Company / domain | Format | Examples | Source |
|---|---|---|---|
| Deloitte Middle East (deloitte.com) | first initial + surname (flast) | ykayali@deloitte.com, ncheikh@deloitte.com | https://www.deloitte.com/middle-east/en/contact/press-contacts.html (fetched 2026-10-19) |
| Capgemini (capgemini.com) | first.last | victoire.grux@, sam.connatty@, antara.nandy@capgemini.com | Capgemini press releases (Q1 2025 revenue release; 2022-2024 releases) |
| Oracle (oracle.com) | first.last (duplicates may get a middle initial: only use rare names) | ken.bond@, deborah.hellinger@oracle.com | Oracle Q4 FY25 earnings release, 2025-06-11 (SEC copy on last10k.com) |
| HPE (hpe.com) | first.last | laura.keller@hpe.com, kari.curto@hpe.com | HPE earnings webcast releases on Business Wire (2025); Deloitte US press room |
| Trend Micro (trendmicro.com) | first_last | lisiane_lenz@, lena_clefberg@, lorena_rodriguez@, angela_chiang@ | trendmicro.com press-contacts pages. **On hold:** enterprise unit renamed TrendAI (2026-03-24), staff domain may have changed |

Not proven (1 example only, or conflicting): PwC (sarah.salman@pwc.com, 2017), Accenture (rachel.frey@accenture.com), Check Point (lizwu@ / emilieb@ / audreyp@ conflict), Red Hat (kcatallo@ truncated surname), CrowdStrike, Palo Alto, Fortinet, NVIDIA, CPX, Core42, Presight, EY, KPMG, IBM, Microsoft, Cisco.

## Clay (per-person work email, since 2026-10-22)

/coldemail Step 3 now starts with a Clay MCP Work Email lookup per person. Validation run 2026-10-22 (task mcp-task_0tnatq3wgU4weHG4yBM):

| Person | Clay result | Known truth |
|---|---|---|
| Abhinav Noronha (Help AG) | abhinav.noronha@helpag.com | delivered 2026-09-28 - match |
| John Canimo (G42) | john.canimo@g42.ai | delivered 2026-09-28 - match |
| Zulul Huma (CPX) | no email (error: missing input) | zulul.huma@cpx.net bounced - Clay would not have sent it |

### Clay run 2026-10-22 (live batch) - accuracy notes
Accepted (Clay result matches >=2 published/delivered same-domain examples):
- jineshr@checkpoint.com (first + last initial; matches emilieb@, audreyp@ from checkpoint.com press kit)
- abdullah.ashraf@helpag.com (first.last; matches delivered abhinav.noronha@)
- jserrao@deloitte.com (flast; matches ykayali@, ncheikh@, delivered ptaleng@)
- anis.chamkhi@hpe.com (first.last; matches laura.keller@, kari.curto@)
- bhaskar.verma@ingrammicro.com (first.last; matches lisa.zwick@, willa.mcmanmon@ in Ingram Micro Business Wire releases 2025/2026) -> Ingram Micro first.last now PROVEN
Rejected (Clay wrong or implausible): mhussain@kpmg.ca (KPMG Canada domain), ajose@deloittece.com (Deloitte Central Europe), cb@us.pwc.com, aisha@ibm.com (IBM uses flast, e.g. sgillot@ibm.com), sal@accenture.com (contradicts first.last), ranjit.patil@core42.ai (Core42 high-risk).
Lesson: Clay often returns a sibling-country domain or a junk alias for big multinationals; always check the domain is the UAE/ME entity and the pattern matches published examples.

### Clay run 2026-10-27 - accuracy notes
Accepted (Clay result matches the proven first.last pattern; all delivered, no bounce): waseem.qaffaf@pwc.com, ahmad.alzaben@accenture.com, irine.benoy@oracle.com, ramila.vempati@capgemini.com.
Rejected: rs@capgemini.com for Sivaji Retta (junk alias, contradicts first.last).
No email from Clay (contact found, enrichment empty): Raed Salha (Fortinet), Mowafak Shebib (Palo Alto), Yusuf Sheikh (AWS), Mourad Nakib and Serhat Dirik (Red Hat). Palo Alto people Karim Sheba and Muath Salman were not in Clay at all.
Lesson: Clay works well for consulting firms and Oracle/Capgemini, but so far not for security vendors, AWS or Red Hat. For those, prefer 1st-degree LinkedIn connections.
