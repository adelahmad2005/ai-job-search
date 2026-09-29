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
| Cisco (cisco.com) | suvjain@cisco.com (Suvidha Jain, flast-style alias) | Her own LinkedIn headline |
